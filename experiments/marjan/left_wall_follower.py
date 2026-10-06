"""Left-hand wall follower for the iRobot Create 3, using only IR sensors and bumpers.

Strategy: keep a wall on the robot's LEFT side (left-hand rule).
In narrow passages (wall close on both sides) the robot centres itself between the walls.
A state machine decides what the robot is doing; the light ring shows the state.
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from geometry_msgs.msg import Twist
from irobot_create_msgs.msg import (IrIntensityVector, HazardDetectionVector,
                                    HazardDetection, LightringLeds, LedColor)

ROBOT = '/robot_10'

# IR thresholds (for IR: BIGGER = CLOSER). Calibrate these on the real maze walls!
FRONT_BLOCKED = 300     # start turning right when front is above this
FRONT_CLEAR = 150       # stop turning right only when front is below this (hysteresis)
LEFT_TARGET = 200       # the left value we want while following (= desired distance)
LEFT_LOST = 40          # below this, there is no wall on the left anymore
RIGHT_CLOSE = 150       # right value above this = narrow passage -> centre between walls

# Motion settings
SPEED = 0.12            # m/s forward
NARROW_SPEED = 0.08     # m/s forward in narrow passages
TURN_SPEED = 0.6        # rad/s when rotating on the spot
KP = 0.002              # steering strength per IR unit (following the left wall)
KP_CENTER = 0.002       # steering strength per IR unit (centring between two walls)
MAX_STEER = 0.5         # rad/s, limit for the steering correction
CORNER_STRAIGHT_TIME = 0.8   # s: drive past the wall end before curving left
TURN_LEFT_TIMEOUT = 6.0      # s: give up curving and search for a wall again
BACKUP_TIME = 0.4            # s: reverse after a bump
BACKUP_TURN_TIME = 0.6       # s: then rotate right

# States
FIND_WALL = 'FIND_WALL'
FOLLOW_WALL = 'FOLLOW_WALL'
TURN_RIGHT = 'TURN_RIGHT'
TURN_LEFT = 'TURN_LEFT'
BACK_UP = 'BACK_UP'

STATE_COLORS = {                 # (red, green, blue) for the light ring
    FIND_WALL: (255, 255, 255),  # white
    FOLLOW_WALL: (0, 255, 0),    # green
    TURN_RIGHT: (0, 0, 255),     # blue
    TURN_LEFT: (255, 255, 0),    # yellow
    BACK_UP: (255, 0, 0),        # red
}


class LeftWallFollower(Node):
    """Follow the left wall through the maze with a simple state machine."""

    def __init__(self):
        super().__init__('left_wall_follower')
        sensor_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.ir = {}
        self.bumped = False
        self.state = None
        self.state_start = self.get_clock().now()

        self.create_subscription(IrIntensityVector, ROBOT + '/ir_intensity',
                                 self.ir_callback, sensor_qos)
        self.create_subscription(HazardDetectionVector, ROBOT + '/hazard_detection',
                                 self.hazard_callback, sensor_qos)
        self.cmd_pub = self.create_publisher(Twist, ROBOT + '/cmd_vel', 10)
        self.light_pub = self.create_publisher(LightringLeds, ROBOT + '/cmd_lightring', 10)

        self.change_state(FIND_WALL)
        self.create_timer(0.1, self.control_loop)

    # ---------- listening ----------
    def ir_callback(self, msg):
        """Store the newest value of each IR sensor by name."""
        for r in msg.readings:
            name = r.header.frame_id.replace('ir_intensity_', '')
            self.ir[name] = r.value

    def hazard_callback(self, msg):
        """Remember that the bumper was hit."""
        for d in msg.detections:
            if d.type == HazardDetection.BUMP:
                self.bumped = True

    # ---------- helpers ----------
    def change_state(self, new_state):
        """Switch to a new state, remember when it started, and update the lights."""
        if new_state == self.state:
            return
        self.get_logger().info(f'STATE: {self.state} -> {new_state}')
        self.state = new_state
        self.state_start = self.get_clock().now()
        self.set_lights(*STATE_COLORS[new_state])

    def time_in_state(self):
        """Seconds since the current state started."""
        return (self.get_clock().now() - self.state_start).nanoseconds / 1e9

    def set_lights(self, red, green, blue):
        """Set all 6 LEDs of the light ring to one colour."""
        msg = LightringLeds()
        msg.override_system = True
        msg.leds = [LedColor(red=red, green=green, blue=blue) for _ in range(6)]
        self.light_pub.publish(msg)

    # ---------- deciding ----------
    def control_loop(self):
        """Read the sensors, run the current state's function, publish the command."""
        if not self.ir:
            return

        # "Wall ahead" = only the two sensors that look straight forward
        front = max(self.ir.get('front_center_left', 0), self.ir.get('front_center_right', 0))
        # Left wall: the two left-side sensors
        left = max(self.ir.get('side_left', 0), self.ir.get('left', 0))
        # Right wall: the right sensor + the diagonal front_right (sees side walls in narrow passages)
        right = max(self.ir.get('right', 0), self.ir.get('front_right', 0))

        # A bump overrides everything (except when we are already backing up)
        if self.bumped and self.state != BACK_UP:
            self.change_state(BACK_UP)
        self.bumped = False

        # Each state has its own small function; it returns the command for this tick
        if self.state == FIND_WALL:
            cmd = self.find_wall(front, left)
        elif self.state == FOLLOW_WALL:
            cmd = self.follow_wall(front, left, right)
        elif self.state == TURN_RIGHT:
            cmd = self.turn_right(front)
        elif self.state == TURN_LEFT:
            cmd = self.turn_left(front, left)
        else:
            cmd = self.back_up()

        self.get_logger().info(
            f'{self.state:12} front={front:4} left={left:4} right={right:4} '
            f'-> v={cmd.linear.x:.2f} w={cmd.angular.z:.2f}')
        self.cmd_pub.publish(cmd)

    # ---------- one function per state ----------
    def find_wall(self, front, left):
        """Drive straight until a wall is found ahead or on the left."""
        cmd = Twist()
        if front > FRONT_BLOCKED:
            self.change_state(TURN_RIGHT)
        elif left > LEFT_LOST:
            self.change_state(FOLLOW_WALL)
        else:
            cmd.linear.x = SPEED
        return cmd

    def follow_wall(self, front, left, right):
        """Drive along the left wall; centre between walls in narrow passages."""
        cmd = Twist()
        if front > FRONT_BLOCKED:              # inside corner
            self.change_state(TURN_RIGHT)
            return cmd                         # stop for this tick
        if left < LEFT_LOST:                   # opening on the left
            self.change_state(TURN_LEFT)
            cmd.linear.x = SPEED
            return cmd

        if right > RIGHT_CLOSE:                # narrow passage: stay in the middle
            error = left - right               # positive = closer to the left wall
            steer = -KP_CENTER * error
            cmd.linear.x = NARROW_SPEED
        else:                                  # normal: keep distance to the left wall
            error = left - LEFT_TARGET         # positive = too close to the left wall
            steer = -KP * error
            cmd.linear.x = SPEED

        cmd.angular.z = max(-MAX_STEER, min(MAX_STEER, steer))
        return cmd

    def turn_right(self, front):
        """Rotate right on the spot until the front is clearly free (hysteresis)."""
        cmd = Twist()
        if front < FRONT_CLEAR:
            self.change_state(FOLLOW_WALL)
        else:
            cmd.angular.z = -TURN_SPEED
        return cmd

    def turn_left(self, front, left):
        """Drive past the end of the left wall, then curve left into the opening."""
        cmd = Twist()
        if front > FRONT_BLOCKED:
            self.change_state(TURN_RIGHT)
            return cmd
        t = self.time_in_state()
        if t < CORNER_STRAIGHT_TIME:           # first drive past the end of the wall
            cmd.linear.x = SPEED
        elif left > LEFT_LOST:                 # found the new left wall
            self.change_state(FOLLOW_WALL)
        elif t > TURN_LEFT_TIMEOUT:            # curved too long: open space
            self.change_state(FIND_WALL)
        else:                                  # curve left into the opening
            cmd.linear.x = SPEED * 0.5
            cmd.angular.z = TURN_SPEED * 0.8
        return cmd

    def back_up(self):
        """After a bump: reverse a little, then rotate right, then follow again."""
        cmd = Twist()
        t = self.time_in_state()
        if t < BACKUP_TIME:
            cmd.linear.x = -0.1
        elif t < BACKUP_TIME + BACKUP_TURN_TIME:
            cmd.angular.z = -TURN_SPEED
        else:
            self.change_state(FOLLOW_WALL)
        return cmd


def main():
    rclpy.init()
    node = LeftWallFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.cmd_pub.publish(Twist())              # stop the wheels
    lights = LightringLeds()
    lights.override_system = False             # give the light ring back to the robot
    node.light_pub.publish(lights)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()