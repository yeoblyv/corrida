"""Run slam_toolbox (online async mapping) with our config."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description() -> LaunchDescription:
    config = os.path.join(
        get_package_share_directory("corrida_bringup"), "config", "slam_toolbox.yaml"
    )
    # slam_toolbox's own launch file, it also configures and activates the node
    slam_launch = os.path.join(
        get_package_share_directory("slam_toolbox"), "launch", "online_async_launch.py"
    )
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_launch),
        # that launch file uses sim time by default, the robot runs on real time
        launch_arguments={"slam_params_file": config, "use_sim_time": "false"}.items(),
    )
    return LaunchDescription([slam])
