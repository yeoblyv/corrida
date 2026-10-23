# src/

The ROS 2 packages. The repo root is the colcon workspace, so build from
there with `./scripts/build.sh`.

- `corrida_bringup/` - launch files and config that start the lidar and
  slam_toolbox (`bringup.launch.py`) and Nav2 (`nav2.launch.py`), plus
  the odometry relay Nav2 needs with this robot
- `corrida_exploration/` - finds the frontiers of the SLAM map, shows the
  next place to explore in Foxglove and, with `drive:=true`, drives there
  through Nav2

New packages get the `corrida_` prefix. Logic that doesn't need ROS
should stay plain Python, so it can be tested in `tests/` without the
robot.
