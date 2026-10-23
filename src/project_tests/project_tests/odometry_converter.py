#!/usr/bin/env python3


# note 1: I performed accuracy test on the odometry, see odometry_data.xlsx
# the error's were minimal (<2%) and can be corrected using SLAM, so the error's
# will not be adressed further.

# note 2: parameters are in odometry_converter_parameters.yaml. To use this, paste the following command in terminal (maybe adjust it):
# ros2 run project_tests odometry_converter --ros-args --params-file /home/mark/create3_ws/src/project_tests/config/odometry_converter_parameters.yaml

# note 3: possible to also use launch. Run these two lines:
# cd ~/create3_ws
# source install/setup.bash
# ros2 launch project_tests odometry.launch.py

# note 4: command to run teleop_twist_keyboard
# ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/robot_10/cmd_vel


# setup libraries
from corrida_interfaces.msg import ConvertedOdometry # custom message type
import math
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from rclpy.qos import ReliabilityPolicy, QoSProfile


# setup dictionary
FACE_DIRECTION_MAZE = {
    "positive_x": 0.0,
    "positive_y": 90.0,
    "negative_x": 180.0,
    "negative_y": -90.0,
}


# helper function
def from_orientation_to_yaw(x, y, z, w):
    return math.atan2(2 * (w * z + x * y), 1 - 2 * (y**2 + z**2))


# this class maps a raw pose to a maze frame pose
class OdometryMap():

    # runs when class object is made; set the maze frame start coordinate as basis
    def __init__(self, start_xy, face_direction, finish_xy, finish_error):
        self.start_maze_pose = (float(start_xy[0]), float(start_xy[1]), math.radians(float(face_direction)))
        self.start_dyaw = 0.0
        self.last_raw_pose = None
        self.last_maze_pose = (0.0, 0.0, 0.0)
        self.finish_maze_xy = (float(finish_xy[0]), float(finish_xy[1]))
        self.finish_maze_error = float(finish_error)

    # main function of the class; converts a raw pose to the maze frame pose
    def to_maze_frame(self, raw_pose):

        # for first time set the initial values and return that no movement yet
        if self.last_raw_pose is None:
            self.last_raw_pose = raw_pose
            self.last_maze_pose = self.start_maze_pose
            self.start_dyaw = self.start_maze_pose[2] - raw_pose[2]

        # for second time and onward run this
        else:
            # calculate the difference in the raw pose
            dx_raw = raw_pose[0] - self.last_raw_pose[0]
            dy_raw = raw_pose[1] - self.last_raw_pose[1]
            maze_yaw = math.atan2(math.sin(raw_pose[2] + self.start_dyaw), math.cos(raw_pose[2] + self.start_dyaw)) # wraps angle in radians to the range -pi..pi

            # perform 2D tranformation on raw coordinate difference to get maze coordinate difference
            dx = dx_raw * math.cos(self.start_dyaw) - dy_raw * math.sin(self.start_dyaw)
            dy = dx_raw * math.sin(self.start_dyaw) + dy_raw * math.cos(self.start_dyaw)

            # store raw reading for next calculating difference
            self.last_raw_pose = raw_pose

            # calculate current maze pose (which then is also the last pose)
            self.last_maze_pose = (self.last_maze_pose[0] + dx, self.last_maze_pose[1]  + dy, maze_yaw)
        
        # return the updated converted maze pose
        return self.last_maze_pose

    # function that measures if the robot within the allowed finish error
    def at_finish(self):
        
        # calculate error distance by using c= sqrt(a**2 + b**2) (which math.hypot() does)
        x_error = self.finish_maze_xy[0] - self.last_maze_pose[0]
        y_error = self.finish_maze_xy[1] - self.last_maze_pose[1]
        distance_error = math.hypot(x_error, y_error)

        # return boolean True if it is at the finish
        return (distance_error < self.finish_maze_error, distance_error)


