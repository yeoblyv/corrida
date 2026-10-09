"""Start the explorer inside the robot namespace. The bringup and nav2.launch.py must be running."""

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace, SetRemap
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    # scripts/env.sh sets ROBOT_NAMESPACE
    namespace = os.environ.get("ROBOT_NAMESPACE", "/robot_10")
    # drive:=true makes the robot move, without it the goals are only shown in Foxglove
    drive = DeclareLaunchArgument("drive", default_value="false")
    explorer = Node(
        package="corrida_exploration",
        executable="explorer",
        parameters=[{"drive": ParameterValue(LaunchConfiguration("drive"), value_type=bool)}],
        output="screen",
    )

    group = GroupAction(
        [
            PushRosNamespace(namespace),
            # same remaps as in bringup.launch.py, the explorer reads the robot's tf too
            SetRemap("/tf", "tf"),
            SetRemap("/tf_static", "tf_static"),
            explorer,
        ]
    )
    return LaunchDescription([drive, group])
