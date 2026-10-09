"""
Explore the map on its own: drive to the nearest frontier until none is left.

For every new map from slam_toolbox the node sends the nearest frontier to Nav2 as a goal.
With drive:=false it only shows the goals.
"""

import math
import signal
import time

import rclpy
from geometry_msgs.msg import Point, PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
from nav_msgs.msg import OccupancyGrid
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from rclpy.signals import SignalHandlerOptions
from rclpy.time import Time
from tf2_ros import Buffer, TransformException, TransformListener
from visualization_msgs.msg import Marker

from corrida_exploration import frontiers

ROBOT_FRAME = "base_link"
# m, an opening has to be wider than the robot (about 0.35 m) to count
MIN_FRONTIER_SIZE = 0.4
# m, how far from the robot the search may start if its cell isn't free
START_REACH = 0.15
# m, a frontier this close to a goal that was reached or given up is not chosen again
DONE_RADIUS = 0.3
# s, give up on a goal after this long, Nav2's own recoveries take a while
GOAL_TIMEOUT = 90.0


class Explorer(BasicNavigator):
    """Pick frontiers and drive to them. BasicNavigator does the talking to Nav2."""

    def __init__(self) -> None:
        super().__init__(node_name="explorer")
        self.declare_parameter("drive", False)
        self.drive = self.get_parameter("drive").value
        self.map = None
        self.new_map = False
        self.origin = (0.0, 0.0)
        self.resolution = 0.05
        self.steps = {}
        self.found = []
        self.done_goals = []  # map points (x, y) that were reached or given up
        # same QoS as slam_toolbox's map (transient local), so its last map comes right away
        map_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        # "/map" with the slash, slam_toolbox publishes it outside the robot namespace
        self.create_subscription(OccupancyGrid, "/map", self.on_map, map_qos)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.frontier_pub = self.create_publisher(Marker, "frontiers", 1)
        self.goal_pub = self.create_publisher(PoseStamped, "exploration_goal", 1)

    def on_map(self, map_msg: OccupancyGrid) -> None:
        self.map = map_msg
        self.new_map = True

    def cells(self, metres: float) -> int:
        return round(metres / self.resolution)

    def search(self) -> bool:
        """Look for frontiers in the latest map, False while the robot's pose is unknown."""
        self.new_map = False
        try:
            # Time() asks for the newest transform there is
            robot = self.tf_buffer.lookup_transform(self.map.header.frame_id, ROBOT_FRAME, Time())
        except TransformException as error:
            self.get_logger().warn(f"no robot pose from tf yet: {error}")
            return False

        info = self.map.info
        # slam_toolbox doesn't rotate the map origin, so x and y are enough
        self.origin = (info.origin.position.x, info.origin.position.y)
        self.resolution = info.resolution
        grid = frontiers.to_rows(list(self.map.data), info.width)
        position = (robot.transform.translation.x, robot.transform.translation.y)
        robot_cell = frontiers.world_to_cell(position, self.origin, self.resolution)
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
    stop_requests = []
    # Nav2 keeps driving to its last goal when this node just dies, so Ctrl+C only
    # asks the loop below to stop, and the loop cancels the goal first
    signal.signal(signal.SIGINT, lambda *args: stop_requests.append(True))
    signal.signal(signal.SIGTERM, lambda *args: stop_requests.append(True))
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    explorer = Explorer()
    log = explorer.get_logger()
    goal = None
    sent_at = 0.0

    while not stop_requests:
        # handles the map and tf messages, also while a goal is running
        rclpy.spin_once(explorer, timeout_sec=0.1)
        if explorer.new_map and explorer.search():
            if goal is None:
                goal = explorer.choose_goal()
                if goal is None:
                    log.info("no frontiers left to explore", throttle_duration_sec=10.0)
                    if explorer.drive:
                        break
                elif not explorer.drive:
                    goal = None
                elif not explorer.nav_to_pose_client.server_is_ready():
                    log.warn("Nav2 isn't running, start nav2.launch.py", throttle_duration_sec=5.0)
                    goal = None
                elif explorer.goToPose(goal):
                    sent_at = time.monotonic()
                else:
                    explorer.done_goals.append(goal_point(goal))
                    goal = None
            elif not explorer.still_a_frontier(goal):
                log.info("frontier explored already, choosing a new one")
                explorer.cancelTask()
                goal = None
        if goal is None or not explorer.drive:
            continue

        if explorer.isTaskComplete():
            log.info(f"goal {explorer.getResult().name.lower()}")
            explorer.done_goals.append(goal_point(goal))
            goal = None
        elif time.monotonic() - sent_at > GOAL_TIMEOUT:
            log.warn(f"goal timed out after {GOAL_TIMEOUT:.0f} s, giving up")
            explorer.cancelTask()
            explorer.done_goals.append(goal_point(goal))
            goal = None

    if goal is not None:
        explorer.cancelTask()
    explorer.destroy_node()
    rclpy.try_shutdown()


if __name__ == "__main__":
    main()
