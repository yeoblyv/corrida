"""
Start the RPLIDAR A1M8 driver and the transform for how it is mounted.

Driver settings follow rplidar.launch.py from rplidar_ros 2.1.0, the version
that comes with ROS 2 Jazzy:
https://github.com/ros2-gbp/rplidar_ros-release/blob/release/jazzy/rplidar_ros/2.1.0-4/launch/rplidar.launch.py
(full citation: docs/REFERENCES.md)
"""

import math

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

ROBOT_FRAME = "base_link"
LIDAR_FRAME = "laser"


def generate_launch_description() -> LaunchDescription:
    serial_port = DeclareLaunchArgument(
        "serial_port", default_value="/dev/ttyUSB0", description="Serial device of the lidar."
    )
    # 115200 baud is from the "Communication interface" table of the A1M8 datasheet:
    # https://www.slamtec.com/en/support
    serial_baudrate = DeclareLaunchArgument(
        "serial_baudrate", default_value="115200", description="Baud rate of the lidar."
    )
    # The lidar sits on the robot turned around, its 0 degrees points to the back.
    # A 180 degree yaw in the static transform fixes that for everything that reads tf,
    # so the scan itself does not have to be flipped.
    lidar_yaw = DeclareLaunchArgument(
        "lidar_yaw", default_value=str(math.pi), description="Lidar yaw on the robot, rad."
    )

    driver = Node(
        name="rplidar",
        package="rplidar_ros",
        executable="rplidar_composition",
        output="screen",
        parameters=[
            {
                "serial_port": LaunchConfiguration("serial_port"),
                "serial_baudrate": ParameterValue(
                    LaunchConfiguration("serial_baudrate"), value_type=int
                ),
                "frame_id": LIDAR_FRAME,
                "inverted": False,
                "angle_compensate": True,
            }
        ],
    )

    mount_tf = Node(
        name="lidar_mount_tf",
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=[
            "--frame-id",
            ROBOT_FRAME,
            "--child-frame-id",
            LIDAR_FRAME,
            "--yaw",
            LaunchConfiguration("lidar_yaw"),
        ],
        # The Create 3 tf lives inside the robot namespace (the namespace goes in front of
        # every topic of the robot), so this transform has to go to the same tf_static:
        # https://iroboteducation.github.io/create3_docs/setup/multi-robot/
        remappings=[("/tf_static", "tf_static")],
    )

    return LaunchDescription([serial_port, serial_baudrate, lidar_yaw, driver, mount_tf])
