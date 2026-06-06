#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME_MODE="${1:-ros}"

source /opt/ros/jazzy/setup.bash
source "$REPO_ROOT/ros2_ws/install/setup.bash"

ros2 run ur3e_omniverse_bridge ur3e_joint_command_demo --ros-args \
  -p topic:=/joint_command \
  -p name_mode:="$NAME_MODE"
