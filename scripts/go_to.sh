#!/usr/bin/env bash
# Drive the robot to a point given in metres from where it stands now.
# usage: scripts/go_to.sh X Y [MINUTES]
#   X metres ahead, Y metres to the left (negative = right), MINUTES defaults to 8.
# Needs bringup.launch.py and nav2.launch.py running (see scripts/README.md).
set -e
cd "$(dirname "$0")/.."

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "usage: scripts/go_to.sh X Y [MINUTES]" >&2
  exit 1
fi
x=$1
y=$2
minutes=${3:-8}

# the explorer takes the finish as a distance and an angle from the start heading
read -r distance angle < <(python3 -c \
  "import math,sys; x,y=float(sys.argv[1]),float(sys.argv[2]); \
print(f'{math.hypot(x,y):.3f} {math.degrees(math.atan2(y,x)):.1f}')" "$x" "$y")
echo "target ($x, $y) m -> finish_distance=$distance finish_angle=$angle"

source scripts/env.sh
ros2 launch corrida_exploration explore.launch.py drive:=true align:=false \
  finish_distance:="$distance" finish_angle:="$angle" max_minutes:="$minutes"
