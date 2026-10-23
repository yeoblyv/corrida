import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    params = os.path.join(
        get_package_share_directory("project_tests"),
        "config", "odometry_converter_parameters.yaml")

    return LaunchDescription([
        Node(
            package="project_tests",
            executable="odometry_converter",   # name from console_scripts
            name="odometry_converter",         # must match the YAML's top key
            parameters=[params],
            output="screen",                   # show the node's log in the terminal
        ),
        # second node goes here once it exists, same pattern, e.g.:
        # Node(package="project_tests", executable="maze_solver", name="maze_solver"),
    ])