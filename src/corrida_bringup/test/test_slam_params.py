from pathlib import Path

import yaml

PARAMS_FILE = Path(__file__).parents[1] / "config" / "slam_toolbox.yaml"


def test_slam_uses_robot_frames_and_namespaced_scan() -> None:
    params = yaml.safe_load(PARAMS_FILE.read_text())["/**"]["ros__parameters"]
    assert params["base_frame"] == "base_link"
    assert params["odom_frame"] == "odom"
    # an absolute /scan would miss the robot namespace
    assert not params["scan_topic"].startswith("/")
