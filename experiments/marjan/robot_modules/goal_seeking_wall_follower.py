"""GoalSeekingWallFollower: an additive, optional extra layer on top of
WallFollowerRobust.

When a goal is set (set_goal()) and the straight line ahead toward it looks
clear, the robot steers directly at the goal instead of blindly following a
wall -- a simplified "Bug"-style navigator (see INTEGRATION_NOTES.md /
course FAQ for the literature angle). The moment something is in the way,
or the goal is no longer roughly ahead, it falls straight back to the exact
same tested wall-following + LoopGuard + arrival logic used by
wall_left_robust/wall_right_robust -- nothing in wall_follower.py or
wall_follower_robust.py is touched by this file.

This is a SEPARATE behaviour (see main.py: wall_left_bug / wall_right_bug),
not a replacement: wall_left_robust/wall_right_robust are completely
unaffected by this file existing, so if this does not behave well on the
real maze, just keep using those for the demo instead.

Also works with no goal set at all: decide() then skips straight to the
exact same WallFollowerRobust behaviour (wall-follow + LoopGuard), same as
today.
"""
import math

from wall_follower import FIND_WALL, FRONT_BLOCKED, SPEED
from wall_follower_robust import ARRIVED_COLOR, WallFollowerRobust

# ---------- goal-seeking settings (tune on the real maze) ----------
SEEK_ANGLE_TOLERANCE_DEG = 35.0   # goal must be within this cone of current heading to go direct
SEEK_KP_ANGULAR = 1.5             # proportional gain: bearing error (rad) -> angular speed (rad/s)
SEEK_MAX_ANGULAR = 0.5            # clamp, same scale as wall_follower.py's MAX_STEER/TURN_SPEED


def normalize_angle(angle):
    """Wrap an angle (radians) into [-pi, pi]. Pure function, unit-tested
    separately in tests/ -- no ROS needed."""
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle


class GoalSeekingWallFollower(WallFollowerRobust):
    """WallFollowerRobust that drives straight at the goal whenever the path
    ahead is clear, and only falls back to wall-following when blocked."""

    def __init__(self, side='left'):
        super().__init__(side)
        self._yaw = 0.0

    def odom_callback(self, msg):
        super().odom_callback(msg)  # keeps _odom_x/_odom_y/_have_odom/LoopGuard updated as before
        q = msg.pose.pose.orientation
        self._yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))

    def _bearing_to_goal(self):
        """Angle (radians, signed) from the robot's current heading to the
        goal: 0 = straight ahead, positive = goal is to the left."""
        dx = self._goal.goal_x - self._odom_x
        dy = self._goal.goal_y - self._odom_y
        return normalize_angle(math.atan2(dy, dx) - self._yaw)

    def decide(self):
        if self._have_odom and self._goal is not None:
            if self._goal.has_arrived(self._odom_x, self._odom_y):
                if not self._arrived_announced:
                    self._arrived_announced = True
                    self.get_logger().info(
                        f'ARRIVED at goal (closest approach was '
                        f'{self._goal.closest_distance:.2f} m)')
                    self.set_lights(*ARRIVED_COLOR)
                return 0.0, 0.0

            t = self.get_clock().now().nanoseconds / 1e9
            if self._loop_guard.should_break_loop(t):
                self.switch_side()
                self.change_state(FIND_WALL)
                self._loop_guard.reset()
                return 0.0, 0.0

            bearing = self._bearing_to_goal()
            front_clear = self.front() < FRONT_BLOCKED
            if front_clear and abs(math.degrees(bearing)) <= SEEK_ANGLE_TOLERANCE_DEG:
                angular = max(-SEEK_MAX_ANGULAR, min(SEEK_MAX_ANGULAR, SEEK_KP_ANGULAR * bearing))
                self.debug = f'(seek goal, bearing={math.degrees(bearing):+.0f} deg)'
                self.get_logger().info(
                    f'SEEK_GOAL  bearing={math.degrees(bearing):+.1f} deg -> v={SPEED:.2f} w={angular:.2f}')
                return SPEED, angular

        return super().decide()
