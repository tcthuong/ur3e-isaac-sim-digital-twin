#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

set +u
source "$REPO_ROOT/scripts/setup_fastdds.sh"
source /opt/ros/jazzy/setup.bash
source "$REPO_ROOT/ros2_ws/install/setup.bash"
set -u

PIDS=()
cleanup() {
  for pid in "${PIDS[@]:-}"; do
    kill "$pid" 2>/dev/null || true
  done
}
trap cleanup EXIT INT TERM

ros2 launch ur_robot_driver ur_rsp.launch.py \
  ur_type:=ur3e \
  robot_ip:=0.0.0.0 \
  use_mock_hardware:=false &
PIDS+=("$!")

sleep 2

ros2 launch ur_moveit_config ur_moveit.launch.py \
  ur_type:=ur3e \
  launch_rviz:=true \
  use_sim_time:=true &
PIDS+=("$!")

sleep 4

ros2 run ur3e_omniverse_bridge follow_joint_trajectory_to_joint_command --ros-args \
  -p action_name:=/scaled_joint_trajectory_controller/follow_joint_trajectory \
  -p output_topic:=/joint_command \
  -p joint_state_topic:=/joint_states &
PIDS+=("$!")

echo "MoveIt2 + Isaac trajectory bridge is running."
echo "Run pick-place demo in another terminal: ./scripts/run_moveit_pick_place_demo.sh"

wait -n "${PIDS[@]}"
