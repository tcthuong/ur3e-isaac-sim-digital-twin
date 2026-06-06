#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCENARIO_FILE="${1:-$REPO_ROOT/scenarios/pick_place_blocks.yaml}"

set +u
source "$REPO_ROOT/scripts/setup_fastdds.sh"
source /opt/ros/jazzy/setup.bash
source "$REPO_ROOT/ros2_ws/install/setup.bash"
set -u

ros2 run ur3e_omniverse_bridge moveit_scenario_runner --ros-args \
  -p scenario_file:="$SCENARIO_FILE"
