"""
Top-level launch file for the Corrida robot stack.

Every other package's launch file gets included from here, inside one group
that pushes the robot namespace, so all nodes end up under a single prefix
(default ``/robot_10``, taken from ``$ROBOT_NAMESPACE`` set by
``scripts/env.sh``). One entry point means the same command starts the stack
on the Raspberry Pi, in a VM or in simulation.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import EnvironmentVariable, LaunchConfiguration
from launch_ros.actions import PushRosNamespace


def generate_launch_description() -> LaunchDescription:
    """Declare the ``namespace`` argument and the namespaced group of actions."""
    namespace = DeclareLaunchArgument(
        "namespace",
        default_value=EnvironmentVariable("ROBOT_NAMESPACE", default_value="/robot_10"),
        description="Namespace prepended to every node and topic of the robot stack.",
    )
    stack = GroupAction([PushRosNamespace(LaunchConfiguration("namespace"))])
    return LaunchDescription([namespace, stack])
