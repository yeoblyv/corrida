"""Tests for the frontier search, on small hand-drawn maps."""

import pytest

from corrida_exploration import frontiers

CORRIDOR = """
    ##########
    #.......??
    #.......??
    #.......??
    ##########
"""

TWO_ROOMS = """
    #######
    #..#..#
    #..#..#
    #######
"""

ONE_UNKNOWN_CELL = """
    #######
    #.....#
    #..?..#
    #.....#
    #######
"""

OPEN_ROOM_BEHIND_A_WALL = """
    #####???
    #...#...
    #...#...
    #####???
"""

MAP_ENDS_IN_FREE_SPACE = """
    ####
    #...
    #...
    ####
"""

FREE_SPACE_AT_THE_FIRST_CELLS = """
    ...#
    ...#
    ####
"""

TWO_OPENINGS = """
    ?????????
    ##...####
    #.......?
    #.......?
    #.......?
    #########
"""

LONG_WAY_AROUND = """
    ###########
    ?.........#
    #########.#
    #.........#
    #.........#
    #?????????#
"""


def grid_from(drawing: str) -> list[list[int]]:
    # '.' is free, '?' unknown, '#' a wall. The first line of a drawing is row 0
    values = {".": 0, "?": -1, "#": 100}
    grid = []
    for line in drawing.split():
        grid.append([values[char] for char in line])
    return grid


def test_to_rows_cuts_the_data_at_the_width():
    assert frontiers.to_rows([1, 2, 3, 4, 5, 6], 3) == [[1, 2, 3], [4, 5, 6]]


def test_world_point_to_cell_and_back():
    origin = (-1.0, -2.0)
    assert frontiers.world_to_cell((-0.98, -1.93), origin, 0.05) == (0, 1)
    assert frontiers.cell_to_world((0, 1), origin, 0.05) == pytest.approx((-0.975, -1.925))
    # a point just left of and below the origin is outside the map, not in cell (0, 0)
    assert frontiers.world_to_cell((-1.01, -2.01), origin, 0.05) == (-1, -1)


def test_nearest_free_cell():
    grid = grid_from(ONE_UNKNOWN_CELL)
    assert frontiers.nearest_free_cell(grid, (1, 1), 2) == (1, 1)
    # standing on the unknown cell in the middle, one of the cells beside it is taken
    assert frontiers.nearest_free_cell(grid, (3, 2), 2) in [(3, 1), (2, 2), (4, 2), (3, 3)]
    assert frontiers.nearest_free_cell(grid, (0, 0), 0) is None
    assert frontiers.nearest_free_cell(grid, (50, 50), 2) is None
    # next to the border of the map, it must not look at cells on the other side
    assert frontiers.nearest_free_cell(grid_from(MAP_ENDS_IN_FREE_SPACE), (0, 0), 1) == (1, 1)


def test_reachable_cells_stop_at_walls():
    steps = frontiers.reachable_cells(grid_from(TWO_ROOMS), (1, 1))
    assert sorted(steps) == [(1, 1), (1, 2), (2, 1), (2, 2)]
    assert steps[(2, 2)] == 2


def test_frontier_at_the_open_end_of_a_corridor():
    grid = grid_from(CORRIDOR)
    steps = frontiers.reachable_cells(grid, (1, 2))
    found = frontiers.find_frontiers(grid, steps, 3)
    assert found == [[(7, 1), (7, 2), (7, 3)]]
    assert frontiers.nearest_goal(found, steps, [], 0) == (7, 2)
    assert steps[(7, 2)] == 6


def test_short_frontiers_are_dropped():
    grid = grid_from(CORRIDOR)
    steps = frontiers.reachable_cells(grid, (1, 2))
    assert frontiers.find_frontiers(grid, steps, 4) == []
    assert frontiers.nearest_goal([], steps, [], 0) is None


def test_one_unknown_cell_between_laser_beams_is_no_frontier():
    grid = grid_from(ONE_UNKNOWN_CELL)
    steps = frontiers.reachable_cells(grid, (1, 1))
    # the four cells around it do form a group, but it is shorter than the minimum
    assert frontiers.find_frontiers(grid, steps, 1) == [[(2, 2), (3, 1), (3, 3), (4, 2)]]
    assert frontiers.find_frontiers(grid, steps, 5) == []


def test_frontier_behind_a_wall_is_not_found():
    grid = grid_from(OPEN_ROOM_BEHIND_A_WALL)
    steps = frontiers.reachable_cells(grid, (1, 1))
    assert frontiers.find_frontiers(grid, steps, 1) == []


def test_the_edge_of_the_map_counts_as_unknown():
    grid = grid_from(MAP_ENDS_IN_FREE_SPACE)
    steps = frontiers.reachable_cells(grid, (1, 1))
    assert frontiers.find_frontiers(grid, steps, 1) == [[(3, 1), (3, 2)]]
    # the same at row 0 and column 0, where an index below zero would wrap around
    grid = grid_from(FREE_SPACE_AT_THE_FIRST_CELLS)
    steps = frontiers.reachable_cells(grid, (1, 1))
    assert frontiers.find_frontiers(grid, steps, 1) == [[(0, 0), (0, 1), (1, 0), (2, 0)]]


def test_middle_cell_is_a_cell_of_the_frontier():
    u_shape = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0)]
    # the centre of this shape is (1.0, 1.1), which is not one of its cells
    assert frontiers.middle_cell(u_shape) == (1, 2)


def test_nearest_goal_is_the_closest_of_two_frontiers():
    grid = grid_from(TWO_OPENINGS)
    steps = frontiers.reachable_cells(grid, (1, 3))
    found = frontiers.find_frontiers(grid, steps, 3)
    assert len(found) == 2
    assert frontiers.nearest_goal(found, steps, [], 0) == (3, 1)


def test_blocked_frontiers_are_skipped():
    grid = grid_from(TWO_OPENINGS)
    steps = frontiers.reachable_cells(grid, (1, 3))
    found = frontiers.find_frontiers(grid, steps, 3)
    # a goal that was reached or given up is blocked, a cell next to it blocks as well
    assert frontiers.nearest_goal(found, steps, [(3, 1)], 0) == (7, 3)
    assert frontiers.nearest_goal(found, steps, [(2, 1)], 1) == (7, 3)
    assert frontiers.nearest_goal(found, steps, [(2, 1)], 0) == (3, 1)
    assert frontiers.nearest_goal(found, steps, [(3, 1), (7, 3)], 0) is None


def test_distance_is_counted_along_the_way_around_walls():
    grid = grid_from(LONG_WAY_AROUND)
    steps = frontiers.reachable_cells(grid, (1, 3))
    found = frontiers.find_frontiers(grid, steps, 1)
    # the frontier at (1, 1) is 2 cells away in a straight line but 18 steps to drive
    assert steps[(1, 1)] == 18
    assert frontiers.nearest_goal(found, steps, [], 0) == (5, 4)
