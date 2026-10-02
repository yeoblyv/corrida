#!/usr/bin/env bash
# Source this file (do not execute it): ROS 2 Jazzy + this workspace's overlay.
#   source scripts/env.sh
# ROS_DOMAIN_ID (default 10) and ROBOT_NAMESPACE (default /robot_10) keep any value
# already exported. ROS_AUTOMATIC_DISCOVERY_RANGE stays at the ROS 2 default (SUBNET)
# unless you export it first (e.g. LOCALHOST for local-only tests).
# RMW_IMPLEMENTATION defaults to rmw_cyclonedds_cpp because our robot runs Cyclone DDS.
# All ROS 2 processes have to use the same RMW as the robot (it is set on the robot's
# web page): https://iroboteducation.github.io/create3_docs/setup/xml-config/
# With the Jazzy default (Fast DDS) on our side we saw the robot's topics but got no data.
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
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_cyclonedds_cpp}"

if [ -f "$_corrida_root/install/setup.bash" ]; then
  # shellcheck disable=SC1091
  source "$_corrida_root/install/setup.bash"
fi
unset _corrida_root
