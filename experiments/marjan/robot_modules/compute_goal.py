#!/usr/bin/env python3
"""Read current odom position + heading once and print the --goal x y
for a destination that is <forward> metres forward and <left> metres
left of wherever the robot is facing RIGHT NOW (not the original odom
+x axis). For "right" instead of left, pass a negative number.

Usage: python3 compute_goal.py <forward_m> <left_m>
Example (3 m forward, 1 m RIGHT):  python3 compute_goal.py 3 -1
"""
import sys
import math
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry


def yaw_from_quaternion(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


class OnceOdomReader(Node):
    def __init__(self, forward, left):
        super().__init__('compute_goal_once')
        self.forward = forward
        self.left = left
        self.done = False
        self.create_subscription(Odometry, '/robot_10/odom', self.cb, qos_profile_sensor_data)

    def cb(self, msg):
        if self.done:
            return
        self.done = True
        x0 = msg.pose.pose.position.x
        y0 = msg.pose.pose.position.y
        yaw = yaw_from_quaternion(msg.pose.pose.orientation)
        goal_x = x0 + self.forward * math.cos(yaw) - self.left * math.sin(yaw)
        goal_y = y0 + self.forward * math.sin(yaw) + self.left * math.cos(yaw)
        print(f'current position: x={x0:.3f} y={y0:.3f} yaw={math.degrees(yaw):.1f} deg')
        print(f'--goal {goal_x:.3f} {goal_y:.3f}')
        rclpy.shutdown()


def main():
    forward = float(sys.argv[1])
    left = float(sys.argv[2])
    rclpy.init()
    node = OnceOdomReader(forward, left)
    rclpy.spin(node)


if __name__ == '__main__':
    main()
