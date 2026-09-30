"""The bring-up launch file must load and expose the robot namespace argument."""

import importlib.util
from pathlib import Path

from launch.actions import DeclareLaunchArgument, GroupAction

LAUNCH_FILE = Path(__file__).parents[1] / "launch" / "bringup.launch.py"


def _load_description():
    spec = importlib.util.spec_from_file_location("bringup_launch", LAUNCH_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate_launch_description()


def test_declares_namespace_argument() -> None:
    entities = _load_description().entities
    names = [e.name for e in entities if isinstance(e, DeclareLaunchArgument)]
    assert names == ["namespace"]


def test_has_namespaced_group() -> None:
    entities = _load_description().entities
    assert any(isinstance(e, GroupAction) for e in entities)
