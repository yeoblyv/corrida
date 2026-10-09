"""
Start Nav2 inside the robot namespace, for driving to goals while slam_toolbox maps.

Nothing moves until a node sends a goal. The bringup (lidar and slam) must be running.
Servers and wiring are from navigation_launch.py of nav2_bringup 1.3.13 and from the
TurtleBot 4 (same robot base and lidar):
https://github.com/ros-navigation/navigation2/blob/1.3.13/nav2_bringup/launch/navigation_launch.py
https://github.com/turtlebot/turtlebot4/blob/jazzy/turtlebot4_navigation/launch/nav2.launch.py
(full citations: docs/REFERENCES.md)
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import GroupAction
from launch_ros.actions import Node, PushRosNamespace, SetRemap

# package, node name (also the key in nav2.yaml)
SERVERS = [
    ("nav2_controller", "controller_server"),
    ("nav2_planner", "planner_server"),
    ("nav2_behaviors", "behavior_server"),
    ("nav2_bt_navigator", "bt_navigator"),
    ("nav2_collision_monitor", "collision_monitor"),
]


def generate_launch_description() -> LaunchDescription:
    # scripts/env.sh sets ROBOT_NAMESPACE
    namespace = os.environ.get("ROBOT_NAMESPACE", "/robot_10")
    config_dir = os.path.join(get_package_share_directory("corrida_bringup"), "config")
    params = os.path.join(config_dir, "nav2.yaml")
    behavior_tree = os.path.join(config_dir, "navigate_to_pose.xml")

    servers = []
    for package, name in SERVERS:
        # controller and behaviors publish to cmd_vel_nav, the collision monitor checks
        # those against the lidar and publishes the final cmd_vel
        remaps = [("cmd_vel", "cmd_vel_nav")] if name != "collision_monitor" else []
        extra = [{"default_nav_to_pose_bt_xml": behavior_tree}] if name == "bt_navigator" else []
        servers.append(
            Node(
                package=package,
                executable=name,
                name=name,
                parameters=[params] + extra,
                remappings=remaps,
                output="screen",
            )
        )

    # configures and activates the servers above, in this order
    manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_navigation",
        parameters=[{"autostart": True, "node_names": [name for _, name in SERVERS]}],
        output="screen",
    )
    odom_relay = Node(package="corrida_bringup", executable="odom_relay", output="screen")

    group = GroupAction(
        [
            PushRosNamespace(namespace),
            SetRemap("/tf", "tf"),
            SetRemap("/tf_static", "tf_static"),
            # the costmaps live one level deeper (<ns>/local_costmap), so their scan has to
            # point at the robot's, like the TurtleBot 4 does
            SetRemap(namespace + "/local_costmap/scan", namespace + "/scan"),
            SetRemap(namespace + "/global_costmap/scan", namespace + "/scan"),
            odom_relay,
            *servers,
            manager,
        ]
    )
    return LaunchDescription([group])
