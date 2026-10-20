"""WallFollower + automatic loop recovery + an optional LiDAR front check.

Same wall-following state machine as wall_follower.py -- this only adds two
things on top, and both are ADDITIVE: if their sensor never provides data,
this node drives exactly like plain WallFollower.

1. Loop recovery (loop_guard.py): watches the robot's odometry position.
   If it keeps coming back to the same spot -- the classic failure mode of a
   pure left-hand (or right-hand) rule on a maze with loops, see
   robot_modules/README.md's "Demo tip" -- it automatically swaps which wall
   it is following, instead of needing someone to stop it and restart it
   with the other side by hand.

2. LiDAR front check (lidar_utils.py): in addition to the IR front sensors
   (effective range roughly 20-30 cm), also checks /scan for anything close
   ahead. LiDAR sees much further than the IR sensors, so this can catch an
   oncoming wall earlier, especially at higher speed. It only ever makes the
   front-blocked check trigger EARLIER or the same as IR alone, never later.

3. Goal arrival (goal_tracker.py), OPTIONAL: if you tell the node where the
   finish mark is (measured by hand, see set_goal() and INTEGRATION_NOTES.md
   for the coordinate convention), it watches odometry and stops the robot
   as soon as it gets within GOAL_ARRIVAL_RADIUS_M of that point, lighting
   up a distinct colour so it's obvious on camera that it recognised the
   finish itself rather than just being picked up. If you never call
   set_goal(), this feature is simply off -- decide() falls straight through
   to the loop-recovery/plain-WallFollower logic exactly as before.

ASSUMPTIONS TO VERIFY ON THE ROBOT -- none of this has been run against the
real hardware or a simulator, only unit-tested as plain Python:
  - Odometry topic is ROBOT + '/odom', type nav_msgs/msg/Odometry.
    Check with: ros2 topic info /robot_10/odom
  - LiDAR topic is LIDAR_TOPIC below (default: ROBOT + '/scan'). This repo's
    corrida_bringup launch file is not used here on purpose (see the note in
    the PR/commit message) -- if you start the LiDAR driver yourself, e.g.:
      ros2 run rplidar_ros rplidar_node --ros-args -p frame_id:=laser
    the topic may come up as plain /scan instead of /robot_10/scan. Check
    with `ros2 topic list` and fix LIDAR_TOPIC below if needed.
  - If either topic never publishes anything, the corresponding feature
    just never activates -- this was a deliberate design choice so a LiDAR
    or odom problem can't make this behave worse than plain WallFollower.

Calibrate LOOP_* and LIDAR_FRONT_BLOCKED_M on the real maze before the demo,
the same way the IR thresholds in wall_follower.py get calibrated -- add a
row for them in robot_modules/README.md's settings table once measured.
"""
from rclpy.qos import QoSProfile, ReliabilityPolicy

from goal_tracker import GoalTracker
from lidar_utils import min_range_in_sector
from loop_guard import LoopGuard
from robot_base import ROBOT
from wall_follower import FIND_WALL, FRONT_BLOCKED, WallFollower

try:
    from nav_msgs.msg import Odometry
    from sensor_msgs.msg import LaserScan
except ImportError as exc:  # pragma: no cover - only hit outside a ROS 2 workspace
    raise ImportError(
        'nav_msgs/sensor_msgs not found -- source /opt/ros/jazzy/setup.bash first'
    ) from exc

# ---------- LiDAR settings ----------
LIDAR_TOPIC = ROBOT + '/scan'   # verify on the robot, see module docstring above
LIDAR_FRONT_SECTOR_DEG = 20.0   # +-15 degrees around straight ahead
LIDAR_FRONT_BLOCKED_M = 0.10    # metres -- calibrate against the real maze walls

# ---------- loop-recovery settings ----------
LOOP_CELL_SIZE_M = 0.35   # metres per grid cell -- start near the corridor width
LOOP_REVISIT_LIMIT = 2    # re-entries within the window before it counts as a loop
LOOP_WINDOW_S = 90.0      # seconds a re-entry stays "fresh"
LOOP_COOLDOWN_S = 8.0     # seconds of quiet after switching sides before it can fire again

