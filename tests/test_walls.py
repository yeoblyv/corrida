"""Tests for the wall direction, on lidar scans of made-up rooms."""

import math
import random

import pytest

from corrida_exploration import walls

STEP = math.radians(0.5)
BEAMS = 720


def room_scan(
    half_x: float, half_y: float, turn_deg: float, at: tuple[float, float], noise: float = 0.0
) -> list[float]:
    """Lidar ranges from `at` inside a rectangular room turned by turn_deg."""
    turn = math.radians(turn_deg)
    corners = [(-half_x, -half_y), (half_x, -half_y), (half_x, half_y), (-half_x, half_y)]
    corners = [
        (x * math.cos(turn) - y * math.sin(turn), x * math.sin(turn) + y * math.cos(turn))
        for x, y in corners
    ]
    sides = list(zip(corners, corners[1:] + corners[:1]))
    rng = random.Random(1)
    ranges = []
    for i in range(BEAMS):
        a = -math.pi + i * STEP
        dx, dy = math.cos(a), math.sin(a)
        best = math.inf
        for (x1, y1), (x2, y2) in sides:
            # crossing of the beam with one side of the room, t and u as in
            # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
            ex, ey = x2 - x1, y2 - y1
            den = dx * ey - dy * ex
            if abs(den) < 1e-12:
                continue
            t = ((x1 - at[0]) * ey - (y1 - at[1]) * ex) / den
            u = ((x1 - at[0]) * dy - (y1 - at[1]) * dx) / den
            if t > 0 and 0 <= u <= 1:
                best = min(best, t)
        ranges.append(best + rng.gauss(0.0, noise))
    return ranges


def angle_of(ranges: list[float]) -> tuple[float, float]:
    points = walls.scan_points(ranges, -math.pi, STEP, 6.0)
    angle, sure = walls.wall_angle(points)
    return math.degrees(angle), sure


@pytest.mark.parametrize("turn", [0.0, 7.0, -20.0, 33.0, 44.0, 90.0, 127.0])
def test_angle_of_a_turned_room(turn):
    angle, sure = angle_of(room_scan(1.5, 0.9, turn, (0.3, -0.2)))
    assert walls.difference_mod_90(math.radians(angle), math.radians(turn)) == pytest.approx(
        0.0, abs=math.radians(0.5)
    )
    assert sure > 0.95


def test_lidar_noise_of_a_centimetre():
    # the A1M8 is about this noisy at these distances
    angle, sure = angle_of(room_scan(1.5, 0.9, 12.0, (0.2, 0.1), noise=0.01))
    assert angle == pytest.approx(12.0, abs=1.5)
    assert sure > 0.8


def test_result_stays_between_minus_and_plus_45_degrees():
    angle, _ = angle_of(room_scan(1.5, 0.9, 60.0, (0.0, 0.0)))
    assert angle == pytest.approx(-30.0, abs=0.5)


def test_round_room_has_no_wall_direction():
    ranges = [1.0] * BEAMS
    _, sure = angle_of(ranges)
    assert sure < 0.5


def test_points_across_a_doorway_are_not_one_wall_piece():
    # 7 points along one wall, the window would just fit them
    points = [(0.01 * i, 1.0) for i in range(7)]
    pieces = walls.wall_pieces(points)
    assert len(pieces) == 1
    assert pieces[0][0] == pytest.approx(0.0, abs=1e-9)
    assert pieces[0][1] == pytest.approx(0.06)
    # the same wall with a doorway of 0.5 m after the third point
    points = points[:3] + [(x + 0.5, y) for x, y in points[3:]]
    assert walls.wall_pieces(points) == []


def test_no_points_gives_zero():
    assert walls.wall_angle([]) == (0.0, 0.0)


def test_difference_mod_90():
    assert math.degrees(walls.difference_mod_90(math.radians(89.0), 0.0)) == pytest.approx(-1.0)
    assert math.degrees(walls.difference_mod_90(math.radians(10.0), math.radians(-80.0))) == (
        pytest.approx(0.0, abs=1e-9)
    )
