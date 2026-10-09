"""Send the robot's odometry on again with reliable delivery, so Nav2 receives it."""

import rclpy
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data


class OdomRelay(Node):
    def __init__(self) -> None:
        super().__init__("odom_relay")
        # the Create 3 publishes odom best effort, Nav2 subscribes reliable, they never connect:
        # https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html
        self.reliable_pub = self.create_publisher(Odometry, "odom_reliable", 10)
        self.create_subscription(
            Odometry, "odom", self.reliable_pub.publish, qos_profile_sensor_data
        )


def main() -> None:
    rclpy.init()
    node = OdomRelay()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
