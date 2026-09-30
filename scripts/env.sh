#!/usr/bin/env bash
# Source this file (do not execute it): ROS 2 Jazzy + this workspace's overlay.
#   source scripts/env.sh
# ROS_DOMAIN_ID (default 10) and ROBOT_NAMESPACE (default /robot_10) keep any value
# already exported. ROS_AUTOMATIC_DISCOVERY_RANGE stays at the ROS 2 default (SUBNET)
# unless you export it first (e.g. LOCALHOST for local-only tests).
# ROS 2 does not read a ROS_NAMESPACE env var: launch files take ROBOT_NAMESPACE and
# pass it as the node namespace (or use `--ros-args -r __ns:=$ROBOT_NAMESPACE`).

_corrida_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -f /opt/ros/jazzy/setup.bash ]; then
  echo "ROS 2 Jazzy not found in /opt/ros/jazzy" >&2
  return 1
fi

# shellcheck disable=SC1091
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-10}"
export ROBOT_NAMESPACE="${ROBOT_NAMESPACE:-/robot_10}"

if [ -f "$_corrida_root/install/setup.bash" ]; then
  # shellcheck disable=SC1091
  source "$_corrida_root/install/setup.bash"
fi
unset _corrida_root
