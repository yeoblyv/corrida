"""
Run slam_toolbox online async mapping inside the robot namespace.

The configure and activate steps follow online_async_launch.py from
slam_toolbox 2.8.4:
https://github.com/SteveMacenski/slam_toolbox/blob/2.8.4/launch/online_async_launch.py
(full citation: docs/REFERENCES.md)
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, LogInfo, RegisterEventHandler
from launch.events import matches_action
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from launch_ros.substitutions import FindPackageShare
from lifecycle_msgs.msg import Transition

# The Create 3 publishes tf inside its namespace. Plain /tf is the global tree,
# which has no odom from the robot, so slam would drop every scan.
TF_REMAPPINGS = [("/tf", "tf"), ("/tf_static", "tf_static")]


def generate_launch_description() -> LaunchDescription:
    params_file = DeclareLaunchArgument(
        "slam_params_file",
        default_value=PathJoinSubstitution(
            [FindPackageShare("corrida_bringup"), "config", "slam_toolbox.yaml"]
        ),
        description="Parameter file for slam_toolbox.",
    )

    # LifecycleNode needs a namespace argument, the real one is pushed by bringup.launch.py
    slam = LifecycleNode(
        package="slam_toolbox",
        executable="async_slam_toolbox_node",
        name="slam_toolbox",
        namespace="",
        output="screen",
        parameters=[LaunchConfiguration("slam_params_file"), {"use_sim_time": False}],
        remappings=TF_REMAPPINGS,
    )

    # slam_toolbox is a lifecycle node, it only subscribes to the scan and publishes
    # the map after it has been configured and then activated
    configure = EmitEvent(
        event=ChangeState(
            lifecycle_node_matcher=matches_action(slam),
            transition_id=Transition.TRANSITION_CONFIGURE,
        )
    )
    activate = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=slam,
            start_state="configuring",
            goal_state="inactive",
            entities=[
                LogInfo(msg="slam_toolbox configured, activating"),
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(slam),
                        transition_id=Transition.TRANSITION_ACTIVATE,
                    )
                ),
            ],
        )
    )

    return LaunchDescription([params_file, slam, configure, activate])
