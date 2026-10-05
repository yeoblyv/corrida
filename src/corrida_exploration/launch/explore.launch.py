"""Start the explorer node inside the robot namespace. The bringup must already be running."""

import os

from launch import LaunchDescription
from launch.actions import GroupAction
from launch_ros.actions import Node, PushRosNamespace, SetRemap


def generate_launch_description() -> LaunchDescription:
    # scripts/env.sh sets ROBOT_NAMESPACE
    namespace = os.environ.get("ROBOT_NAMESPACE", "/robot_10")
    explorer = Node(package="corrida_exploration", executable="explorer", output="screen")

    group = GroupAction(
        [
            PushRosNamespace(namespace),
            # same remaps as in bringup.launch.py, the explorer reads the robot's tf too
            SetRemap("/tf", "tf"),
            SetRemap("/tf_static", "tf_static"),
            explorer,
        ]
    )
    return LaunchDescription([group])
