#!/usr/bin/env bash
# Source this file, don't run it:  source scripts/env.sh
# Sets up ROS 2 Jazzy, the robot's domain and namespace, and this workspace if it is built.
# Variables that are already exported keep their value.

source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-10}"
export ROBOT_NAMESPACE="${ROBOT_NAMESPACE:-/robot_10}"  # read by bringup.launch.py
# our robot runs Cyclone DDS and every node needs the same RMW as the robot,
# with the Jazzy default (Fast DDS) we saw its topics but got no data:
# https://iroboteducation.github.io/create3_docs/setup/xml-config/
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_cyclonedds_cpp}"

corrida_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "$corrida_dir/install/setup.bash" ]; then
  source "$corrida_dir/install/setup.bash"
fi
unset corrida_dir
