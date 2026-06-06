#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$SCRIPT_DIR/run_isaac_sim.sh" --exec "$SCRIPT_DIR/open_ur3e_stage.py" "$@"
