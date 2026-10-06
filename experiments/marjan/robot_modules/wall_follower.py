"""Wall follower: keep a wall on one side (left-hand or right-hand rule).

WallFollower('left')  -> keep the wall on the LEFT  (inside corner: turn right)
WallFollower('right') -> keep the wall on the RIGHT (inside corner: turn left)
In narrow passages (wall close on both sides) the robot centres itself between the walls.
"""
from robot_base import RobotBase

# IR thresholds (for IR: BIGGER = CLOSER). Calibrate these on the real maze walls!
FRONT_BLOCKED = 300     # start turning away when front is above this
FRONT_CLEAR = 150       # stop turning only when front is below this (hysteresis)
WALL = {                # per side, because the left has 2 sensors and the right only 1
    'left':  {'target': 200, 'lost': 40, 'close': 150},
    'right': {'target': 200, 'lost': 40, 'close': 150},
}
# target: value we want while following that wall (= desired distance)
# lost:   below this there is no wall on that side anymore
# close:  above this the wall is close (used for the OTHER side -> narrow passage)

# Motion settings
SPEED = 0.12            # m/s forward
NARROW_SPEED = 0.08     # m/s forward in narrow passages
TURN_SPEED = 0.6        # rad/s when rotating on the spot
KP = 0.002              # steering strength per IR unit (following one wall)
KP_CENTER = 0.002       # steering strength per IR unit (centring between two walls)
MAX_STEER = 0.5         # rad/s, limit for the steering correction
CORNER_STRAIGHT_TIME = 0.8   # s: drive past the wall end before curving in
TURN_INTO_TIMEOUT = 6.0      # s: give up curving and search for a wall again
BACKUP_TIME = 0.4            # s: reverse after a bump
BACKUP_TURN_TIME = 0.6       # s: then rotate away from the wall

# States
FIND_WALL = 'FIND_WALL'
FOLLOW_WALL = 'FOLLOW_WALL'
TURN_AWAY = 'TURN_AWAY'      # inside corner: rotate away from our wall (left side: turn right)
TURN_INTO = 'TURN_INTO'      # opening on our side: curve into it (left side: turn left)
BACK_UP = 'BACK_UP'


class WallFollower(RobotBase):
    """Follow one wall through the maze with a state machine."""

    STATE_COLORS = {                 # (red, green, blue) for the light ring
        FIND_WALL: (255, 255, 255),  # white
        FOLLOW_WALL: (0, 255, 0),    # green
        TURN_AWAY: (0, 0, 255),      # blue
        TURN_INTO: (255, 255, 0),    # yellow
        BACK_UP: (255, 0, 0),        # red
    }

    def __init__(self, side='left'):
        if side not in ('left', 'right'):
            raise ValueError("side must be 'left' or 'right'")
        self.side = side
        self.other = 'right' if side == 'left' else 'left'
        # +1 if our wall is on the left. Turning TOWARDS our wall = +sign, AWAY = -sign.
        self.sign = 1.0 if side == 'left' else -1.0
        super().__init__(f'wall_follower_{side}', first_state=FIND_WALL)

    def decide(self):
        """Read the sensors, run the current state's function, return (linear, angular)."""
        front = self.front()
        near = self.left() if self.side == 'left' else self.right()    # the wall we follow
        far = self.right() if self.side == 'left' else self.left()     # the opposite wall
        self.debug = ''

        # A bump overrides everything (except when we are already backing up)
        if self.take_bump() is not None and self.state != BACK_UP:
            self.change_state(BACK_UP)

        if self.state == FIND_WALL:
            return self.find_wall(front, near)
        if self.state == FOLLOW_WALL:
            return self.follow_wall(front, near, far)
        if self.state == TURN_AWAY:
            return self.turn_away(front)
        if self.state == TURN_INTO:
            return self.turn_into(front, near)
        return self.back_up()

    # ---------- one function per state ----------
    def find_wall(self, front, near):
        """Drive straight until a wall is found ahead or on our side."""
        if front > FRONT_BLOCKED:
            self.change_state(TURN_AWAY)
            return 0.0, 0.0
        if near > WALL[self.side]['lost']:
            self.change_state(FOLLOW_WALL)
        return SPEED, 0.0

    def follow_wall(self, front, near, far):
        """Drive along our wall; centre between walls in narrow passages."""
        if front > FRONT_BLOCKED:                      # inside corner
            self.change_state(TURN_AWAY)
            return 0.0, 0.0
        if near < WALL[self.side]['lost']:             # opening on our side
            self.change_state(TURN_INTO)
            return SPEED, 0.0

        if far > WALL[self.other]['close']:            # narrow passage: stay in the middle
            error = near - far                         # positive = closer to our wall
            steer = -self.sign * KP_CENTER * error     # -> steer away from our wall
            speed = NARROW_SPEED
            self.debug = '(narrow)'
        else:                                          # normal: keep distance to our wall
            error = near - WALL[self.side]['target']   # positive = too close to our wall
            steer = -self.sign * KP * error
            speed = SPEED
        return speed, max(-MAX_STEER, min(MAX_STEER, steer))

    def turn_away(self, front):
        """Rotate away from our wall until the front is clearly free (hysteresis)."""
        if front < FRONT_CLEAR:
            self.change_state(FOLLOW_WALL)
            return 0.0, 0.0
        return 0.0, -self.sign * TURN_SPEED

    def turn_into(self, front, near):
        """Drive past the end of our wall, then curve into the opening."""
        if front > FRONT_BLOCKED:
            self.change_state(TURN_AWAY)
            return 0.0, 0.0
        t = self.time_in_state()
        if t < CORNER_STRAIGHT_TIME:                   # first drive past the end of the wall
            return SPEED, 0.0
        if near > WALL[self.side]['lost']:             # found the new wall
            self.change_state(FOLLOW_WALL)
            return SPEED, 0.0
        if t > TURN_INTO_TIMEOUT:                      # curved too long: open space
            self.change_state(FIND_WALL)
            return 0.0, 0.0
        return SPEED * 0.5, self.sign * TURN_SPEED * 0.8   # curve towards our side

    def back_up(self):
        """After a bump: reverse a little, then rotate away from the wall, then follow again."""
        t = self.time_in_state()
        if t < BACKUP_TIME:
            return -0.1, 0.0
        if t < BACKUP_TIME + BACKUP_TURN_TIME:
            return 0.0, -self.sign * TURN_SPEED
        self.change_state(FOLLOW_WALL)
        return 0.0, 0.0
