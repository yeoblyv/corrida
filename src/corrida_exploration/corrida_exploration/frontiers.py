"""
Find frontiers in a SLAM map: the places where free space borders unknown space.

Exploring a map by driving to its frontiers is from Yamauchi (1997),
https://doi.org/10.1109/CIRA.1997.613851 (full citation: docs/REFERENCES.md).
No ROS in this file, so it is tested with pytest in tests/.
"""

import math
from collections import deque

# values of a map cell, slam_toolbox only writes -1, 0 and 100 (a wall)
FREE = 0
UNKNOWN = -1
OCCUPIED = 100

Cell = tuple[int, int]  # (column, row) of a map cell
Grid = list[list[int]]  # grid[row][column]

SIDES = [(1, 0), (-1, 0), (0, 1), (0, -1)]
CORNERS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def to_rows(data: list[int], width: int) -> Grid:
    # nav_msgs/OccupancyGrid stores the map row by row, starting at the map origin
    return [data[start : start + width] for start in range(0, len(data), width)]


def world_to_cell(
    point: tuple[float, float], origin: tuple[float, float], resolution: float
) -> Cell:
    """Return the cell that contains a map point (x, y in m)."""
    column = math.floor((point[0] - origin[0]) / resolution)
    row = math.floor((point[1] - origin[1]) / resolution)
    return column, row


def cell_to_world(
    cell: Cell, origin: tuple[float, float], resolution: float
) -> tuple[float, float]:
    x = origin[0] + (cell[0] + 0.5) * resolution
    y = origin[1] + (cell[1] + 0.5) * resolution
    return x, y


def neighbours(cell: Cell, grid: Grid, offsets: list[Cell]) -> list[Cell]:
    inside = []
    for d_column, d_row in offsets:
        column, row = cell[0] + d_column, cell[1] + d_row
        if 0 <= row < len(grid) and 0 <= column < len(grid[0]):
            inside.append((column, row))
    return inside


def nearest_free_cell(grid: Grid, cell: Cell, reach: int) -> Cell | None:
    """Return the free cell closest to a cell, or None if all cells within reach are taken."""
    free = []
    for row in range(cell[1] - reach, cell[1] + reach + 1):
        for column in range(cell[0] - reach, cell[0] + reach + 1):
            inside = 0 <= row < len(grid) and 0 <= column < len(grid[0])
            if inside and grid[row][column] == FREE:
                free.append((column, row))
    if not free:
        return None
    return min(free, key=lambda other: math.dist(other, cell))


def reachable_cells(grid: Grid, start: Cell) -> dict[Cell, int]:
    """Return every free cell that connects to start, with its distance in steps."""
    # the search starts at the robot and spreads through free cells, so we only find
    # frontiers the robot can get to. Same idea as the search in explore_lite:
    # https://github.com/robo-friends/m-explore-ros2/blob/main/explore/src/frontier_search.cpp
    steps = {start: 0}
    queue = deque([start])
    while queue:
        cell = queue.popleft()
        for other in neighbours(cell, grid, SIDES):
            if other not in steps and grid[other[1]][other[0]] == FREE:
                steps[other] = steps[cell] + 1
                queue.append(other)
    return steps


def touches_unknown(cell: Cell, grid: Grid) -> bool:
    sides = neighbours(cell, grid, SIDES)
    # a cell on the edge of the map has the unmapped world next to it
    if len(sides) < len(SIDES):
        return True
    return any(grid[row][column] == UNKNOWN for column, row in sides)


def find_frontiers(grid: Grid, steps: dict[Cell, int], min_cells: int) -> list[list[Cell]]:
    """Return the frontiers the robot can reach, each one as a list of its cells."""
    # a frontier cell is a free cell next to unknown space (Yamauchi, 1997)
    edge = {cell for cell in steps if touches_unknown(cell, grid)}
    frontiers = []
    while edge:
        # group the cells that touch each other, also at the corners
        group = [edge.pop()]
        queue = deque(group)
        while queue:
            for other in neighbours(queue.popleft(), grid, SIDES + CORNERS):
                if other in edge:
                    edge.remove(other)
                    group.append(other)
                    queue.append(other)
        # a short one is a gap between laser beams or an opening the robot doesn't fit in
        if len(group) >= min_cells:
            frontiers.append(sorted(group))
    return sorted(frontiers)


def clearance(grid: Grid, limit: int) -> dict[Cell, int]:
    """Return how many cells away the nearest wall is, for cells up to `limit` cells from one."""
    # one search that starts from all wall cells at once and grows outwards. With 8
    # neighbours a diagonal step counts as one cell, a bit less than the real distance
    distance = {}
    queue = deque()
    for row, values in enumerate(grid):
        for column, value in enumerate(values):
            if value == OCCUPIED:
                distance[(column, row)] = 0
                queue.append((column, row))
    while queue:
        cell = queue.popleft()
        if distance[cell] == limit:
            continue
        for other in neighbours(cell, grid, SIDES + CORNERS):
            if other not in distance:
                distance[other] = distance[cell] + 1
                queue.append(other)
    return distance


def goal_cell(cells: list[Cell], clear: dict[Cell, int], limit: int) -> Cell:
    """Return the frontier cell furthest from the walls (up to limit), the most central on a tie."""
    centre = (
        sum(cell[0] for cell in cells) / len(cells),
        sum(cell[1] for cell in cells) / len(cells),
    )
    # a cell of the frontier and not its centre, a bent frontier has its centre in a wall.
    # Cells missing from `clear` are more than `limit` cells from any wall
    return max(cells, key=lambda cell: (clear.get(cell, limit), -math.dist(cell, centre)))


def is_blocked(cell: Cell, blocked: list[Cell], radius: int) -> bool:
    for other in blocked:
        if math.dist(cell, other) <= radius:
            return True
    return False


def usable_cells(
    cells: list[Cell],
    clear: dict[Cell, int],
    limit: int,
    min_clear: int,
    blocked: list[Cell],
    radius: int,
) -> list[Cell]:
    """Return the cells that are far enough from walls and from goals tried before."""
    usable = []
    for cell in cells:
        if clear.get(cell, limit) >= min_clear and not is_blocked(cell, blocked, radius):
            usable.append(cell)
    return usable


def best_goal(goals: list[Cell], steps: dict[Cell, int], finish: Cell | None = None) -> Cell | None:
    """Return the goal that is the fewest steps away, or None if there are no goals."""
    if not goals:
        return None
    if finish is None:
        return min(goals, key=lambda goal: steps[goal])
    # plus the straight distance from the goal to the finish, so the robot explores in the
    # direction of the finish instead of the nearest corner (like the cost of a node in A*)
    return min(goals, key=lambda goal: steps[goal] + math.dist(goal, finish))
