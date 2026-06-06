#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec "$SCRIPT_DIR/run_isaac_sim.sh" \
  isaacsim.exp.compatibility_check \
  --/app/quitAfter=10 \
  --no-window \
  "$@"
