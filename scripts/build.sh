#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

if [ -z "$ROS_DISTRO" ]; then
  echo "ROS 2 is not sourced, run: source scripts/env.sh" >&2
  exit 1
fi

colcon build --symlink-install
echo "Build done, now run: source scripts/env.sh"