# ---------- goal-arrival settings ----------
GOAL_ARRIVAL_RADIUS_M = 0.15   # metres -- how close counts as "arrived"; tune on the real maze
ARRIVED_COLOR = (0, 255, 255)  # cyan -- not used by any WallFollower state, easy to spot on demo


class WallFollowerRobust(WallFollower):
    """WallFollower with automatic loop recovery and an optional LiDAR front check."""

    def __init__(self, side='left'):
        super().__init__(side)
        self._loop_guard = LoopGuard(cell_size=LOOP_CELL_SIZE_M,
                                      revisit_limit=LOOP_REVISIT_LIMIT,
                                      window_s=LOOP_WINDOW_S,
                                      cooldown_s=LOOP_COOLDOWN_S)
        self._have_odom = False
        self._lidar_front_blocked = False
        self._odom_x = 0.0
        self._odom_y = 0.0
        self._goal = None
        self._arrived_announced = False

        sensor_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.create_subscription(Odometry, ROBOT + '/odom', self.odom_callback, sensor_qos)
        self.create_subscription(LaserScan, LIDAR_TOPIC, self.scan_callback, sensor_qos)

    # ---------- extra listening ----------
    def odom_callback(self, msg):
        self._have_odom = True
        t = self.get_clock().now().nanoseconds / 1e9
        p = msg.pose.pose.position
        self._odom_x = p.x
        self._odom_y = p.y
        self._loop_guard.update(p.x, p.y, t)

    def set_goal(self, goal_x, goal_y, arrival_radius=GOAL_ARRIVAL_RADIUS_M):
        """Tell the node where the finish mark is, in the odom frame (metres
        forward / metres left of wherever the robot was facing when odom was
        reset -- see goal_tracker.py and INTEGRATION_NOTES.md). Optional: if
        this is never called, decide() behaves exactly as if this feature
        didn't exist."""
        self._goal = GoalTracker(goal_x, goal_y, arrival_radius=arrival_radius)
        self._arrived_announced = False
        self.get_logger().info(
            f'Goal set to ({goal_x:.2f}, {goal_y:.2f}) m, arrival radius {arrival_radius:.2f} m')

    def scan_callback(self, msg):
        closest = min_range_in_sector(msg.ranges, msg.angle_min, msg.angle_increment,
                                       center_deg=0.0, width_deg=LIDAR_FRONT_SECTOR_DEG)
        self._lidar_front_blocked = closest is not None and closest < LIDAR_FRONT_BLOCKED_M

    def switch_side(self):
        """Flip which wall we follow -- the README's manual 'run wall_right in
        round 2' demo tip, done automatically without restarting the node."""
        self.side, self.other = self.other, self.side
        self.sign = -self.sign
        self.get_logger().info(
            f'LoopGuard: kept revisiting the same spot, switching to wall_{self.side}')

    # ---------- overrides ----------
    def front(self):
        """Same as WallFollower.front(), but also counts as blocked if the
        LiDAR sees something close ahead that the IR sensors would miss."""
        ir_front = super().front()
        if self._lidar_front_blocked:
            self.debug = '(lidar front)'
            return max(ir_front, FRONT_BLOCKED + 1)  # force the existing IR threshold to trip
        return ir_front

    def decide(self):
        if self._have_odom:
            if self._goal is not None and self._goal.has_arrived(self._odom_x, self._odom_y):
                if not self._arrived_announced:
                    self._arrived_announced = True
                    self.get_logger().info(
                        f'ARRIVED at goal (closest approach was '
                        f'{self._goal.closest_distance:.2f} m)')
                    self.set_lights(*ARRIVED_COLOR)
                return 0.0, 0.0  # stay stopped at the goal, don't go wandering off again

            t = self.get_clock().now().nanoseconds / 1e9
            if self._loop_guard.should_break_loop(t):
                self.switch_side()
                self.change_state(FIND_WALL)
                self._loop_guard.reset()
                return 0.0, 0.0
        return super().decide()
