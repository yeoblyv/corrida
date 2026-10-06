"""Bump target for the iRobot Create 3, using only IR sensors and bumpers.

The robot stands still and waits. When an obstacle appears (left, right or in front),
it rotates on the spot until the obstacle is straight in front, drives slowly to it
and touches it with the FRONT of the bumper. Then it backs off and waits again.
A state machine decides what the robot is doing; the light ring shows the state.
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from geometry_msgs.msg import Twist
from irobot_create_msgs.msg import (IrIntensityVector, HazardDetectionVector,
                                    HazardDetection, LightringLeds, LedColor)

ROBOT = '/robot_10'

# Rough direction of each IR sensor: + = left, - = right, 0 = straight ahead
IR_DIRECTIONS = {
    'side_left': 3.0,
    'left': 2.0,
    'front_left': 1.0,
    'front_center_left': 0.3,
    'front_center_right': -0.3,
    'front_right': -1.0,
    'right': -2.0,
}
CENTER_SENSORS = ('front_center_left', 'front_center_right')

# IR thresholds (for IR: BIGGER = CLOSER). Calibrate these!
DETECT = 60             # strongest IR value above this = "I see an obstacle"
LOST = 30               # below this = "obstacle gone" (hysteresis)

# Motion settings
APPROACH_SPEED = 0.08   # m/s driving towards the obstacle (slow = gentle hit)
K_AIM = 0.4             # rad/s turning per unit of direction error
MIN_AIM_TURN = 0.2      # rad/s, so small errors still make the robot turn
MAX_AIM_TURN = 0.6      # rad/s, fastest rotation while aiming
MAX_STEER = 0.3         # rad/s, small corrections while approaching
BACKUP_SPEED = 0.1      # m/s reversing after the hit
SCAN_TURN = 0.3         # rad/s slow rotation while waiting (0 = stand still)

# Timing
LOST_TIMEOUT = 1.0      # s without seeing the obstacle while approaching -> wait again
HIT_PAUSE = 1.0         # s standing still after the hit
RETREAT_TIME = 0.6      # s reversing after the hit (the Create 3 limits long reversing)

# States
WAIT = 'WAIT'
AIM = 'AIM'
APPROACH = 'APPROACH'
HIT = 'HIT'
RETREAT = 'RETREAT'

STATE_COLORS = {                    # (red, green, blue) for the light ring
    WAIT: (255, 255, 255),          # white
    AIM: (255, 255, 0),             # yellow
    APPROACH: (255, 128, 0),        # orange
    HIT: (255, 0, 0),               # red
    RETREAT: (255, 0, 255),         # magenta
}


class BumpTarget(Node):
    """Turn to face an obstacle and touch it with the front of the bumper."""

    def __init__(self):
        super().__init__('bump_target')
        sensor_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.ir = {}
        self.bump_part = None           # which part of the bumper was hit, e.g. 'bump_front_center'
        self.state = None
        self.state_start = self.get_clock().now()
        self.last_seen = None           # time when we last saw the obstacle
        self.armed = True               # False after a hit, until the obstacle is removed

        self.create_subscription(IrIntensityVector, ROBOT + '/ir_intensity',
                                 self.ir_callback, sensor_qos)
        self.create_subscription(HazardDetectionVector, ROBOT + '/hazard_detection',
                                 self.hazard_callback, sensor_qos)
        self.cmd_pub = self.create_publisher(Twist, ROBOT + '/cmd_vel', 10)
        self.light_pub = self.create_publisher(LightringLeds, ROBOT + '/cmd_lightring', 10)

        self.change_state(WAIT)
        self.create_timer(0.1, self.control_loop)

    # ---------- listening ----------
    def ir_callback(self, msg):
        """Store the newest value of each IR sensor by name."""
        for r in msg.readings:
            name = r.header.frame_id.replace('ir_intensity_', '')
            self.ir[name] = r.value

    def hazard_callback(self, msg):
        """Remember that the bumper was hit, and which part of it."""
        for d in msg.detections:
            if d.type == HazardDetection.BUMP:
                self.bump_part = d.header.frame_id

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

    def seconds_since_seen(self):
        """Seconds since the obstacle was last seen (large number if never)."""
        if self.last_seen is None:
            return 999.0
        return (self.get_clock().now() - self.last_seen).nanoseconds / 1e9

    def set_lights(self, red, green, blue):
        """Set all 6 LEDs of the light ring to one colour."""
        msg = LightringLeds()
        msg.override_system = True
        msg.leds = [LedColor(red=red, green=green, blue=blue) for _ in range(6)]
        self.light_pub.publish(msg)

    def obstacle_info(self):
        """Where is the obstacle? Returns (strength, direction, strongest_sensor).

        strength        : the highest IR value (how close the obstacle is)
        direction       : weighted average of sensor directions (+ = left, - = right, 0 = ahead)
        strongest_sensor: name of the sensor that sees it most
        """
        total = 0.0
        weighted = 0.0
        strength = 0
        strongest = None
        for name, direction in IR_DIRECTIONS.items():
            value = self.ir.get(name, 0)
            total += value
            weighted += value * direction
            if value > strength:
                strength = value
                strongest = name
        if total == 0:
            return 0, 0.0, None
        return strength, weighted / total, strongest

    def aim_turn(self, direction):
        """Turning speed that rotates the robot towards the obstacle."""
        turn = K_AIM * direction
        if abs(turn) < MIN_AIM_TURN:
            turn = MIN_AIM_TURN if direction >= 0 else -MIN_AIM_TURN
        return max(-MAX_AIM_TURN, min(MAX_AIM_TURN, turn))

    # ---------- deciding ----------
    def control_loop(self):
        """Read the sensors, run the current state's function, publish the command."""
        if not self.ir:
            return

        strength, direction, strongest = self.obstacle_info()
        if strength > LOST:
            self.last_seen = self.get_clock().now()

        # The bumper touched something while aiming or approaching = a hit!
        if self.bump_part is not None and self.state in (AIM, APPROACH):
            front_hit = 'front' in self.bump_part
            self.get_logger().info(
                f'HIT with {self.bump_part} -> {"FRONT hit, success!" if front_hit else "not the front"}')
            self.change_state(HIT)
        self.bump_part = None

        # Each state has its own small function; it returns the command for this tick
        if self.state == WAIT:
            cmd = self.wait(strength)
        elif self.state == AIM:
            cmd = self.aim(strength, direction, strongest)
        elif self.state == APPROACH:
            cmd = self.approach(direction, strongest)
        elif self.state == HIT:
            cmd = self.hit()
        else:
            cmd = self.retreat()

        self.get_logger().info(
            f'{self.state:9} strength={strength:4} direction={direction:+.2f} '
            f'strongest={strongest} -> v={cmd.linear.x:.2f} w={cmd.angular.z:.2f}')
        self.cmd_pub.publish(cmd)

    # ---------- one function per state ----------
    def wait(self, strength):
        """Rotate slowly on the spot until an obstacle appears (after a hit: until it was removed)."""
        cmd = Twist()
        if strength < LOST:
            self.armed = True                  # nothing near: ready for a new obstacle
        if self.armed and strength > DETECT:
            self.change_state(AIM)
        else:
            cmd.angular.z = SCAN_TURN          # slowly look around
        return cmd

    def aim(self, strength, direction, strongest):
        """Rotate on the spot until the obstacle is straight in front."""
        cmd = Twist()
        if strength < LOST:                    # it went away
            self.change_state(WAIT)
        elif strongest in CENTER_SENSORS:      # the front-centre sensors see it most = facing it
            self.change_state(APPROACH)
        else:
            cmd.angular.z = self.aim_turn(direction)
        return cmd

    def approach(self, direction, strongest):
        """Drive slowly straight at the obstacle until the bumper touches it."""
        cmd = Twist()
        if self.seconds_since_seen() > LOST_TIMEOUT:
            self.change_state(WAIT)
        elif strongest not in CENTER_SENSORS and strongest is not None and \
                abs(IR_DIRECTIONS[strongest]) >= 2.0:   # it is far to the side now: aim again
            self.change_state(AIM)
        else:
            cmd.linear.x = APPROACH_SPEED
            cmd.angular.z = max(-MAX_STEER, min(MAX_STEER, K_AIM * direction))
        return cmd

    def hit(self):
        """Stand still for a moment after touching the obstacle."""
        if self.time_in_state() >= HIT_PAUSE:
            self.change_state(RETREAT)
        return Twist()

    def retreat(self):
        """Reverse a few centimetres, then wait for the next obstacle."""
        cmd = Twist()
        if self.time_in_state() < RETREAT_TIME:
            cmd.linear.x = -BACKUP_SPEED
        else:
            self.armed = False                 # do not hit the same obstacle again
            self.change_state(WAIT)
        return cmd


def main():
    rclpy.init()
    node = BumpTarget()
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