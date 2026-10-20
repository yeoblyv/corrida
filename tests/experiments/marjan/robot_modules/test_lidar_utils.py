"""Unit tests for lidar_utils. Run with: pytest tests/"""
import math

from lidar_utils import angle_to_index, min_range_in_sector


def make_scan(n=360, angle_min_deg=-180.0, angle_max_deg=180.0, fill=float("inf")):
    """A LaserScan-shaped ranges array, all set to `fill` (default: nothing in range)."""
    angle_min = math.radians(angle_min_deg)
    angle_increment = math.radians(angle_max_deg - angle_min_deg) / (n - 1)
    ranges = [fill] * n
    return ranges, angle_min, angle_increment


def set_deg(ranges, angle_min, angle_increment, deg, value):
    idx = angle_to_index(math.radians(deg), angle_min, angle_increment, len(ranges))
    ranges[idx] = value


def test_angle_to_index_center_is_near_middle():
    ranges, angle_min, angle_increment = make_scan(n=361, angle_min_deg=-180.0, angle_max_deg=180.0)
    idx = angle_to_index(0.0, angle_min, angle_increment, len(ranges))
    assert 175 <= idx <= 185  # straight ahead should land near the middle index


def test_min_range_in_sector_finds_closest():
    ranges, angle_min, angle_increment = make_scan()
    set_deg(ranges, angle_min, angle_increment, 0.0, 2.0)
    set_deg(ranges, angle_min, angle_increment, 2.0, 0.40)  # closer, still in the front sector
    set_deg(ranges, angle_min, angle_increment, -2.0, 1.5)
    closest = min_range_in_sector(ranges, angle_min, angle_increment,
                                   center_deg=0.0, width_deg=30.0)
    assert closest == 0.40


def test_min_range_in_sector_ignores_inf_and_nan():
    ranges, angle_min, angle_increment = make_scan(fill=float("inf"))
    set_deg(ranges, angle_min, angle_increment, 1.0, float("nan"))
    closest = min_range_in_sector(ranges, angle_min, angle_increment,
                                   center_deg=0.0, width_deg=30.0)
    assert closest is None  # only inf/nan in the sector -> no valid reading


def test_min_range_in_sector_ignores_out_of_range_values():
    ranges, angle_min, angle_increment = make_scan(fill=float("inf"))
    set_deg(ranges, angle_min, angle_increment, 0.0, 0.01)  # closer than range_min
    set_deg(ranges, angle_min, angle_increment, 1.0, 20.0)  # farther than range_max
    closest = min_range_in_sector(ranges, angle_min, angle_increment,
                                   center_deg=0.0, width_deg=30.0,
                                   range_min=0.05, range_max=12.0)
    assert closest is None


def test_min_range_in_sector_outside_sector_is_ignored():
    ranges, angle_min, angle_increment = make_scan(fill=float("inf"))
    set_deg(ranges, angle_min, angle_increment, 90.0, 0.20)  # directly to the side
    closest = min_range_in_sector(ranges, angle_min, angle_increment,
                                   center_deg=0.0, width_deg=30.0)  # narrow front sector
    assert closest is None


def test_empty_ranges_returns_none():
    assert min_range_in_sector([], angle_min=0.0, angle_increment=0.01,
                                center_deg=0.0, width_deg=30.0) is None
