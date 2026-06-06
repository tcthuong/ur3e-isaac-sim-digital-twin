#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

set +u
source "$REPO_ROOT/scripts/setup_fastdds.sh"
source /opt/ros/jazzy/setup.bash
source "$REPO_ROOT/ros2_ws/install/setup.bash"
set -u

ros2 run ur3e_omniverse_bridge moveit_pick_place_demo "$@"
