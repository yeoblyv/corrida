#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

if [ -z "$ROS_DISTRO" ]; then
  echo "ROS 2 is not sourced, run: source scripts/env.sh" >&2
  exit 1
fi

# rosdep has to be initialised once per machine (asks for sudo)
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
  sudo rosdep init
fi
rosdep update
rosdep install --from-paths src --ignore-src -y
