#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export ROBOTX_STAGE_PATH="$REPO_ROOT/assets/scenes/ur3e_pick_place_demo.usda"
exec "$REPO_ROOT/scripts/run_isaac_sim.sh" --exec "$REPO_ROOT/scripts/setup_ur3e_ros2_action_graph.py" "$@"
