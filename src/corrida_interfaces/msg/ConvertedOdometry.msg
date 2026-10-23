std_msgs/Header header      # stamp copied from the odometry message, frame_id "maze"
float64 x                   # meters, maze frame
float64 y                   # meters, maze frame
float64 yaw                 # radians, counter-clockwise from maze +x, -pi..pi
bool finished               # true when within the allowed error of the finish
float64 distance_to_finish  # meters