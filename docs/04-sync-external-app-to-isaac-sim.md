# Sync an External App to Isaac Sim

The target runtime data flow is:

```text
External app / MoveIt / HTTP API
  -> ROS 2 sensor_msgs/JointState
  -> /joint_command
  -> Isaac Sim ROS2 Subscribe Joint State
  -> Articulation Controller
  -> UR3e USD articulation
```

Official Isaac Sim tutorial:

- ROS2 Joint Control: https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/tutorial_ros2_manipulation.html

## Step 1: Build the Bridge

```bash
cd /root/ur3e-isaac-sim-digital-twin/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Step 2: Configure Isaac Sim Action Graph

Use the launcher that opens the UR3e stage and creates the ROS 2 Action Graph automatically:

```bash
cd /root/ur3e-isaac-sim-digital-twin
./scripts/run_ur3e_ros2_bridge.sh
```

The runtime graph is created at `/ActionGraph` with this wiring:

```text
On Playback Tick
  -> ROS2 Subscribe Joint State [/joint_command]
  -> Articulation Controller [/ur3e/root_joint]

On Playback Tick
  -> ROS2 Publish Joint State [/joint_states]
  -> ROS2 Publish Clock [/clock]
```

The script finds the actual articulation root automatically. For the current UR3e USD it is `/ur3e/root_joint`. The subscriber sends `jointNames`, `positionCommand`, `velocityCommand`, and `effortCommand` into the Articulation Controller. Isaac Sim starts playback automatically so incoming ROS 2 commands are applied immediately.

### Manual UI Setup

Create an Action Graph:

1. Open **Window > Graph Editors > Action Graph**.
2. Add `On Playback Tick`.
3. Add `ROS2 Context`.
4. Add `ROS2 Subscribe Joint State`.
5. Add `Articulation Controller`.
6. Add optional `ROS2 Publish Joint State`, `ROS2 Publish Clock`, and `Isaac Read Simulation Time`.
7. Set `ROS2 Subscribe Joint State.inputs:topicName` to `/joint_command`.
8. Set `Articulation Controller.inputs:robotPath` to the articulation root. For this asset, use `/ur3e/root_joint`.
9. Set `ROS2 Publish Joint State.inputs:topicName` to `/joint_states`.
10. Set `ROS2 Publish Joint State.inputs:targetPrim` to `/ur3e/root_joint`.
11. Connect tick execution into the subscriber, publisher, clock, and controller.
12. Connect context into all ROS 2 nodes.
13. Connect simulation time into joint-state and clock timestamps.
14. Connect subscriber joint names and commands into the controller command inputs.
15. Press **Play**.

If the robot does not move, inspect the USD articulation's actual joint names. Then run the demo with `name_mode:=usd_short` or pass explicit `joint_names_csv`.

## Step 3: Run a Demo Publisher

```bash
cd /root/ur3e-isaac-sim-digital-twin/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run ur3e_omniverse_bridge ur3e_joint_command_demo --ros-args -p topic:=/joint_command
```

Verify the topic:

```bash
cd /root/ur3e-isaac-sim-digital-twin
source scripts/setup_fastdds.sh
source /opt/ros/jazzy/setup.bash
ros2 topic echo /joint_command --once
```

Verify Isaac is publishing state back to ROS 2:

```bash
cd /root/ur3e-isaac-sim-digital-twin
source scripts/setup_fastdds.sh
source /opt/ros/jazzy/setup.bash
ros2 topic echo /joint_states --once
```

Expected joint names:

```text
shoulder_pan_joint
shoulder_lift_joint
elbow_joint
wrist_1_joint
wrist_2_joint
wrist_3_joint
```

## Quick Visual Motion Test

To verify the UR3e articulation can move before wiring the ROS 2 Action Graph, run:

```bash
cd /root/ur3e-isaac-sim-digital-twin
./scripts/run_ur3e_demo_motion.sh
```

This opens `assets/ur3e/ur3e.usd`, initializes the `/ur3e` articulation, and applies a small sinusoidal joint-position demo directly inside Isaac Sim.

## Step 4: Relay an External App

### Option A: App Runs Inside the Same ROS 2 Network

If your external app can publish `sensor_msgs/JointState`, publish to `/external_joint_states`, then run:

```bash
ros2 run ur3e_omniverse_bridge external_joint_state_relay --ros-args \
  -p input_topic:=/external_joint_states \
  -p output_topic:=/joint_command \
  -p source_name_mode:=ros \
  -p target_name_mode:=ros
```

Your external app message should look like:

```text
name:
- shoulder_pan_joint
- shoulder_lift_joint
- elbow_joint
- wrist_1_joint
- wrist_2_joint
- wrist_3_joint
position:
- 0.0
- -1.2
- 1.5
- 0.0
- 0.8
- 0.0
```

If your app has different joint names, publish its names and pass mapping parameters:

```bash
ros2 run ur3e_omniverse_bridge external_joint_state_relay --ros-args \
  -p source_joint_names_csv:=j1,j2,j3,j4,j5,j6 \
  -p target_joint_names_csv:=shoulder_pan_joint,shoulder_lift_joint,elbow_joint,wrist_1_joint,wrist_2_joint,wrist_3_joint
```

## Step 5: Mirror MoveIt Planned Paths

This is useful for visual sync while you are still setting up full trajectory execution:

```bash
ros2 run ur3e_omniverse_bridge display_trajectory_to_joint_command --ros-args \
  -p input_topic:=/display_planned_path \
  -p output_topic:=/joint_command
```

When RViz/MoveIt publishes a planned path, the bridge plays the joint points to Isaac Sim.

## Control Rule

Use one command source at a time:

- demo publisher, or
- external app relay, or
- MoveIt trajectory relay.

Do not publish competing commands to `/joint_command` unless you intentionally build an arbiter.

## RunPod-Friendly HTTP Control

If your app is outside the Pod, direct ROS 2 discovery can be awkward because RunPod public access is HTTP/TCP oriented and ROS 2 DDS often relies on UDP discovery. Use the HTTP bridge first.

Expose HTTP port `8000` in the RunPod Pod settings, then run:

```bash
cd /root/ur3e-isaac-sim-digital-twin/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run ur3e_omniverse_bridge http_joint_command_server --ros-args -p port:=8000
```

From your external app, send:

```bash
curl -X POST https://POD_ID-8000.proxy.runpod.net/joint_command \
  -H 'Content-Type: application/json' \
  -d '{"positions":{"shoulder_pan_joint":0.0,"shoulder_lift_joint":-1.0,"elbow_joint":1.2,"wrist_1_joint":0.0,"wrist_2_joint":0.5,"wrist_3_joint":0.0}}'
```

You can also send explicit arrays:

```json
{
  "name": [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint"
  ],
  "position": [0.0, -1.0, 1.2, 0.0, 0.5, 0.0]
}
```
