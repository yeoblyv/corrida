"""
Find the direction of the walls in a lidar scan.

The maze walls meet at about 90 degrees, so modulo 90 they all point the same way.
Multiplying an angle by 4 turns 0, 90, 180 and 270 degrees into the same angle, after
that a normal average of directions works. No ROS in here, tested with pytest in tests/.
"""

import math

Point = tuple[float, float]

# points in one straight piece of wall
WINDOW = 7
# m, neighbouring points further apart than this are not on the same wall
MAX_GAP = 0.08
# a piece is straight when it is at least this many times longer than wide
MIN_STRAIGHTNESS = 10.0
# deg, pieces this far from the first estimate are left out of the second one
KEEP_WITHIN = 10.0


def scan_points(
    ranges: list[float], angle_min: float, angle_increment: float, max_range: float
) -> list[Point]:
    """Turn lidar ranges into (x, y) points in the lidar frame, leaving out bad readings."""
    points = []
    for i, r in enumerate(ranges):
        if math.isfinite(r) and 0.0 < r <= max_range:
            angle = angle_min + i * angle_increment
            points.append((r * math.cos(angle), r * math.sin(angle)))
    return points


def wall_pieces(points: list[Point]) -> list[tuple[float, float]]:
    """Return (direction in rad, length in m) of the short straight wall pieces in a scan."""
    pieces = []
    for start in range(0, len(points) - WINDOW + 1, WINDOW // 2):
        window = points[start : start + WINDOW]
        if any(math.dist(a, b) > MAX_GAP for a, b in zip(window, window[1:])):
            continue  # a jump between two walls, or into a doorway
        n = len(window)
        mx = sum(p[0] for p in window) / n
        my = sum(p[1] for p in window) / n
        sxx = sum((p[0] - mx) ** 2 for p in window)
        syy = sum((p[1] - my) ** 2 for p in window)
        sxy = sum((p[0] - mx) * (p[1] - my) for p in window)
        # direction of the line through the points: the principal axis of the 2x2 covariance,
        # same formula as the orientation in https://en.wikipedia.org/wiki/Image_moment
        direction = 0.5 * math.atan2(2 * sxy, sxx - syy)
        # spread along and across that line (the two eigenvalues, see the same page), to drop
        # corners and round things
        along = (sxx + syy) / 2 + math.hypot((sxx - syy) / 2, sxy)
        across = (sxx + syy) / 2 - math.hypot((sxx - syy) / 2, sxy)
        if across > 0 and along / across < MIN_STRAIGHTNESS**2:
            continue
        pieces.append((direction, math.dist(window[0], window[-1])))
    return pieces


def mean_direction_mod_90(pieces: list[tuple[float, float]]) -> float:
    """Average direction modulo 90 degrees, weighted by length, in (-45, 45] deg as rad."""
    # a circular mean of the angle times 4: https://en.wikipedia.org/wiki/Circular_mean
    c = sum(length * math.cos(4 * direction) for direction, length in pieces)
    s = sum(length * math.sin(4 * direction) for direction, length in pieces)
    return math.atan2(s, c) / 4


def difference_mod_90(a: float, b: float) -> float:
    """Return a - b modulo 90 degrees, in (-45, 45] deg, as rad."""
    d = (a - b) % (math.pi / 2)
    return d - math.pi / 2 if d > math.pi / 4 else d


def wall_angle(points: list[Point]) -> tuple[float, float]:
    """Wall direction modulo 90 deg (rad, in (-45, 45] deg) and how sure that is."""
    pieces = wall_pieces(points)
    total = sum(length for _, length in pieces)
    if total == 0.0:
        return 0.0, 0.0
    first = mean_direction_mod_90(pieces)
    # second pass without the pieces that don't fit, so clutter can't pull the result
    close = [p for p in pieces if abs(difference_mod_90(p[0], first)) <= math.radians(KEEP_WITHIN)]
    if not close:
        return first, 0.0
    # share of straight wall length within KEEP_WITHIN deg of the direction: 1.0 is a clean
    # maze, about 0.2 is random clutter
    return mean_direction_mod_90(close), sum(length for _, length in close) / total
