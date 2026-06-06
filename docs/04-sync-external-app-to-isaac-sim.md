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
cd ~/robotx/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Step 2: Configure Isaac Sim Action Graph

Open `~/robotx/assets/ur3e/ur3e.usd` in Isaac Sim.

Create an Action Graph:

1. Open **Window > Graph Editors > Action Graph**.
2. Add `On Playback Tick`.
3. Add `ROS2 Subscribe Joint State`.
4. Add `Articulation Controller`.
5. Set the subscriber topic to `/joint_command`.
6. Set the Articulation Controller target prim to the UR3e articulation root.
7. Connect tick execution into the subscriber and controller.
8. Connect subscriber joint names and positions into the controller command inputs.
9. Press **Play**.

If the robot does not move, inspect the USD articulation's actual joint names. Then run the demo with `name_mode:=usd_short` or pass explicit `joint_names_csv`.

## Step 3: Run a Demo Publisher

```bash
cd ~/robotx/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run ur3e_omniverse_bridge ur3e_joint_command_demo --ros-args -p topic:=/joint_command
```

Verify the topic:

```bash
ros2 topic echo /joint_command --once
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
cd ~/robotx/ros2_ws
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
