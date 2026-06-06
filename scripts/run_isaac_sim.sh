#!/usr/bin/env bash
set -euo pipefail

ISAACSIM_ENV="${ISAACSIM_ENV:-$HOME/isaacsim-5.1.0}"
ISAACSIM_BIN="$ISAACSIM_ENV/bin/isaacsim"
ISAACSIM_ROS_BRIDGE="$ISAACSIM_ENV/lib/python3.11/site-packages/isaacsim/exts/isaacsim.ros2.bridge"
ISAACSIM_ROS_DISTRO="${ISAACSIM_ROS_DISTRO:-jazzy}"
ISAACSIM_ROS_LIB="$ISAACSIM_ROS_BRIDGE/$ISAACSIM_ROS_DISTRO/lib"

if [[ ! -x "$ISAACSIM_BIN" ]]; then
  echo "Isaac Sim executable not found: $ISAACSIM_BIN" >&2
  echo "Set ISAACSIM_ENV to the Isaac Sim Python environment path." >&2
  exit 1
fi

if [[ ! -d "$ISAACSIM_ROS_LIB" ]]; then
  echo "Isaac Sim ROS 2 bridge libraries not found: $ISAACSIM_ROS_LIB" >&2
  exit 1
fi

# Isaac Sim pip packages are Python 3.11. Do not inherit ROS Jazzy's
# Python 3.12 paths from an already-sourced shell.
unset AMENT_PREFIX_PATH
unset COLCON_PREFIX_PATH
unset CMAKE_PREFIX_PATH
unset PYTHONPATH

export OMNI_KIT_ACCEPT_EULA="${OMNI_KIT_ACCEPT_EULA:-YES}"
export OMNI_KIT_ALLOW_ROOT="${OMNI_KIT_ALLOW_ROOT:-1}"
export ROS_DISTRO="$ISAACSIM_ROS_DISTRO"
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"
export FASTRTPS_DEFAULT_PROFILES_FILE="${FASTRTPS_DEFAULT_PROFILES_FILE:-$HOME/.ros/fastdds.xml}"
export LD_LIBRARY_PATH="$ISAACSIM_ROS_LIB${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

exec "$ISAACSIM_BIN" --enable isaacsim.ros2.bridge "$@"
