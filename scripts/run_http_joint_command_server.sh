#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${1:-8000}"

set +u
source "$REPO_ROOT/scripts/setup_fastdds.sh"
source /opt/ros/jazzy/setup.bash
source "$REPO_ROOT/ros2_ws/install/setup.bash"
set -u

ros2 run ur3e_omniverse_bridge http_joint_command_server --ros-args \
  -p host:=0.0.0.0 \
  -p port:="$PORT" \
  -p output_topic:=/joint_command
