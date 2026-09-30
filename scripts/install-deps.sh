#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [ -z "${ROS_DISTRO:-}" ]; then
  echo "ROS2 environment not sourced. Run: source scripts/env.sh" >&2
  exit 1
fi

# One-time rosdep setup (needs sudo) on a fresh machine.
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
  sudo rosdep init
fi
rosdep update
rosdep install --from-paths src --ignore-src -y
