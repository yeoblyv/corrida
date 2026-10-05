# src/

The ROS 2 packages. The repo root is the colcon workspace, so build from
there with `./scripts/build.sh`.

- `corrida_bringup/` - launch files and config that start the lidar and
  slam_toolbox
- `corrida_exploration/` - finds the frontiers of the SLAM map and picks
  the next place to explore. It only shows that goal in Foxglove for now,
  it doesn't drive the robot

New packages get the `corrida_` prefix. Logic that doesn't need ROS
should stay plain Python, so it can be tested in `tests/` without the
robot.
