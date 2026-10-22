import math

from goal_seeking_wall_follower import normalize_angle


def test_normalize_angle_already_in_range():
    assert normalize_angle(0.5) == 0.5


def test_normalize_angle_wraps_above_pi():
    assert abs(normalize_angle(math.pi + 0.1) - (-math.pi + 0.1)) < 1e-9


def test_normalize_angle_wraps_below_minus_pi():
    assert abs(normalize_angle(-math.pi - 0.1) - (math.pi - 0.1)) < 1e-9
