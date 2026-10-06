"""Start the robot with the behaviour you choose.

Usage (run from this folder):
    python3 main.py              # default: wall_left
    python3 main.py wall_left    # left-hand rule
    python3 main.py wall_right   # right-hand rule
    python3 main.py bump         # turn to face an obstacle and touch it with the front bumper
    python3 main.py avoid        # simple reactive obstacle avoider
"""
import argparse

import rclpy

from bump_target import BumpTarget
from obstacle_avoider import ObstacleAvoider
from wall_follower import WallFollower

# name you type -> how to create that behaviour
BEHAVIOURS = {
    'wall_left': lambda: WallFollower('left'),
    'wall_right': lambda: WallFollower('right'),
    'bump': BumpTarget,
    'avoid': ObstacleAvoider,
}


def main():
    parser = argparse.ArgumentParser(description='Run one robot behaviour.')
    parser.add_argument('behaviour', nargs='?', default='wall_left',
                        choices=sorted(BEHAVIOURS.keys()),
                        help='which behaviour to run (default: wall_left)')
    args = parser.parse_args()

    rclpy.init()
    node = BEHAVIOURS[args.behaviour]()
    node.get_logger().info(f'Running behaviour: {args.behaviour}')
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.stop()             # stop the wheels and give the lights back
        except Exception:
            pass                    # ROS may already be shutting down after Ctrl+C
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
