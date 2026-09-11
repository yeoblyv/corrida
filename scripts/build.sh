#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [ -z "${ROS_DISTRO:-}" ]; then
  echo "ROS2 environment not sourced. Run: source /opt/ros/jazzy/setup.bash" >&2
  exit 1
fi

colcon build --symlink-install
echo "Build complete. Run: source install/setup.bash"
