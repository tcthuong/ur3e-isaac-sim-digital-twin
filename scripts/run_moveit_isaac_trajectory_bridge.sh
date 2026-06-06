#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ACTION_NAME="${1:-/scaled_joint_trajectory_controller/follow_joint_trajectory}"

set +u
source "$REPO_ROOT/scripts/setup_fastdds.sh"
source /opt/ros/jazzy/setup.bash
source "$REPO_ROOT/ros2_ws/install/setup.bash"
set -u

ros2 run ur3e_omniverse_bridge follow_joint_trajectory_to_joint_command --ros-args \
  -p action_name:="$ACTION_NAME" \
  -p output_topic:=/joint_command \
  -p joint_state_topic:=/joint_states
