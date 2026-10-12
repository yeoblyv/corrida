"""
Explore the maze on its own, or explore it on the way to a finish point.

For every new map from slam_toolbox the best frontier goes to Nav2 as a goal, with a finish
the finish itself as soon as the map shows a free way to it. With drive:=false nothing moves
and the goals are only shown.
"""

import math
import signal
import time

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import Point, PoseStamped, PoseWithCovarianceStamped
from irobot_create_msgs.action import RotateAngle, Undock
from irobot_create_msgs.msg import DockStatus, HazardDetection, HazardDetectionVector
from irobot_create_msgs.srv import ResetPose
from nav2_msgs.action import NavigateToPose
from nav2_msgs.srv import ClearEntireCostmap
from nav_msgs.msg import OccupancyGrid, Odometry
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy, qos_profile_sensor_data
from rclpy.signals import SignalHandlerOptions
from sensor_msgs.msg import BatteryState, LaserScan
from slam_toolbox.srv import Reset
from visualization_msgs.msg import Marker

from corrida_exploration import frontiers, walls

# m, an opening has to be wider than the robot (about 0.35 m) to count
MIN_FRONTIER_SIZE = 0.4
# m, a goal closer than this to a wall is skipped, on the first run the robot got stuck
# after a goal 0.24 m from a wall
MIN_GOAL_CLEARANCE = 0.25
# m, further from a wall than this counts as free enough
CLEARANCE_LIMIT = 0.4
# m, how far from the robot the search may start if its cell isn't free
START_REACH = 0.15
# m, a frontier this close to a goal that was reached or given up is not chosen again
DONE_RADIUS = 0.3
# m, the finish counts as reached this close
FINISH_RADIUS = 0.3
# s, give up on a goal after this long, Nav2's own recoveries take a while
GOAL_TIMEOUT = 90.0
# rad/s, for turning parallel to the walls (the Create 3 action defaults to 1.9)
TURN_SPEED = 0.3
# turning stops when the walls are this close to straight, or after this many turns.
# rotate_angle overshoots a few percent, so a big turn needs a second small one
ALIGN_TOLERANCE = math.radians(1.0)
ALIGN_TURNS = 3
# below this the walls are not clear enough to turn to (see walls.wall_angle)
MIN_WALL_SURE = 0.6
# stop when the battery is this low, the robot switches itself off at 2 %
MIN_BATTERY = 0.2
# stop after this many bumps, then something is wrong
MAX_BUMPS = 3

# how a Nav2 goal ended, for the log
RESULTS = {
    GoalStatus.STATUS_SUCCEEDED: "reached",
    GoalStatus.STATUS_ABORTED: "failed",
    GoalStatus.STATUS_CANCELED: "cancelled",
}