# define node to subscribe to topics
class OdometryConverter(Node):

    # runs  when the node is created, sets up the basics
    def __init__(self):
        super().__init__("odometry_converter") # name of the node is with underscore

        # declare parameters from YAML with default values
        self.declare_parameter("odometry_topic", "/robot_10/odom")
        self.declare_parameter("converted_odometry_topic", "/robot_10/converted_odom")
        self.declare_parameter("start_x", 0.2)
        self.declare_parameter("start_y", 0.2)
        self.declare_parameter("start_face_direction", "positive_x")
        self.declare_parameter("finish_x", 4.4)
        self.declare_parameter("finish_y", 2.8)
        self.declare_parameter("finish_allowed_error", 0.2)
        self.declare_parameter("print_information", False)

        # read parameters from YAML
        odometry_topic = self.get_parameter("odometry_topic").value
        converted_odometry_topic = self.get_parameter("converted_odometry_topic").value
        start_x = self.get_parameter("start_x").value
        start_y = self.get_parameter("start_y").value
        start_face_direction = self.get_parameter("start_face_direction").value
        finish_x = self.get_parameter("finish_x").value
        finish_y = self.get_parameter("finish_y").value
        finish_allowed_error = self.get_parameter("finish_allowed_error").value
        self.print_information = self.get_parameter("print_information").value
        
        # create the map
        self.odometry_map = OdometryMap(start_xy=(start_x,start_y), face_direction=FACE_DIRECTION_MAZE[start_face_direction], finish_xy=(finish_x,finish_y), finish_error=finish_allowed_error)

        # subscribe to the odometry topic, which has a message with type Odometry, and go to odometry_callback if message is received
        self.odometry_subscriber = self.create_subscription(Odometry,odometry_topic, self.odometry_callback, QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT))

        # publish to the converted odometry topic, which has a message with type ConvertedOdometry
        self.converted_odometry_publisher = self.create_publisher(ConvertedOdometry, converted_odometry_topic, 10)
        
        # print the calculated maze_pose and finished in terminal
        if self.print_information:
            self.get_logger().info("odometry_converter started, waiting for odometry.")
        
    # function that runs everytime when raw odometry data is received
    def odometry_callback(self,msg):

        # get the raw pose from odometry information from subscriber
        x_raw = msg.pose.pose.position.x
        y_raw = msg.pose.pose.position.y
        yaw_raw = from_orientation_to_yaw(msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z, msg.pose.pose.orientation.w)

        # calculate the current maze pose of robot from the raw pose
        maze_pose = self.odometry_map.to_maze_frame((x_raw, y_raw, yaw_raw))

        # calculate if the robot is at the finish
        finished = self.odometry_map.at_finish()

        # prepare and publish the converted odometry information
        out = ConvertedOdometry()
        out.header.stamp = msg.header.stamp # time of the measurement, copied from the robot's message
        out.header.frame_id = "maze"
        out.x = maze_pose[0]
        out.y = maze_pose[1]
        out.yaw = maze_pose[2]
        out.finished = finished[0]
        out.distance_to_finish = finished[1]
        self.converted_odometry_publisher.publish(out)

        # print the calculated maze_pose and finished in terminal
        if self.print_information:
            self.get_logger().info(
                f"x: {maze_pose[0]:.2f} m, "
                f"y: {maze_pose[1]:.2f} m, "
                f"yaw: {maze_pose[2]:.2f} rad, "
                f"finished: {finished[0]} (distance: {finished[1]:.2f} m)", 
                throttle_duration_sec=3.0)


# this starts, runs, and stops the node when the programming is called
def main():

    # setup rclpy and odometry converter node
    rclpy.init()
    node = OdometryConverter()

    # run odometry converter node, untill KeyboardInterrupt, then close node and try shutdown (if not already shutdown by keyboard interrupt)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


# if this file is called directly, run the main function
if __name__ == '__main__':
    main()