# UR3e Isaac Sim Digital Twin

Starter repo for controlling a UR3e robot arm from an external app and syncing the motion into NVIDIA Isaac Sim.

The first working path is deliberately simple:

```text
External app / HTTP / MoveIt
  -> ROS 2 JointState
  -> /joint_command
  -> Isaac Sim ROS 2 Bridge
  -> Articulation Controller
  -> assets/ur3e/ur3e.usd
```

## What Is Included

- `assets/ur3e`: UR3e USD asset copied from the local Omniverse asset folder.
- `assets/scenes/ur3e_pick_place_demo.usda`: demo scene with UR3e, table, colored blocks, and place target.
- `ros2_ws/src/ur3e_omniverse_bridge`: ROS 2 bridge package for `/joint_command`.
- `scenarios/pick_place_blocks.yaml`: scripted MoveIt2 scenario for the block demo.
- `docs`: step-by-step RunPod, Isaac Sim, ROS 2, MoveIt 2, sync, and training notes.
- `scripts`: install/build/run helpers for Ubuntu 24.04 + ROS 2 Jazzy.

## Recommended Platform

- Ubuntu 24.04 desktop on RunPod
- RTX-capable GPU such as RTX 4090, RTX 6000 Ada, L40, L40S, or A6000
- ROS 2 Jazzy
- MoveIt 2
- NVIDIA Isaac Sim with `isaacsim.ros2.bridge`

Avoid A100/H100 for this GUI/RTX workflow because Isaac Sim rendering and many simulation workflows expect RT-core capable GPUs.

## Quick Start

Read in order:

1. [RunPod Ubuntu Desktop](docs/01-runpod-ubuntu-desktop.md)
2. [Install Isaac Sim](docs/02-install-isaac-sim.md)
3. [Install ROS 2 and MoveIt 2](docs/03-install-ros2-moveit2.md)
4. [Sync External App to Isaac Sim](docs/04-sync-external-app-to-isaac-sim.md)
5. [Pick-Place Demo Status](docs/06-pick-place-demo-status.md)
6. [Training Roadmap](docs/05-training-roadmap-isaac-lab.md)

## Build the ROS 2 Workspace

```bash
cd ~/robotx
./scripts/install_ros2_jazzy_moveit2.sh
./scripts/build_ros2_ws.sh
```

## Run a Joint Command Demo

Terminal 1:

```bash
cd ~/robotx
./scripts/run_joint_command_demo.sh
```

Terminal 2:

```bash
source /opt/ros/jazzy/setup.bash
source ~/robotx/ros2_ws/install/setup.bash
ros2 topic echo /joint_command --once
```

## Run the MoveIt2 + Isaac Pick-Place Scene

Terminal 1:

```bash
cd /root/ur3e-isaac-sim-digital-twin
./scripts/run_pick_place_demo_scene.sh
```

Terminal 2:

```bash
cd /root/ur3e-isaac-sim-digital-twin
./scripts/run_moveit_isaac_stack.sh
```

Terminal 3:

```bash
cd /root/ur3e-isaac-sim-digital-twin
./scripts/run_moveit_scenario.sh scenarios/pick_place_blocks.yaml
```

Recorded demo video:

- `docs/media/pick_place_moveit_isaac_demo_latest.mp4`

Current limitation: the robot motion sync works, but the block grasp is not yet a validated physical grasp. Isaac currently rejects attach if the measured end-effector/object distance is too large. See `docs/06-pick-place-demo-status.md`.

## Run HTTP Control for an External App

Inside the RunPod:

```bash
cd ~/robotx
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 run ur3e_omniverse_bridge http_joint_command_server --ros-args -p port:=8000
```

From an external app or terminal:

```bash
curl -X POST https://POD_ID-8000.proxy.runpod.net/joint_command \
  -H 'Content-Type: application/json' \
  -d '{"positions":{"shoulder_pan_joint":0.0,"shoulder_lift_joint":-1.0,"elbow_joint":1.2,"wrist_1_joint":0.0,"wrist_2_joint":0.5,"wrist_3_joint":0.0}}'
```

Replace `POD_ID` with the RunPod pod id and expose HTTP port `8000`.

## Safety

This repo is for simulation-first development. Do not connect the same commands directly to a physical UR3e until robot calibration, speed limits, workspace limits, collision checking, and emergency-stop procedures are in place.
