from goal_tracker import GoalTracker


def test_distance_to_goal_is_pythagorean():
    g = GoalTracker(goal_x=3.0, goal_y=4.0)
    assert g.distance_to(0.0, 0.0) == 5.0


def test_has_arrived_false_outside_radius():
    g = GoalTracker(goal_x=2.0, goal_y=0.0, arrival_radius=0.15)
    assert g.has_arrived(0.0, 0.0) is False


def test_has_arrived_true_within_radius():
    g = GoalTracker(goal_x=2.0, goal_y=0.0, arrival_radius=0.15)
    assert g.has_arrived(1.95, 0.0) is True


def test_has_arrived_is_inclusive_at_the_boundary():
    g = GoalTracker(goal_x=1.0, goal_y=0.0, arrival_radius=0.2)
    assert g.has_arrived(0.8, 0.0) is True  # distance == 0.2 exactly


def test_closest_distance_keeps_the_minimum_even_after_moving_away():
    g = GoalTracker(goal_x=0.0, goal_y=0.0, arrival_radius=0.1)
    g.distance_to(1.0, 0.0)   # 1.0 m away
    g.distance_to(0.2, 0.0)   # 0.2 m away -- new closest
    g.distance_to(0.9, 0.0)   # moved back away again
    assert g.closest_distance == 0.2


def test_closest_distance_starts_at_infinity_before_any_reading():
    g = GoalTracker(goal_x=5.0, goal_y=5.0)
    assert g.closest_distance == float('inf')
