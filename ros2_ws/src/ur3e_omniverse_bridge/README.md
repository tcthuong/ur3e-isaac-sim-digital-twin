# ur3e_omniverse_bridge

Small ROS 2 nodes for syncing UR3e joint commands into NVIDIA Isaac Sim.

## Nodes

- `ur3e_joint_command_demo`: publishes a smooth demo `sensor_msgs/JointState` to `/joint_command`.
- `external_joint_state_relay`: maps an external app's `JointState` topic to `/joint_command`.
- `display_trajectory_to_joint_command`: plays MoveIt `/display_planned_path` points as `/joint_command`.
- `http_joint_command_server`: accepts `POST /joint_command` JSON over HTTP and publishes `/joint_command`.

## Build

```bash
cd ~/robotx/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Demo

```bash
ros2 run ur3e_omniverse_bridge ur3e_joint_command_demo --ros-args -p topic:=/joint_command
```

If your Isaac Sim USD articulation uses short joint names, try:

```bash
ros2 run ur3e_omniverse_bridge ur3e_joint_command_demo --ros-args -p name_mode:=usd_short
```

## HTTP Control

This is useful on RunPod because browser/API apps can reach HTTP proxy ports more easily than ROS 2 DDS discovery.

```bash
ros2 run ur3e_omniverse_bridge http_joint_command_server --ros-args -p port:=8000
```

In another terminal:

```bash
curl -X POST http://127.0.0.1:8000/joint_command \
  -H 'Content-Type: application/json' \
  -d '{"positions":{"shoulder_pan_joint":0.0,"shoulder_lift_joint":-1.0,"elbow_joint":1.2,"wrist_1_joint":0.0,"wrist_2_joint":0.5,"wrist_3_joint":0.0}}'
```
