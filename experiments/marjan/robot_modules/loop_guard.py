"""LoopGuard: notices when the robot keeps coming back to the same place.

Pure Python, no ROS imports -- so it can be unit-tested without rclpy or a
robot (see tests/experiments/marjan/robot_modules/test_loop_guard.py). A
behaviour feeds it (x, y) positions from odometry every control tick and
asks should_break_loop(); when the same patch of ground has been *entered*
too many times inside a short window, that is the classic failure mode of a
pure left-hand (or right-hand) rule on a maze with loops (see
robot_modules/README.md's "Demo tip": restart with the other side) -- this
notices it automatically instead of needing someone to restart the node.

Only ENTERING a cell counts as a visit, not every tick spent inside it --
otherwise driving slowly, or stopping, in one spot would look like a loop
after a couple of seconds. See test_dwelling_in_one_cell_does_not_trigger.
"""
from collections import defaultdict


class LoopGuard:
    """Flags a loop when the same grid cell is re-entered too often, too soon."""

    def __init__(self, cell_size=0.25, revisit_limit=3, window_s=20.0, cooldown_s=8.0):
        """
        cell_size: metres per grid cell (position is bucketed into cells this
            big). Start around the width of the maze corridor; calibrate like
            the other settings in robot_modules/README.md.
        revisit_limit: how many times a cell may be *entered* again within
            window_s before it counts as a loop.
        window_s: only entries within this many seconds of each other count
            towards revisit_limit -- older entries "expire" so a cell seen
            once near the start of an 8-minute run doesn't count against a
            pass near the end.
        cooldown_s: once a loop is flagged, stay quiet for this long before
            flagging again, so recovering from one loop doesn't immediately
            get treated as a second loop.
        """
        self.cell_size = cell_size
        self.revisit_limit = revisit_limit
        self.window_s = window_s
        self.cooldown_s = cooldown_s
        self._entries = defaultdict(list)  # cell -> [entry timestamps]
        self._current_cell = None
        self._last_trigger_t = None

    def _cell(self, x, y):
        return (round(x / self.cell_size), round(y / self.cell_size))

    def update(self, x, y, t):
        """Record a position at time t (seconds, one consistent clock).

        Only counts as a new "entry" if this cell is different from the one
        we were in last tick -- staying inside one cell, however long,
        is one entry, not many.
        """
        cell = self._cell(x, y)
        if cell == self._current_cell:
            return
        self._current_cell = cell
        entries = self._entries[cell]
        entries.append(t)
        cutoff = t - self.window_s
        while entries and entries[0] < cutoff:
            entries.pop(0)

    def should_break_loop(self, t):
        """True if some cell has been re-entered revisit_limit+ times recently
        and we are not still in the cooldown from the last time this fired."""
        if self._last_trigger_t is not None and t - self._last_trigger_t < self.cooldown_s:
            return False
        for entries in self._entries.values():
            if len(entries) >= self.revisit_limit:
                self._last_trigger_t = t
                return True
        return False

    def reset(self):
        """Forget all history (e.g. after a manual restart between rounds)."""
        self._entries.clear()
        self._current_cell = None
        self._last_trigger_t = None
