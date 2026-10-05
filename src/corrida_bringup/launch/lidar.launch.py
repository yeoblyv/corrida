"""
Start the RPLIDAR A1M8 driver and the transform for how it is mounted.

Driver settings are from rplidar.launch.py of rplidar_ros 2.1.0 (ROS 2 Jazzy):
https://github.com/ros2-gbp/rplidar_ros-release/blob/release/jazzy/rplidar_ros/2.1.0-4/launch/rplidar.launch.py
(full citation: docs/REFERENCES.md)
"""

import math

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    driver = Node(
        name="rplidar",
        package="rplidar_ros",
        executable="rplidar_composition",
        output="screen",
        parameters=[
            {
                "serial_port": "/dev/ttyUSB0",
                # A1M8 datasheet, "Communication interface": https://www.slamtec.com/en/support
                "serial_baudrate": 115200,
                "frame_id": "laser",
                "inverted": False,
                "angle_compensate": True,
            }
        ],
    )

    # the lidar is mounted backwards (its 0 deg points to the back of the robot),
    # so the transform has a 180 deg yaw
    mount_tf = Node(
        name="lidar_mount_tf",
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=["--frame-id", "base_link", "--child-frame-id", "laser", "--yaw", str(math.pi)],
    )

    return LaunchDescription([driver, mount_tf])