class Explorer(Node):
    """Get the robot ready, then pick frontiers in the slam map and send them to Nav2."""

    def __init__(self) -> None:
        super().__init__("explorer")
        self.drive = self.declare_parameter("drive", False).value
        self.align = self.declare_parameter("align", True).value
        self.finish_distance = self.declare_parameter("finish_distance", 0.0).value
        self.finish_angle = math.radians(self.declare_parameter("finish_angle", 0.0).value)
        self.max_seconds = 60.0 * self.declare_parameter("max_minutes", 10.0).value

        self.ready = False  # True once the start is done
        self.finished = False
        self.started_at = time.monotonic()
        self.map = None
        self.grid = []
        self.robot = None  # (x, y) on the map
        self.odom = None  # (x, y, yaw) from the robot's odometry
        self.dock = None
        self.battery = None
        self.bumps = 0
        self.bumped = False
        self.scans = []
        self.finish = None  # (x, y) on the map
        self.origin = (0.0, 0.0)
        self.resolution = 0.05
        self.steps = {}
        self.found = []
        self.done_goals = []  # map points (x, y) that were reached or given up
        self.goal = None  # the goal Nav2 is driving to, None when there is none
        self.goal_is_finish = False
        self.shown = None  # (x, y) of the last goal that was logged
        self.goal_handle = None  # Nav2's handle for that goal, to cancel it
        self.send_future = None
        self.sent_at = 0.0
        self.cancel_asked = False
        self.robot_action = None  # handle of a running undock or turn, to cancel it

        # same QoS as slam_toolbox's map (transient local), so its last map comes right away
        latched = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        # "/map" with the slash, slam_toolbox publishes it outside the robot namespace
        self.create_subscription(OccupancyGrid, "/map", self.on_map, latched)
        # slam_toolbox publishes the robot's pose on the map, so this node doesn't need tf
        self.create_subscription(PoseWithCovarianceStamped, "pose", self.on_pose, 10)
        # the Create 3 publishes its sensors as best effort, so subscribe the same way,
        # scans and odometry are only needed in get_ready() and start there
        sensors = qos_profile_sensor_data
        self.create_subscription(DockStatus, "dock_status", self.on_dock, sensors)
        self.create_subscription(BatteryState, "battery_state", self.on_battery, sensors)
        self.create_subscription(HazardDetectionVector, "hazard_detection", self.on_hazard, sensors)
        self.frontier_pub = self.create_publisher(Marker, "frontiers", 1)
        self.goal_pub = self.create_publisher(PoseStamped, "exploration_goal", 1)
        self.finish_pub = self.create_publisher(PoseStamped, "finish", latched)
        self.nav2 = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self.undock_client = ActionClient(self, Undock, "undock")
        self.rotate_client = ActionClient(self, RotateAngle, "rotate_angle")
        self.reset_pose_client = self.create_client(ResetPose, "reset_pose")
        self.reset_slam_client = self.create_client(Reset, "slam_toolbox/reset")
        self.clear_clients = [
            self.create_client(ClearEntireCostmap, "local_costmap/clear_entirely_local_costmap"),
            self.create_client(ClearEntireCostmap, "global_costmap/clear_entirely_global_costmap"),
        ]
        self.create_timer(1.0, self.check_limits)

    def on_pose(self, pose_msg: PoseWithCovarianceStamped) -> None:
        self.robot = (pose_msg.pose.pose.position.x, pose_msg.pose.pose.position.y)
        if self.ready and self.finish is not None and not self.finished:
            distance = math.dist(self.robot, self.finish)
            if distance <= FINISH_RADIUS:
                self.finish_reached(f"the robot is {distance:.2f} m from it")

    def on_scan(self, scan: LaserScan) -> None:
        self.scans.append(scan)
        del self.scans[:-8]

    def on_odom(self, odom: Odometry) -> None:
        position = odom.pose.pose.position
        self.odom = (position.x, position.y, yaw_of(odom.pose.pose.orientation))

    def on_dock(self, dock: DockStatus) -> None:
        self.dock = dock

    def on_battery(self, battery: BatteryState) -> None:
        self.battery = battery.percentage

    def on_hazard(self, hazards: HazardDetectionVector) -> None:
        # the robot only sends this when something changes, count each new bump once
        bumped = any(h.type == HazardDetection.BUMP for h in hazards.detections)
        if bumped and not self.bumped:
            self.bumps += 1
        self.bumped = bumped

    def on_map(self, map_msg: OccupancyGrid) -> None:
        self.map = map_msg
        if not self.ready or self.finished or not self.search():
            return
        if self.goal is None:
            self.start_next_goal()
        elif not self.goal_is_finish and not self.still_a_frontier(self.goal):
            self.get_logger().info("frontier explored already, choosing a new one")
            self.cancel_goal()

    def check_limits(self) -> None:
        """Stop on a low battery, too many bumps or the time limit, and give up stuck goals."""
        if self.finished:
            return
        if self.battery is not None and self.battery < MIN_BATTERY:
            self.get_logger().warn(f"battery at {self.battery * 100:.0f} %, stopping")
            self.finished = True
        elif self.bumps >= MAX_BUMPS:
            self.get_logger().warn(f"{self.bumps} bumps, stopping")
            self.finished = True
        elif time.monotonic() - self.started_at > self.max_seconds:
            self.get_logger().warn("time limit reached, stopping")
            self.finished = True
        elif self.goal is not None and time.monotonic() - self.sent_at > GOAL_TIMEOUT:
            self.get_logger().warn(f"goal timed out after {GOAL_TIMEOUT:.0f} s, giving up")
            self.cancel_goal()

    def get_ready(self) -> None:
        """Leave the dock, turn parallel to the walls and start the odometry and map from here."""
        # every message costs CPU in Python, so scans and odometry are only listened to here
        sensors = qos_profile_sensor_data
        subscriptions = [
            self.create_subscription(LaserScan, "scan", self.on_scan, sensors),
            self.create_subscription(Odometry, "odom", self.on_odom, sensors),
        ]
        # the robot sends its battery state every 5 s
        self.wait_for(
            lambda: self.scans and self.odom and self.dock and self.battery is not None,
            "scan, odometry, dock status and battery state",
        )
        # check the battery before anything moves
        self.check_limits()
        # the finish is measured from this pose
        start = self.odom
        if self.dock.is_docked and not self.finished:
            self.get_logger().info("leaving the dock")
            self.run_action(self.undock_client, Undock.Goal())
        if self.align:
            self.turn_to_walls()
        # check_limits() may have stopped everything while the robot moved
        if self.finished:
            return
        before_reset = self.odom
        self.restart_map()
        if self.finish_distance > 0.0:
            # the finish in odometry, seen from the start pose
            fx = start[0] + self.finish_distance * math.cos(start[2] + self.finish_angle)
            fy = start[1] + self.finish_distance * math.sin(start[2] + self.finish_angle)
            # the new map starts at the pose just before the reset, put the finish in that frame
            dx, dy = fx - before_reset[0], fy - before_reset[1]
            c, s = math.cos(-before_reset[2]), math.sin(-before_reset[2])
            self.set_finish((c * dx - s * dy, s * dx + c * dy))
        for subscription in subscriptions:
            self.destroy_subscription(subscription)
        self.ready = True
        self.get_logger().info("ready, exploring")

    def turn_to_walls(self) -> None:
        for _ in range(ALIGN_TURNS):
            if self.finished:
                return
            angle, sure = self.measure_walls()
            if sure < MIN_WALL_SURE:
                self.get_logger().warn("no clear walls around, not turning")
                return
            if abs(angle) <= ALIGN_TOLERANCE:
                break
            # a wall `angle` to the left lines up after a left turn by `angle` (checked on
            # the robot, the other sign doubles the error)
            self.get_logger().info(f"turning {math.degrees(angle):.1f} deg to line up with walls")
            goal = RotateAngle.Goal(angle=angle, max_rotation_speed=TURN_SPEED)
            self.run_action(self.rotate_client, goal)
        angle, _ = self.measure_walls()
        self.get_logger().info(f"walls at {math.degrees(angle):.1f} deg after turning")

    def measure_walls(self) -> tuple[float, float]:
        """Return the wall angle (rad) and how sure it is, from the median of 8 new scans."""
        self.scans = []
        self.wait_for(lambda: len(self.scans) >= 8, "8 lidar scans")
        results = []
        for scan in self.scans:
            points = walls.scan_points(list(scan.ranges), scan.angle_min, scan.angle_increment, 4.0)
            results.append(walls.wall_angle(points))
        # the lidar is mounted backwards (yaw pi), that doesn't change an angle modulo 90 deg
        angles = sorted(angle for angle, _ in results)
        return angles[len(angles) // 2], min(sure for _, sure in results)

    def restart_map(self) -> None:
        """Start the odometry and the slam map at the robot's pose, then clear Nav2's costmaps."""
        # the Create 3 zeroes its odometry (it ignores the pose in the request), and
        # slam_toolbox starts a new map in the odometry's axes
        self.call(self.reset_pose_client, ResetPose.Request())
        self.wait_for(lambda: abs(self.odom[0]) + abs(self.odom[1]) < 0.01, "odometry reset")
        self.call(self.reset_slam_client, Reset.Request())
        for client in self.clear_clients:
            self.call(client, ClearEntireCostmap.Request())

    def set_finish(self, point: tuple[float, float]) -> None:
        self.finish = point
        finish = PoseStamped()
        finish.header.frame_id = "map"
        finish.header.stamp = self.get_clock().now().to_msg()
        finish.pose.position.x, finish.pose.position.y = point
        finish.pose.orientation.w = 1.0
        self.finish_pub.publish(finish)
        self.get_logger().info(f"finish at ({point[0]:.2f}, {point[1]:.2f}) on the map")

    def wait_for(self, condition, what: str, timeout: float = 15.0) -> None:
        end = time.monotonic() + timeout
        while not condition():
            if time.monotonic() > end:
                raise RuntimeError(f"no {what} after {timeout:.0f} s")
            rclpy.spin_once(self, timeout_sec=0.1)

    def call(self, client, request):
        if not client.wait_for_service(timeout_sec=5.0):
            raise RuntimeError(f"service {client.srv_name} isn't there")
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=10.0)
        if not future.done():
            raise RuntimeError(f"service {client.srv_name} didn't answer")
        return future.result()

    def run_action(self, client: ActionClient, goal) -> None:
        """Run one of the robot's own actions (undock, rotate) and wait until it's done."""
        if not client.wait_for_server(timeout_sec=10.0):
            raise RuntimeError("the robot's action server isn't there")
        send = client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, send, timeout_sec=10.0)
        if not send.done() or not send.result().accepted:
            raise RuntimeError("the robot didn't accept the action")
        self.robot_action = send.result()
        result = self.robot_action.get_result_async()
        rclpy.spin_until_future_complete(self, result, timeout_sec=60.0)
        self.robot_action = None
        if not result.done() or result.result().status != GoalStatus.STATUS_SUCCEEDED:
            raise RuntimeError("the robot's action didn't finish")

    def search(self) -> bool:
        """Look for frontiers in the latest map, False while the robot's pose is unknown."""
        if self.robot is None:
            self.get_logger().warn("no pose from slam_toolbox yet")
            return False

        info = self.map.info
        # slam_toolbox doesn't rotate the map origin, so x and y are enough
        self.origin = (info.origin.position.x, info.origin.position.y)
        self.resolution = info.resolution
        self.grid = frontiers.to_rows(list(self.map.data), info.width)
        robot_cell = frontiers.world_to_cell(self.robot, self.origin, self.resolution)
        start = frontiers.nearest_free_cell(self.grid, robot_cell, self.cells(START_REACH))
        if start is None:
            self.get_logger().warn("robot is not on a free part of the map")
            return False

        self.steps = frontiers.reachable_cells(self.grid, start)
        self.found = frontiers.find_frontiers(self.grid, self.steps, self.cells(MIN_FRONTIER_SIZE))
        self.publish_frontiers()
        return True

    def start_next_goal(self) -> None:
        cell = self.choose_goal_cell()
        if cell is None:
            # when driving this is the end, without driving it comes back with every new map,
            # so it's logged once
            if self.finish is None:
                self.get_logger().info("no frontiers left to explore", once=True)
            else:
                self.get_logger().warn("no frontiers left and the finish wasn't reached", once=True)
            self.finished = self.drive
            return

        x, y = frontiers.cell_to_world(cell, self.origin, self.resolution)
        # without driving the same goal comes back with every new map, show it once
        if not self.drive and self.shown and math.dist((x, y), self.shown) < self.resolution:
            return
        self.shown = (x, y)
        goal = PoseStamped()
        goal.header.frame_id = self.map.header.frame_id
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.pose.position.x = x
        goal.pose.position.y = y
        goal.pose.orientation.w = 1.0
        self.goal_pub.publish(goal)
        what = "the finish" if self.goal_is_finish else f"best of {len(self.found)} frontiers"
        distance = self.steps[cell] * self.resolution
        self.get_logger().info(f"goal: {what} at ({x:.2f}, {y:.2f}), {distance:.1f} m to drive")
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
        self.send_future = self.nav2.send_goal_async(NavigateToPose.Goal(pose=goal))
        self.send_future.add_done_callback(self.send_goal_done)

    def choose_goal_cell(self) -> frontiers.Cell | None:
        """Return the finish if there is a known free way to it, else the best frontier cell."""
        limit = self.cells(CLEARANCE_LIMIT)
        clear = frontiers.clearance(self.grid, limit)
        min_clear = self.cells(MIN_GOAL_CLEARANCE)
        blocked = []
        for point in self.done_goals:
            blocked.append(frontiers.world_to_cell(point, self.origin, self.resolution))
        radius = self.cells(DONE_RADIUS)
        finish = None
        self.goal_is_finish = False
        if self.finish is not None:
            finish = frontiers.world_to_cell(self.finish, self.origin, self.resolution)
            # the finish counts as reached within FINISH_RADIUS, so one at a wall can be reached
            # from the nearest cell with enough room (seen on the robot)
            near = frontiers.cells_within(list(self.steps), finish, self.cells(FINISH_RADIUS))
            usable = frontiers.usable_cells(near, clear, limit, min_clear, blocked, 0)
            if usable:
                self.goal_is_finish = True
                return usable[0]

        goals = []
        for cells in self.found:
            # cells at a wall or near an old goal are left out, the rest can still be a goal
            usable = frontiers.usable_cells(cells, clear, limit, min_clear, blocked, radius)
            if not usable:
                continue
            if finish is None:
                goals.append(frontiers.goal_cell(usable, clear, limit))
            else:
                # on a long frontier, the end that is on the way to the finish
                goals.append(frontiers.best_goal(usable, self.steps, finish))
        return frontiers.best_goal(goals, self.steps, finish)

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
        # Nav2 stops up to 0.25 m from a goal (xy_goal_tolerance), and a goal for a finish
        # at a wall is up to FINISH_RADIUS from it, so the check in on_pose() can miss it
        if status == GoalStatus.STATUS_SUCCEEDED and self.goal_is_finish and not self.finished:
            # the pose from slam_toolbox comes only twice a second, so no distance here
            self.finish_reached("Nav2 got to the goal there")
        self.goal_finished()

    def finish_reached(self, how: str) -> None:
        self.get_logger().info(f"finish reached, {how}")
        self.finished = True

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
        """Cancel whatever moves the robot and wait for it, used at the end."""
        if self.robot_action is not None:
            cancel = self.robot_action.cancel_goal_async()
            rclpy.spin_until_future_complete(self, cancel, timeout_sec=3.0)
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

    def cells(self, metres: float) -> int:
        return round(metres / self.resolution)

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


def yaw_of(q) -> float:
    """Return the yaw (rad) of a quaternion, the robot only turns about z."""
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def main() -> None:
    # Nav2 keeps driving when this node just dies, so Ctrl+C and SIGTERM must reach the
    # except below while rclpy still works, rclpy's own handler would shut it down first
    signal.signal(signal.SIGINT, signal.default_int_handler)
    signal.signal(signal.SIGTERM, signal.default_int_handler)
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    explorer = Explorer()
    try:
        if explorer.drive:
            explorer.get_ready()
        else:
            explorer.ready = True
        while not explorer.finished:
            rclpy.spin_once(explorer, timeout_sec=0.5)
    except KeyboardInterrupt:
        explorer.get_logger().info("stopped with Ctrl+C")
    except RuntimeError as error:
        explorer.get_logger().error(f"couldn't get ready: {error}")
    # ros2 launch passes Ctrl+C on and then sends SIGTERM, that must not break off the cancel
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    explorer.stop()
    explorer.destroy_node()
    rclpy.try_shutdown()


if __name__ == "__main__":
    main()
