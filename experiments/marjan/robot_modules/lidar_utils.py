"""Small pure-Python helpers for reading a LaserScan's ranges array.

No ROS imports -- so these can be unit-tested without rclpy, a robot, or a
LiDAR (see tests/experiments/marjan/robot_modules/test_lidar_utils.py). A ROS
node passes in the plain parts of a sensor_msgs/msg/LaserScan message
(msg.ranges, msg.angle_min, msg.angle_increment) plus a direction and width
in degrees, and gets back the closest real reading in that direction, or
None if there wasn't one.

0 degrees = straight ahead (angle_min/angle_increment are in radians, same
convention ROS uses); positive degrees = to the left, matching angular.z.
"""
import math


def angle_to_index(angle_rad, angle_min, angle_increment, n_ranges):
    """Index into ranges[] closest to angle_rad."""
    if angle_increment == 0 or n_ranges == 0:
        return 0
    idx = round((angle_rad - angle_min) / angle_increment)
    return max(0, min(n_ranges - 1, idx))


def min_range_in_sector(ranges, angle_min, angle_increment, center_deg, width_deg,
                         range_min=0.05, range_max=12.0):
    """Closest valid reading within [center_deg - width_deg/2, center_deg + width_deg/2].

    Ignores readings that are None, NaN, inf, or outside [range_min,
    range_max] -- a raw LaserScan is full of those for "nothing in range" or
    a bad return (this is normal, not a sensor fault).

    Returns None if every reading in the sector was invalid (e.g. the LiDAR
    isn't publishing yet, the sector is empty, or nothing is in range) --
    callers should treat None as "no information", not "nothing there".
    """
    n = len(ranges)
    if n == 0:
        return None
    center_rad = math.radians(center_deg)
    half_width_rad = math.radians(width_deg) / 2.0
    lo = angle_to_index(center_rad - half_width_rad, angle_min, angle_increment, n)
    hi = angle_to_index(center_rad + half_width_rad, angle_min, angle_increment, n)
    if lo > hi:
        lo, hi = hi, lo

    best = None
    for r in ranges[lo:hi + 1]:
        if r is None:
            continue
        if math.isnan(r) or math.isinf(r):
            continue
        if r < range_min or r > range_max:
            continue
        if best is None or r < best:
            best = r
    return best
