# src/

The ROS 2 packages. The repo root is the colcon workspace, so build from
there with `./scripts/build.sh`.

- `corrida_bringup/` - launch files and config that start the lidar and
  slam_toolbox

New packages get the `corrida_` prefix. Logic that doesn't need ROS
should stay plain Python, so it can be tested in `tests/` without the
robot.
