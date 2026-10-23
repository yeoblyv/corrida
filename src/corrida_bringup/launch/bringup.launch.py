"""Start the robot stack (lidar and slam_toolbox) inside the robot namespace."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import PushRosNamespace, SetRemap


def generate_launch_description() -> LaunchDescription:
    # scripts/env.sh sets ROBOT_NAMESPACE
    namespace = os.environ.get("ROBOT_NAMESPACE", "/robot_10")
    launch_dir = os.path.join(get_package_share_directory("corrida_bringup"), "launch")

    lidar = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(launch_dir, "lidar.launch.py"))
    )
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(launch_dir, "slam.launch.py"))
    )

    stack = GroupAction(
        [
            PushRosNamespace(namespace),
            # the Create 3 publishes its tf inside the namespace, so our nodes use that one:
            # https://iroboteducation.github.io/create3_docs/setup/multi-robot/
            SetRemap("/tf", "tf"),
            SetRemap("/tf_static", "tf_static"),
            lidar,
            slam,
        ]
    )
    return LaunchDescription([stack])
