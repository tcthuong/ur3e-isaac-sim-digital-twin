# UR3e Isaac Sim Digital Twin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a public starter repo that lets a user install Isaac Sim, ROS 2 Jazzy, MoveIt 2, and sync an external UR3e joint-command app into Isaac Sim.

**Architecture:** The repo keeps the UR3e USD asset under `assets/ur3e`, documents the RunPod Ubuntu workflow under `docs`, and provides a small ROS 2 Python bridge under `ros2_ws/src/ur3e_omniverse_bridge`. Isaac Sim receives `sensor_msgs/JointState` on `/joint_command` through the ROS 2 Bridge and applies it with an Articulation Controller.

**Tech Stack:** Ubuntu 24.04, NVIDIA Isaac Sim, ROS 2 Jazzy, MoveIt 2, Universal Robots ROS 2 packages, Python `rclpy`, `sensor_msgs`, optional Isaac Lab for training.

---

### Task 1: Repository Structure

**Files:**
- Create: `README.md`
- Create: `LICENSE`
- Create: `.gitignore`
- Create: `assets/ur3e/`

- [ ] Copy the existing UR3e USD asset from `C:\Users\Dev\Downloads\ur3e\ur3e` into `assets/ur3e`.
- [ ] Add repository metadata explaining the digital-twin goal, supported platform, and quick start.
- [ ] Keep binary USD files tracked because the asset is small enough for a starter repo.

### Task 2: ROS 2 Bridge Package

**Files:**
- Create: `ros2_ws/src/ur3e_omniverse_bridge/package.xml`
- Create: `ros2_ws/src/ur3e_omniverse_bridge/setup.py`
- Create: `ros2_ws/src/ur3e_omniverse_bridge/ur3e_omniverse_bridge/*.py`
- Create: `ros2_ws/src/ur3e_omniverse_bridge/test/test_joint_utils.py`

- [ ] Add joint-name utilities for standard UR3e ROS names and short USD fallback names.
- [ ] Add a demo publisher for `/joint_command`.
- [ ] Add a relay for external app `JointState` topics.
- [ ] Add a relay for MoveIt `/display_planned_path` previews.
- [ ] Add unit tests for joint-name resolution, bounded demo motion, and mapping.

### Task 3: Install and Operation Docs

**Files:**
- Create: `docs/01-runpod-ubuntu-desktop.md`
- Create: `docs/02-install-isaac-sim.md`
- Create: `docs/03-install-ros2-moveit2.md`
- Create: `docs/04-sync-external-app-to-isaac-sim.md`
- Create: `docs/05-training-roadmap-isaac-lab.md`

- [ ] Write concise, step-by-step RunPod setup guidance.
- [ ] Document Isaac Sim workstation install and compatibility checks.
- [ ] Document ROS 2 Jazzy, MoveIt 2, UR packages, and workspace build.
- [ ] Document Isaac Sim Action Graph wiring for `/joint_command`.
- [ ] Describe training as a later Isaac Lab/ROS 2 policy path, not a first-day requirement.

### Task 4: Setup Scripts

**Files:**
- Create: `scripts/install_ros2_jazzy_moveit2.sh`
- Create: `scripts/setup_fastdds.sh`
- Create: `scripts/build_ros2_ws.sh`
- Create: `scripts/run_joint_command_demo.sh`

- [ ] Add scripts that are safe to re-run where practical.
- [ ] Keep scripts short and readable so docs remain the source of truth.
- [ ] Verify shell syntax with `bash -n` where available.

### Task 5: Verification, Commit, Push

**Files:**
- Modify: Git index and remote

- [ ] Run Python unit tests.
- [ ] Check file tree and git status.
- [ ] Commit the repo.
- [ ] Create or connect a public GitHub repo named `ur3e-isaac-sim-digital-twin`.
- [ ] Push `main`.
