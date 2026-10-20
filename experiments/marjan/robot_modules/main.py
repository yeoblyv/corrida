"""Start the robot with the behaviour you choose.

Usage (run from this folder):
python3 main.py                  # default: wall_left
python3 main.py wall_left        # left-hand rule
python3 main.py wall_right       # right-hand rule
python3 main.py wall_left_robust   # left-hand rule + LoopGuard + LiDAR front check
python3 main.py wall_right_robust  # right-hand rule + LoopGuard + LiDAR front check
python3 main.py bump             # turn to face an obstacle and touch it with the front bumper
python3 main.py avoid            # simple reactive obstacle avoider

Optional, only for the two _robust behaviours -- tell the robot where the
finish mark is so it stops itself and lights up cyan on arrival:
python3 main.py wall_left_robust --goal 3.2 -1.1
(goal is "metres forward, metres left" of wherever the robot is facing
right now -- see INTEGRATION_NOTES.md for how to measure this on demo day)
"""
import argparse

import rclpy

from bump_target import BumpTarget
from obstacle_avoider import ObstacleAvoider
from wall_follower import WallFollower
from wall_follower_robust import WallFollowerRobust

# name you type -> how to create that behaviour
BEHAVIOURS = {
    'wall_left': lambda: WallFollower('left'),
    'wall_right': lambda: WallFollower('right'),
    'wall_left_robust': lambda: WallFollowerRobust('left'),
    'wall_right_robust': lambda: WallFollowerRobust('right'),
    'bump': BumpTarget,
    'avoid': ObstacleAvoider,
}


def main():
    parser = argparse.ArgumentParser(description='Run one robot behaviour.')
    parser.add_argument('behaviour', nargs='?', default='wall_left',
                         choices=sorted(BEHAVIOURS.keys()),
                         help='which behaviour to run (default: wall_left)')
    parser.add_argument('--goal', nargs=2, type=float, metavar=('X', 'Y'), default=None,
                         help='finish position in metres (forward, left) of the start '
                              'heading, in the odom frame -- only used by the _robust '
                              'behaviours; ignored (with a warning) for the others')
    args = parser.parse_args()

    rclpy.init()
    node = BEHAVIOURS[args.behaviour]()
    node.get_logger().info(f'Running behaviour: {args.behaviour}')
    if args.goal is not None:
        if hasattr(node, 'set_goal'):
            node.set_goal(args.goal[0], args.goal[1])
        else:
            node.get_logger().warning(
                f'--goal was given but {args.behaviour} does not support it -- ignoring')
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.stop()  # stop the wheels and give the lights back
        except Exception:
            pass  # ROS may already be shutting down after Ctrl+C
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
