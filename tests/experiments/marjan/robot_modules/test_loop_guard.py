"""Unit tests for loop_guard.LoopGuard. Run with: pytest tests/"""
from loop_guard import LoopGuard


def test_no_trigger_on_single_pass():
    """Driving through a row of distinct cells once each should never flag a loop."""
    guard = LoopGuard(cell_size=0.25, revisit_limit=3, window_s=20.0, cooldown_s=8.0)
    t = 0.0
    for i in range(20):
        guard.update(x=i * 0.25, y=0.0, t=t)
        assert guard.should_break_loop(t) is False
        t += 0.5


def test_dwelling_in_one_cell_does_not_trigger():
    """Sitting still (or driving slowly) inside one cell for a long time is
    ONE entry, not many -- it must never look like a loop by itself."""
    guard = LoopGuard(cell_size=0.25, revisit_limit=3, window_s=20.0, cooldown_s=8.0)
    t = 0.0
    for _ in range(100):  # 100 ticks at 10 Hz = 10 s stationary
        guard.update(x=1.0, y=1.0, t=t)
        assert guard.should_break_loop(t) is False
        t += 0.1


def test_triggers_on_revisits():
    """Entering the same cell 3 times within the window must flag a loop."""
    guard = LoopGuard(cell_size=0.25, revisit_limit=3, window_s=20.0, cooldown_s=8.0)
    t = 0.0

    def visit_cell_once_then_leave(cell_xy, tt):
        x, y = cell_xy
        guard.update(x=x, y=y, t=tt)
        guard.update(x=x + 5.0, y=y + 5.0, t=tt + 0.5)  # step into a different cell
        return tt + 1.0

    t = visit_cell_once_then_leave((1.0, 1.0), t)
    assert guard.should_break_loop(t) is False  # 1st entry
    t = visit_cell_once_then_leave((1.0, 1.0), t)
    assert guard.should_break_loop(t) is False  # 2nd entry
    t = visit_cell_once_then_leave((1.0, 1.0), t)
    assert guard.should_break_loop(t) is True  # 3rd entry -> loop


def test_old_visits_expire_outside_window():
    """Entries older than window_s don't count towards the limit."""
    guard = LoopGuard(cell_size=0.25, revisit_limit=3, window_s=5.0, cooldown_s=8.0)
    guard.update(x=1.0, y=1.0, t=0.0)
    guard.update(x=9.0, y=9.0, t=0.5)  # leave
    guard.update(x=1.0, y=1.0, t=1.0)  # 2nd entry, still within window of 1st
    guard.update(x=9.0, y=9.0, t=1.5)  # leave

    # Long gap: by the time we re-enter, the first two entries have expired.
    guard.update(x=1.0, y=1.0, t=20.0)  # 3rd entry overall, but only 1 "fresh"
    assert guard.should_break_loop(20.0) is False


def test_cooldown_prevents_immediate_retrigger():
    guard = LoopGuard(cell_size=0.25, revisit_limit=2, window_s=20.0, cooldown_s=8.0)
    guard.update(x=1.0, y=1.0, t=0.0)
    guard.update(x=9.0, y=9.0, t=0.5)
    guard.update(x=1.0, y=1.0, t=1.0)  # 2nd entry -> triggers
    assert guard.should_break_loop(1.0) is True

    # Immediately re-trigger-worthy again, but still inside the 8 s cooldown.
    guard.update(x=9.0, y=9.0, t=1.5)
    guard.update(x=1.0, y=1.0, t=2.0)
    assert guard.should_break_loop(2.0) is False

    # Past the cooldown, a fresh set of revisits can trigger again.
    guard.update(x=9.0, y=9.0, t=10.5)
    guard.update(x=1.0, y=1.0, t=11.0)
    assert guard.should_break_loop(11.0) is True


def test_reset_clears_history():
    guard = LoopGuard(cell_size=0.25, revisit_limit=2, window_s=20.0, cooldown_s=8.0)
    guard.update(x=1.0, y=1.0, t=0.0)
    guard.update(x=9.0, y=9.0, t=0.5)
    guard.update(x=1.0, y=1.0, t=1.0)
    assert guard.should_break_loop(1.0) is True

    guard.reset()
    guard.update(x=1.0, y=1.0, t=1.1)
    assert guard.should_break_loop(1.1) is False
