"""ROS 2 node that publishes Create 3 bumper detections."""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from std_msgs.msg import String
from irobot_create_msgs.msg import HazardDetectionVector

from corrida_perception.bumper_logic import get_bumper_names


class BumperNode(Node):
    """Translate Create 3 hazard detections into bumper-name messages."""

    def __init__(self):
        super().__init__("bumper_node")

        self.publisher = self.create_publisher(
            String,
            "/robot_10/bumper",
            10,
        )

        # The Create 3 publishes hazard_detection as BEST_EFFORT. A default
        # (RELIABLE) subscription would never connect to it.
        sensor_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT,
        )

        self.subscription = self.create_subscription(
            HazardDetectionVector,
            "/robot_10/hazard_detection",
            self.hazard_callback,
            sensor_qos,
        )

        self.get_logger().info(
            "Bumper node started. Listening for bumper detections."
        )

    def hazard_callback(self, message):
        """Publish the name of each bumper detected in the incoming message."""
        for bumper_name in get_bumper_names(message):
            output = String()
            output.data = bumper_name
            self.publisher.publish(output)
            self.get_logger().info(f"Bumper detected: {bumper_name}")


def main(args=None):
    """Start the bumper node."""
    rclpy.init(args=args)
    node = BumperNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()