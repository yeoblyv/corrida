"""Bump target for the iRobot Create 3, using only IR sensors and bumpers.

The robot searches for an obstacle with its IR sensors, turns to face it,
drives slowly towards it and touches it with the FRONT bumper.
Then it backs off, turns around and searches for the next obstacle.
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

# IR thresholds (for IR: BIGGER = CLOSER). Calibrate these!
DETECT = 60             # strongest IR value above this = "I see an obstacle"
LOST = 30               # below this = "obstacle gone" (hysteresis)
AIM_TOLERANCE = 0.4     # |direction| below this = obstacle is straight ahead

# Motion settings
SEARCH_SPEED = 0.10     # m/s wandering while searching
APPROACH_SPEED = 0.08   # m/s driving towards the obstacle (slow = gentle hit)
TURN_SPEED = 0.6        # rad/s when rotating on the spot
K_AIM = 0.4             # rad/s turning per unit of direction error
MIN_AIM_TURN = 0.2      # rad/s, so small errors still make the robot turn
MAX_STEER = 0.5         # rad/s, limit for steering while approaching
BACKUP_SPEED = 0.1      # m/s reversing after the hit

# Timing
LOST_TIMEOUT = 1.0      # s without seeing the obstacle while approaching -> search again
HIT_PAUSE = 1.0         # s standing still after the hit
RETREAT_TIME = 0.6      # s reversing after the hit (the Create 3 limits long reversing)
TURN_AROUND_TIME = 5.2  # s rotating at TURN_SPEED (0.6 rad/s * 5.2 s = about 180 degrees)
HIT_ONLY_ONCE = False   # True: stop after the first hit

# States
SEARCH = 'SEARCH'
AIM = 'AIM'
APPROACH = 'APPROACH'
HIT = 'HIT'
RETREAT = 'RETREAT'
TURN_AROUND = 'TURN_AROUND'
DONE = 'DONE'

STATE_COLORS = {                    # (red, green, blue) for the light ring
    SEARCH: (255, 255, 255),        # white
    AIM: (255, 255, 0),             # yellow
    APPROACH: (255, 128, 0),        # orange
    HIT: (255, 0, 0),               # red
    RETREAT: (255, 0, 255),         # magenta
    TURN_AROUND: (0, 0, 255),       # blue
    DONE: (0, 255, 0),              # green
}


class BumpTarget(Node):
    """Find an obstacle with the IR sensors and touch it with the front bumper."""

    def __init__(self):
        super().__init__('bump_target')
        sensor_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.ir = {}
        self.bumped = False
        self.state = None
        self.state_start = self.get_clock().now()
        self.last_seen = None           # time when we last saw the obstacle

        self.create_subscription(IrIntensityVector, ROBOT + '/ir_intensity',
                                 self.ir_callback, sensor_qos)
        self.create_subscription(HazardDetectionVector, ROBOT + '/hazard_detection',
                                 self.hazard_callback, sensor_qos)
        self.cmd_pub = self.create_publisher(Twist, ROBOT + '/cmd_vel', 10)
        self.light_pub = self.create_publisher(LightringLeds, ROBOT + '/cmd_lightring', 10)

        self.change_state(SEARCH)
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

    def obstacle_direction(self):
        """Where is the obstacle? Returns (strength, direction).

        strength : the highest IR value (how close the obstacle is)
        direction: weighted average of the sensor directions (+ = left, - = right, 0 = ahead)
        """
        total = 0.0
        weighted = 0.0
        strength = 0
        for name, direction in IR_DIRECTIONS.items():
            value = self.ir.get(name, 0)
            total += value
            weighted += value * direction
            strength = max(strength, value)
        if total == 0:
            return 0, 0.0
        return strength, weighted / total

    def aim_turn(self, direction):
        """Turning speed that rotates the robot towards the obstacle."""
        turn = K_AIM * direction
        if abs(turn) < MIN_AIM_TURN:
            turn = MIN_AIM_TURN if direction >= 0 else -MIN_AIM_TURN
        return max(-TURN_SPEED, min(TURN_SPEED, turn))

    # ---------- deciding ----------
    def control_loop(self):
        """Read the sensors, run the current state's function, publish the command."""
        if not self.ir:
            return

        strength, direction = self.obstacle_direction()
        if strength > LOST:
            self.last_seen = self.get_clock().now()

        # The bumper touched something while searching/aiming/approaching = a hit!
        if self.bumped and self.state in (SEARCH, AIM, APPROACH):
            self.change_state(HIT)
        self.bumped = False

        # Each state has its own small function; it returns the command for this tick
        if self.state == SEARCH:
            cmd = self.search(strength)
        elif self.state == AIM:
            cmd = self.aim(strength, direction)
        elif self.state == APPROACH:
            cmd = self.approach(direction)
        elif self.state == HIT:
            cmd = self.hit()
        elif self.state == RETREAT:
            cmd = self.retreat()
        elif self.state == TURN_AROUND:
            cmd = self.turn_around()
        else:
            cmd = Twist()                      # DONE: stand still

        self.get_logger().info(
            f'{self.state:12} strength={strength:4} direction={direction:+.2f} '
            f'-> v={cmd.linear.x:.2f} w={cmd.angular.z:.2f}')
        self.cmd_pub.publish(cmd)

    # ---------- one function per state ----------
    def search(self, strength):
        """Drive slowly forward until an obstacle is seen."""
        cmd = Twist()
        if strength > DETECT:
            self.change_state(AIM)
        else:
            cmd.linear.x = SEARCH_SPEED
        return cmd

    def aim(self, strength, direction):
        """Rotate on the spot until the obstacle is straight ahead."""
        cmd = Twist()
        if strength < LOST:                    # lost it
            self.change_state(SEARCH)
        elif abs(direction) < AIM_TOLERANCE:   # straight ahead now
            self.change_state(APPROACH)
        else:
            cmd.angular.z = self.aim_turn(direction)
        return cmd

    def approach(self, direction):
        """Drive slowly towards the obstacle, keeping it centred, until the bumper touches it."""
        cmd = Twist()
        if self.seconds_since_seen() > LOST_TIMEOUT:
            self.change_state(SEARCH)
        elif abs(direction) > 2 * AIM_TOLERANCE:   # drifted far off: aim again
            self.change_state(AIM)
        else:
            cmd.linear.x = APPROACH_SPEED
            cmd.angular.z = max(-MAX_STEER, min(MAX_STEER, K_AIM * direction))
        return cmd

    def hit(self):
        """Stand still for a moment after touching the obstacle."""
        cmd = Twist()
        if self.time_in_state() >= HIT_PAUSE:
            self.change_state(RETREAT)
        return cmd

    def retreat(self):
        """Reverse a few centimetres."""
        cmd = Twist()
        if self.time_in_state() < RETREAT_TIME:
            cmd.linear.x = -BACKUP_SPEED
        else:
            self.change_state(DONE if HIT_ONLY_ONCE else TURN_AROUND)
        return cmd

    def turn_around(self):
        """Rotate about 180 degrees so we do not hit the same obstacle again."""
        cmd = Twist()
        if self.time_in_state() < TURN_AROUND_TIME:
            cmd.angular.z = TURN_SPEED
        else:
            self.change_state(SEARCH)
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