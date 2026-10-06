"""Obstacle avoider: the simple reactive version (our first wall_follower.py).

No memory: every 0.1 s it checks priority rules from top to bottom.
"""
from robot_base import RobotBase

FRONT_THRESHOLD = 300   # IR: wall ahead
SIDE_THRESHOLD = 200    # IR: wall too close on a side
SPEED = 0.1             # m/s forward
TURN_SPEED = 0.5        # rad/s turning on the spot
STEER = 0.3             # rad/s small correction while driving

# "States" here are just labels of what the robot is doing right now
STRAIGHT = 'STRAIGHT'
STEER_LEFT = 'STEER_LEFT'
STEER_RIGHT = 'STEER_RIGHT'
TURN_LEFT = 'TURN_LEFT'
TURN_RIGHT = 'TURN_RIGHT'


class ObstacleAvoider(RobotBase):
    """Reactive IR obstacle avoidance with priority rules."""

    STATE_COLORS = {
        STRAIGHT: (0, 255, 0),          # green
        STEER_LEFT: (0, 255, 255),      # cyan
        STEER_RIGHT: (0, 255, 255),     # cyan
        TURN_LEFT: (0, 0, 255),         # blue
        TURN_RIGHT: (0, 0, 255),        # blue
    }

    def __init__(self):
        super().__init__('obstacle_avoider', first_state=STRAIGHT)

    def decide(self):
        """Priority rules: the first one that matches wins."""
        front = self.front_wide()
        left = self.left()
        right = self.ir_value('right')
        self.debug = ''

        if front > FRONT_THRESHOLD:              # 1. wall ahead: turn to the more open side
            if left > right:
                self.change_state(TURN_RIGHT)
                return 0.0, -TURN_SPEED
            self.change_state(TURN_LEFT)
            return 0.0, TURN_SPEED
        if left > SIDE_THRESHOLD:                # 2. too close to the left wall
            self.change_state(STEER_RIGHT)
            return SPEED, -STEER
        if right > SIDE_THRESHOLD:               # 3. too close to the right wall
            self.change_state(STEER_LEFT)
            return SPEED, STEER
        self.change_state(STRAIGHT)              # 4. nothing close
        return SPEED, 0.0
