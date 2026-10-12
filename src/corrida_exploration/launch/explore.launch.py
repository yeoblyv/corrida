"""Start the explorer inside the robot namespace. The bringup and nav2.launch.py must be running."""

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.parameter_descriptions import ParameterValue

# name, default and what it does
ARGUMENTS = [
    ("drive", "false", "true makes the robot move, without it the goals are only shown"),
    ("align", "true", "turn parallel to the walls at the start, so the map is straight"),
    ("finish_distance", "0.0", "m from the start to the finish, 0 means just explore"),
    ("finish_angle", "0.0", "deg from where the robot faces at the start, + is left"),
    ("max_minutes", "10.0", "stop after this long"),
]
TYPES = {"drive": bool, "align": bool}


def generate_launch_description() -> LaunchDescription:
    # scripts/env.sh sets ROBOT_NAMESPACE
    namespace = os.environ.get("ROBOT_NAMESPACE", "/robot_10")
    arguments = [DeclareLaunchArgument(n, default_value=d, description=t) for n, d, t in ARGUMENTS]
    parameters = {
        name: ParameterValue(LaunchConfiguration(name), value_type=TYPES.get(name, float))
        for name, _, _ in ARGUMENTS
    }
    explorer = Node(
        package="corrida_exploration",
        executable="explorer",
        parameters=[parameters],
        output="screen",
    )

    group = GroupAction([PushRosNamespace(namespace), explorer])
    return LaunchDescription([*arguments, group])
