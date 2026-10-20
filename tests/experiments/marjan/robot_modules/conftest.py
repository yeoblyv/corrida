"""Makes experiments/marjan/robot_modules importable from these tests,
without installing it as a package or changing the repo's pytest config.
"""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SRC = _REPO_ROOT / "experiments" / "marjan" / "robot_modules"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
