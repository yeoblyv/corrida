"""GoalTracker: pure Python, no ROS imports (easy to unit test).

Knows one thing: how far the robot currently is from a known goal position,
in the SAME (x, y) frame as odometry. It does NOT steer the robot towards
the goal -- it only answers "have we arrived?" so the robot can stop and
announce it, on top of whatever wall-following behaviour is already
driving it.

Coordinate convention (important, see INTEGRATION_NOTES.md): odometry's
origin (0, 0) and its +x axis are wherever the robot was pointing the
moment it was powered on / odometry was reset. So measure the goal's
position using that same convention: place the robot at the start mark
facing the direction you will call "forward", then measure the goal as
(metres forward, metres to the left) of that -- that pair is (goal_x,
goal_y) below, no rotation math needed.
"""
import math


class GoalTracker:
    def __init__(self, goal_x, goal_y, arrival_radius=0.15):
        self.goal_x = goal_x
        self.goal_y = goal_y
        self.arrival_radius = arrival_radius
        self.closest_distance = math.inf

    def distance_to(self, x, y):
        """Distance from (x, y) to the goal. Also remembers the smallest
        distance ever seen (self.closest_distance), handy for the report
        even on a run that never quite arrives."""
        d = math.hypot(self.goal_x - x, self.goal_y - y)
        if d < self.closest_distance:
            self.closest_distance = d
        return d

    def has_arrived(self, x, y):
        """True once (x, y) is within arrival_radius of the goal."""
        return self.distance_to(x, y) <= self.arrival_radius
