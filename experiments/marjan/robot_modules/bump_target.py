"""Bump target: turn to face a nearby obstacle and touch it with the FRONT of the bumper.

The robot waits (or slowly looks around). When an obstacle appears left, right or in front,
it rotates until the obstacle is straight in front, drives slowly to it and touches it.
Then it backs off and waits for the next obstacle.
"""
from robot_base import RobotBase

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
SCAN_TURN = 0.0         # rad/s slow rotation while waiting (0 = stand still, e.g. 0.3 = look around)
APPROACH_SPEED = 0.08   # m/s driving towards the obstacle (slow = gentle hit)
K_AIM = 0.4             # rad/s turning per unit of direction error
MIN_AIM_TURN = 0.2      # rad/s, so small errors still make the robot turn
MAX_AIM_TURN = 0.6      # rad/s, fastest rotation while aiming
MAX_STEER = 0.3         # rad/s, small corrections while approaching
BACKUP_SPEED = 0.1      # m/s reversing after the hit

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


class BumpTarget(RobotBase):
    """Turn to face an obstacle and touch it with the front of the bumper."""

    STATE_COLORS = {                    # (red, green, blue) for the light ring
        WAIT: (255, 255, 255),          # white
        AIM: (255, 255, 0),             # yellow
        APPROACH: (255, 128, 0),        # orange
        HIT: (255, 0, 0),               # red
        RETREAT: (255, 0, 255),         # magenta
    }

    def __init__(self):
        self.last_seen = None           # time when we last saw the obstacle
        self.armed = True               # False after a hit, until the obstacle is removed
        super().__init__('bump_target', first_state=WAIT)

    # ---------- helpers ----------
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
            value = self.ir_value(name)
            total += value
            weighted += value * direction
            if value > strength:
                strength = value
                strongest = name
        if total == 0:
            return 0, 0.0, None
        return strength, weighted / total, strongest

    def seconds_since_seen(self):
        """Seconds since the obstacle was last seen (large number if never)."""
        if self.last_seen is None:
            return 999.0
        return (self.get_clock().now() - self.last_seen).nanoseconds / 1e9

    def aim_turn(self, direction):
        """Turning speed that rotates the robot towards the obstacle."""
        turn = K_AIM * direction
        if abs(turn) < MIN_AIM_TURN:
            turn = MIN_AIM_TURN if direction >= 0 else -MIN_AIM_TURN
        return max(-MAX_AIM_TURN, min(MAX_AIM_TURN, turn))

    # ---------- deciding ----------
    def decide(self):
        """Read the sensors, run the current state's function, return (linear, angular)."""
        strength, direction, strongest = self.obstacle_info()
        if strength > LOST:
            self.last_seen = self.get_clock().now()
        self.debug = f'strength={strength:4} dir={direction:+.2f} strongest={strongest}'

        # The bumper touched something while aiming or approaching = a hit!
        part = self.take_bump()
        if part is not None and self.state in (AIM, APPROACH):
            result = 'FRONT hit, success!' if 'front' in part else 'not the front'
            self.get_logger().info(f'HIT with {part} -> {result}')
            self.change_state(HIT)

        if self.state == WAIT:
            return self.wait(strength)
        if self.state == AIM:
            return self.aim(strength, direction, strongest)
        if self.state == APPROACH:
            return self.approach(direction, strongest)
        if self.state == HIT:
            return self.hit()
        return self.retreat()

    # ---------- one function per state ----------
    def wait(self, strength):
        """Wait (or look around) until an obstacle appears; after a hit, until it was removed."""
        if strength < LOST:
            self.armed = True                  # nothing near: ready for a new obstacle
        if self.armed and strength > DETECT:
            self.change_state(AIM)
            return 0.0, 0.0
        return 0.0, SCAN_TURN

    def aim(self, strength, direction, strongest):
        """Rotate on the spot until the obstacle is straight in front."""
        if strength < LOST:                    # it went away
            self.change_state(WAIT)
            return 0.0, 0.0
        if strongest in CENTER_SENSORS:        # the front-centre sensors see it most = facing it
            self.change_state(APPROACH)
            return 0.0, 0.0
        return 0.0, self.aim_turn(direction)

    def approach(self, direction, strongest):
        """Drive slowly straight at the obstacle until the bumper touches it."""
        if self.seconds_since_seen() > LOST_TIMEOUT:
            self.change_state(WAIT)
            return 0.0, 0.0
        if strongest is not None and abs(IR_DIRECTIONS[strongest]) >= 2.0:
            self.change_state(AIM)             # it is far to the side now: aim again
            return 0.0, 0.0
        return APPROACH_SPEED, max(-MAX_STEER, min(MAX_STEER, K_AIM * direction))

    def hit(self):
        """Stand still for a moment after touching the obstacle."""
        if self.time_in_state() >= HIT_PAUSE:
            self.change_state(RETREAT)
        return 0.0, 0.0

    def retreat(self):
        """Reverse a few centimetres, then wait for the next obstacle."""
        if self.time_in_state() < RETREAT_TIME:
            return -BACKUP_SPEED, 0.0
        self.armed = False                     # do not hit the same obstacle again
        self.change_state(WAIT)
        return 0.0, 0.0
