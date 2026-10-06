"""RobotBase: everything that is the SAME for every behaviour.

- listening to the IR sensors and the bumper
- the light ring
- the state machine helpers (change_state, time_in_state)
- the timer that runs 10 times per second
- sending the movement command

A behaviour (wall follower, bump target, ...) inherits from RobotBase and only writes
its own decide() method: "in my current state, what do I do now?"
"""
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from geometry_msgs.msg import Twist
from irobot_create_msgs.msg import (IrIntensityVector, HazardDetectionVector,
                                    HazardDetection, LightringLeds, LedColor)

ROBOT = '/robot_10'
CONTROL_PERIOD = 0.1        # s between decisions (10 times per second)
DEFAULT_COLOR = (255, 0, 255)   # magenta for a state without a colour


class RobotBase(Node):
    """Shared parts of every behaviour. Subclasses must write decide()."""

    STATE_COLORS = {}       # each behaviour fills this: {state: (red, green, blue)}

    def __init__(self, node_name, first_state):
        super().__init__(node_name)
        sensor_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.ir = {}                # newest IR values by name, e.g. {'left': 120, ...}
        self.bump_part = None       # which part of the bumper was hit, e.g. 'bump_front_center'
        self.state = None
        self.state_start = self.get_clock().now()
        self.debug = ''             # extra text a behaviour can show in the log

        self.create_subscription(IrIntensityVector, ROBOT + '/ir_intensity',
                                 self.ir_callback, sensor_qos)
        self.create_subscription(HazardDetectionVector, ROBOT + '/hazard_detection',
                                 self.hazard_callback, sensor_qos)
        self.cmd_pub = self.create_publisher(Twist, ROBOT + '/cmd_vel', 10)
        self.light_pub = self.create_publisher(LightringLeds, ROBOT + '/cmd_lightring', 10)

        self.change_state(first_state)
        self.create_timer(CONTROL_PERIOD, self.control_loop)

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

    # ---------- easy sensor values (IR: BIGGER = CLOSER) ----------
    def ir_value(self, name):
        """Newest value of one IR sensor (0 if not received yet)."""
        return self.ir.get(name, 0)

    def front(self):
        """Wall straight ahead: only the two centre sensors."""
        return max(self.ir_value('front_center_left'), self.ir_value('front_center_right'))

    def front_wide(self):
        """Anything ahead, including the diagonal front sensors."""
        return max(self.ir_value('front_left'), self.front(), self.ir_value('front_right'))

    def left(self):
        """Left wall: the two left-side sensors."""
        return max(self.ir_value('side_left'), self.ir_value('left'))

    def right(self):
        """Right wall: right sensor + diagonal front_right (sees side walls in narrow passages)."""
        return max(self.ir_value('right'), self.ir_value('front_right'))

    def take_bump(self):
        """Return which bumper part was hit since the last call (or None), then forget it."""
        part = self.bump_part
        self.bump_part = None
        return part

    # ---------- state machine helpers ----------
    def change_state(self, new_state):
        """Switch to a new state, remember when it started, and update the lights."""
        if new_state == self.state:
            return
        self.get_logger().info(f'STATE: {self.state} -> {new_state}')
        self.state = new_state
        self.state_start = self.get_clock().now()
        self.set_lights(*self.STATE_COLORS.get(new_state, DEFAULT_COLOR))

    def time_in_state(self):
        """Seconds since the current state started."""
        return (self.get_clock().now() - self.state_start).nanoseconds / 1e9

    # ---------- acting ----------
    def set_lights(self, red, green, blue):
        """Set all 6 LEDs of the light ring to one colour."""
        msg = LightringLeds()
        msg.override_system = True
        msg.leds = [LedColor(red=red, green=green, blue=blue) for _ in range(6)]
        self.light_pub.publish(msg)

    def drive(self, linear, angular):
        """Send a movement command. linear: m/s forward; angular: rad/s (+ = left)."""
        cmd = Twist()
        cmd.linear.x = float(linear)
        cmd.angular.z = float(angular)
        self.cmd_pub.publish(cmd)

    def stop(self):
        """Stop the wheels and give the light ring back to the robot."""
        self.drive(0.0, 0.0)
        lights = LightringLeds()
        lights.override_system = False
        self.light_pub.publish(lights)

    # ---------- the loop ----------
    def control_loop(self):
        """Runs 10 times per second: ask the behaviour what to do, then do it."""
        if not self.ir:
            return
        linear, angular = self.decide()
        self.drive(linear, angular)
        self.get_logger().info(
            f'{self.state:12} front={self.front():4} left={self.left():4} '
            f'right={self.right():4} {self.debug} -> v={linear:.2f} w={angular:.2f}')

    def decide(self):
        """Every behaviour writes its own version. Must return (linear, angular)."""
        raise NotImplementedError('A behaviour must define decide()')
