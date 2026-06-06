#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT/ros2_ws"

source /opt/ros/jazzy/setup.bash
rosdep install -i --from-path src --rosdistro jazzy -y
colcon build --symlink-install

if ! grep -q "source $REPO_ROOT/ros2_ws/install/setup.bash" "$HOME/.bashrc"; then
  echo "source $REPO_ROOT/ros2_ws/install/setup.bash" >> "$HOME/.bashrc"
fi

echo "Workspace built. Run: source $REPO_ROOT/ros2_ws/install/setup.bash"
