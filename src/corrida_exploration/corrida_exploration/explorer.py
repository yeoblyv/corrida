"""
Explore the map on its own: drive to the nearest frontier until none is left.

For every new map from slam_toolbox the node sends the nearest frontier to Nav2 as a goal.
With drive:=false it only shows the goals.
"""

import math
import signal
import time

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import Point, PoseStamped, PoseWithCovarianceStamped
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import OccupancyGrid
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from rclpy.signals import SignalHandlerOptions
from visualization_msgs.msg import Marker

from corrida_exploration import frontiers

# m, an opening has to be wider than the robot (about 0.35 m) to count
MIN_FRONTIER_SIZE = 0.4
# m, how far from the robot the search may start if its cell isn't free
START_REACH = 0.15
# m, a frontier this close to a goal that was reached or given up is not chosen again
DONE_RADIUS = 0.3
# s, give up on a goal after this long, Nav2's own recoveries take a while
GOAL_TIMEOUT = 90.0

# how a Nav2 goal ended, for the log
RESULTS = {
    GoalStatus.STATUS_SUCCEEDED: "reached",
    GoalStatus.STATUS_ABORTED: "failed",
    GoalStatus.STATUS_CANCELED: "cancelled",
}


class Explorer(Node):
    """Pick frontiers in the slam map and send them to Nav2 one by one."""

    def __init__(self) -> None:
        super().__init__("explorer")
        self.declare_parameter("drive", False)
        self.drive = self.get_parameter("drive").value
        self.map = None
        self.robot = None  # (x, y) on the map
        self.origin = (0.0, 0.0)
        self.resolution = 0.05
        self.steps = {}
        self.found = []
        self.done_goals = []  # map points (x, y) that were reached or given up
        self.goal = None  # the goal Nav2 is driving to, None when there is none
        self.goal_handle = None  # Nav2's handle for that goal, to cancel it
        self.send_future = None
        self.sent_at = 0.0
        self.cancel_asked = False
        self.finished = False
        # same QoS as slam_toolbox's map (transient local), so its last map comes right away
        map_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        # "/map" with the slash, slam_toolbox publishes it outside the robot namespace
        self.create_subscription(OccupancyGrid, "/map", self.on_map, map_qos)
        # slam_toolbox publishes the robot's pose on the map, so this node doesn't need tf
        self.create_subscription(PoseWithCovarianceStamped, "pose", self.on_pose, 10)
        self.frontier_pub = self.create_publisher(Marker, "frontiers", 1)
        self.goal_pub = self.create_publisher(PoseStamped, "exploration_goal", 1)
        self.nav2 = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self.create_timer(1.0, self.check_timeout)

    def on_pose(self, pose_msg: PoseWithCovarianceStamped) -> None:
        self.robot = (pose_msg.pose.pose.position.x, pose_msg.pose.pose.position.y)

    def on_map(self, map_msg: OccupancyGrid) -> None:
        self.map = map_msg
        if not self.search():
            return
        if self.goal is None:
            self.start_next_goal()
        elif not self.still_a_frontier(self.goal):
            self.get_logger().info("frontier explored already, choosing a new one")
            self.cancel_goal()

    def start_next_goal(self) -> None:
        goal = self.choose_goal()
        if goal is None:
            self.get_logger().info("no frontiers left to explore", throttle_duration_sec=10.0)
            self.finished = self.drive
            return
        if not self.drive:
            return
        if not self.nav2.server_is_ready():
            self.get_logger().warn(
                "Nav2 isn't running, start nav2.launch.py", throttle_duration_sec=10.0
            )
            return

        # like the ROS 2 action client tutorial, link in send_goal_done()
        self.goal = goal
        self.goal_handle = None
        self.cancel_asked = False
        self.sent_at = time.monotonic()
        self.get_logger().info("sending the goal to Nav2")
        self.send_future = self.nav2.send_goal_async(NavigateToPose.Goal(pose=goal))
        self.send_future.add_done_callback(self.send_goal_done)

    def send_goal_done(self, future) -> None:
        # https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Writing-an-Action-Server-Client/Py.html
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn("Nav2 rejected the goal")
            self.goal_finished()
            return
        self.goal_handle = goal_handle
        goal_handle.get_result_async().add_done_callback(self.result_done)
        # a cancel may have come before Nav2 answered, do it now
        if self.cancel_asked:
            goal_handle.cancel_goal_async()

    def result_done(self, future) -> None:
        status = future.result().status
        self.get_logger().info(f"goal {RESULTS.get(status, f'ended with status {status}')}")
        self.goal_finished()

    def goal_finished(self) -> None:
        if self.goal is not None:
            self.done_goals.append(goal_point(self.goal))
        self.goal = None
        self.goal_handle = None

    def cancel_goal(self) -> None:
        """Ask Nav2 to cancel the goal, don't wait for the answer."""
        if self.goal is None or self.cancel_asked:
            return
        self.cancel_asked = True
        if self.goal_handle is not None:
            self.goal_handle.cancel_goal_async()
        # else send_goal_done() cancels it once Nav2 accepts

    def stop(self) -> None:
        """Cancel the current goal and wait until Nav2 has it, used when the node shuts down."""
        if self.goal is None:
            return
        # Nav2 may not have answered yet and would drive there later, so wait for the
        # answer and take the handle from it, send_goal_done() may not have run
        rclpy.spin_until_future_complete(self, self.send_future, timeout_sec=3.0)
        if not self.send_future.done():
            self.get_logger().error("Nav2 didn't answer, it may still drive: use the e_stop")
            return
        goal_handle = self.send_future.result()
        if goal_handle.accepted:
            cancel = goal_handle.cancel_goal_async()
            rclpy.spin_until_future_complete(self, cancel, timeout_sec=3.0)

    def check_timeout(self) -> None:
        if self.goal is not None and time.monotonic() - self.sent_at > GOAL_TIMEOUT:
            self.get_logger().warn(f"goal timed out after {GOAL_TIMEOUT:.0f} s, giving up")
            self.cancel_goal()

    def cells(self, metres: float) -> int:
        return round(metres / self.resolution)

    def search(self) -> bool:
        """Look for frontiers in the latest map, False while the robot's pose is unknown."""
        if self.robot is None:
            self.get_logger().warn("no pose from slam_toolbox yet")
            return False

        info = self.map.info
        # slam_toolbox doesn't rotate the map origin, so x and y are enough
        self.origin = (info.origin.position.x, info.origin.position.y)
        self.resolution = info.resolution
        grid = frontiers.to_rows(list(self.map.data), info.width)
        robot_cell = frontiers.world_to_cell(self.robot, self.origin, self.resolution)
        start = frontiers.nearest_free_cell(grid, robot_cell, self.cells(START_REACH))
        if start is None:
            self.get_logger().warn("robot is not on a free part of the map")
            return False

        self.steps = frontiers.reachable_cells(grid, start)
        self.found = frontiers.find_frontiers(grid, self.steps, self.cells(MIN_FRONTIER_SIZE))
        self.publish_frontiers()
        return True

    def choose_goal(self) -> PoseStamped | None:
        """Return the middle of the nearest frontier that wasn't reached or given up yet."""
        blocked = []
        for point in self.done_goals:
            blocked.append(frontiers.world_to_cell(point, self.origin, self.resolution))
        cell = frontiers.nearest_goal(self.found, self.steps, blocked, self.cells(DONE_RADIUS))
        if cell is None:
            return None

        goal = PoseStamped()
        goal.header.frame_id = self.map.header.frame_id
        goal.header.stamp = self.get_clock().now().to_msg()
        x, y = frontiers.cell_to_world(cell, self.origin, self.resolution)
        goal.pose.position.x = x
        goal.pose.position.y = y
        goal.pose.orientation.w = 1.0
        self.goal_pub.publish(goal)
        distance = self.steps[cell] * self.resolution
        self.get_logger().info(
            f"{len(self.found)} frontiers, nearest at ({x:.2f}, {y:.2f}), {distance:.1f} m to drive"
        )
        return goal

    def still_a_frontier(self, goal: PoseStamped) -> bool:
        goal_cell = frontiers.world_to_cell(goal_point(goal), self.origin, self.resolution)
        for cells in self.found:
            for cell in cells:
                if math.dist(cell, goal_cell) <= self.cells(DONE_RADIUS):
                    return True
        return False

    def publish_frontiers(self) -> None:
        """Publish the frontier cells as small squares for Foxglove's 3D panel."""
        marker = Marker()
        marker.header = self.map.header
        marker.ns = "frontiers"
        marker.type = Marker.CUBE_LIST
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.x = self.resolution
        marker.scale.y = self.resolution
        marker.scale.z = 0.01
        marker.color.b = 1.0
        marker.color.a = 1.0
        for cells in self.found:
            for cell in cells:
                x, y = frontiers.cell_to_world(cell, self.origin, self.resolution)
                marker.points.append(Point(x=x, y=y))
        self.frontier_pub.publish(marker)


def goal_point(goal: PoseStamped) -> tuple[float, float]:
    return goal.pose.position.x, goal.pose.position.y


def main() -> None:
    # Nav2 keeps driving when this node just dies, so Ctrl+C and SIGTERM must reach the
    # except below while rclpy still works, rclpy's own handler would shut it down first
    signal.signal(signal.SIGINT, signal.default_int_handler)
    signal.signal(signal.SIGTERM, signal.default_int_handler)
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    explorer = Explorer()
    try:
        while not explorer.finished:
            rclpy.spin_once(explorer, timeout_sec=0.5)
    except KeyboardInterrupt:
        # ros2 launch passes Ctrl+C on and then sends SIGTERM, that must not break off the cancel
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        explorer.stop()
    explorer.destroy_node()
    rclpy.try_shutdown()


if __name__ == "__main__":
    main()
