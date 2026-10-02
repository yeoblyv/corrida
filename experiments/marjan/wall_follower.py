import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from irobot_create_msgs.msg import IrIntensityVector
from geometry_msgs.msg import Twist

ROBOT = '/robot_10'
FRONT_THRESHOLD = 300   # wall ahead
SIDE_THRESHOLD = 200    # wall too close on a side -> measure this and adjust!
SPEED = 0.2             # forward speed (m/s)
TURN_SPEED = 0.5        # turning on the spot (rad/s)
STEER = 0.3             # small correction while driving (rad/s)

class CarefulDriver(Node):
    def __init__(self):
        super().__init__('careful_driver')
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.ir = {}    # remember every sensor by name
        self.create_subscription(IrIntensityVector, ROBOT + '/ir_intensity',
                                 self.ir_callback, qos)
        self.cmd_pub = self.create_publisher(Twist, ROBOT + '/cmd_vel', 10)
        self.create_timer(0.1, self.control_loop)

    def ir_callback(self, msg):
        for r in msg.readings:
            name = r.header.frame_id.replace('ir_intensity_', '')
            self.ir[name] = r.value

    def control_loop(self):
        if not self.ir:
            return
        # NEW: group the 7 sensors into three directions
        front = max(self.ir.get('front_left', 0), self.ir.get('front_center_left', 0),
                    self.ir.get('front_center_right', 0), self.ir.get('front_right', 0))
        left = max(self.ir.get('side_left', 0), self.ir.get('left', 0))
        right = self.ir.get('right', 0)

        cmd = Twist()
        if front > FRONT_THRESHOLD:
            cmd.linear.x = 0.0
            if left > right:                      # left is more blocked -> turn right
                cmd.angular.z = -TURN_SPEED
                action = 'TURN RIGHT'
            else:                                 # otherwise turn left
                cmd.angular.z = TURN_SPEED
                action = 'TURN LEFT'
        elif left > SIDE_THRESHOLD:               # too close to left wall
            cmd.linear.x = SPEED
            cmd.angular.z = -STEER                # steer slightly right
            action = 'steer right'
        elif right > SIDE_THRESHOLD:              # too close to right wall
            cmd.linear.x = SPEED
            cmd.angular.z = STEER                 # steer slightly left
            action = 'steer left'
        else:
            cmd.linear.x = SPEED
            action = 'straight'

        self.get_logger().info(f'front={front} left={left} right={right} -> {action}')
        self.cmd_pub.publish(cmd)

def main():
    rclpy.init()
    node = CarefulDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()