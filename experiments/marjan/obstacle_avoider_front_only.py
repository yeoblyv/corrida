import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from irobot_create_msgs.msg import IrIntensityVector
from geometry_msgs.msg import Twist

ROBOT = '/robot_10'
STOP_THRESHOLD = 300   
SPEED = 0.1            # metres per second: slow on purpose

class CarefulDriver(Node):
    def __init__(self):
        super().__init__('careful_driver')
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.front = None
        self.create_subscription(IrIntensityVector, ROBOT + '/ir_intensity',
                                 self.ir_callback, qos)
        self.cmd_pub = self.create_publisher(Twist, ROBOT + '/cmd_vel', 10)
        self.create_timer(0.1, self.control_loop)

    def ir_callback(self, msg):
        # keep only the sensors that look forward, and take the closest one
        front_values = [r.value for r in msg.readings if 'front' in r.header.frame_id]
        self.front = max(front_values) if front_values else None

    
    def control_loop(self):
        if self.front is None:
            return
        cmd = Twist()
        if self.front < STOP_THRESHOLD:
            cmd.linear.x = SPEED       # path is clear: drive forward
            cmd.angular.z = 0.0
        else:
            cmd.linear.x = 0.0         # wall ahead: stop moving forward
            cmd.angular.z = 0.5        # and rotate left on the spot (radians per second)
        self.get_logger().info(f'front={self.front}  speed={cmd.linear.x}  turn={cmd.angular.z}')
        self.cmd_pub.publish(cmd)

def main():
    rclpy.init()
    node = CarefulDriver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()