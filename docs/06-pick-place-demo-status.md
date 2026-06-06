# MoveIt2 Isaac Pick-Place Demo Status

This document records the current UR3e pick-place demo state, how to run it, what the recorded video shows, and what still needs work before claiming a real grasp simulation.

## Current Demo Assets

- Scene: `assets/scenes/ur3e_pick_place_demo.usda`
- Scenario: `scenarios/pick_place_blocks.yaml`
- Isaac launcher: `scripts/run_pick_place_demo_scene.sh`
- Scenario runner: `scripts/run_moveit_scenario.sh`
- ROS 2 node: `ur3e_omniverse_bridge.moveit_scenario_runner`
- Recorded video: `docs/media/pick_place_moveit_isaac_demo_latest.mp4`

The scene contains:

- UR3e USD robot from `assets/ur3e/ur3e.usd`
- table
- red pick cube
- blue spare cube
- green place target
- red and green visual markers

## Runtime Data Flow

```text
MoveIt2 scenario YAML
  -> moveit_scenario_runner
  -> MoveIt /move_action
  -> FollowJointTrajectory bridge
  -> /joint_command
  -> Isaac ROS2 Subscribe Joint State
  -> Isaac Articulation Controller
  -> UR3e articulation

Isaac
  -> /joint_states
  -> /clock
  -> ROS 2 / MoveIt / RViz
```

Pick/place object commands use a separate topic:

```text
moveit_scenario_runner
  -> std_msgs/String /pick_place_command
  -> Isaac PickPlaceObjectController
```

Supported command payloads:

```text
attach:pick_cube_red
detach:pick_cube_red
attach:pick_cube_blue
detach:pick_cube_blue
```

## How to Run

Start Isaac Sim with the demo scene:

```bash
cd /root/ur3e-isaac-sim-digital-twin
./scripts/run_pick_place_demo_scene.sh
```

Start MoveIt2, RViz, and the FollowJointTrajectory bridge:

```bash
cd /root/ur3e-isaac-sim-digital-twin
./scripts/run_moveit_isaac_stack.sh
```

Run the scripted scenario:

```bash
cd /root/ur3e-isaac-sim-digital-twin
./scripts/run_moveit_scenario.sh scenarios/pick_place_blocks.yaml
```

Verify ROS 2 topics:

```bash
cd /root/ur3e-isaac-sim-digital-twin
source scripts/setup_fastdds.sh
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 topic list | sort | grep -E 'joint_command|joint_states|pick_place_command|clock'
```

Expected topics:

```text
/clock
/joint_command
/joint_states
/pick_place_command
```

## Recorded Video

The latest recorded video is:

```text
docs/media/pick_place_moveit_isaac_demo_latest.mp4
```

File properties verified with `ffprobe`:

```text
codec: h264
resolution: 1920x1080
frame rate: 15 fps
duration: 75 seconds
```

The video shows the current end-to-end stack:

- Isaac scene open
- UR3e in the colored-object workspace
- MoveIt scenario sending trajectory goals
- Isaac receiving and executing robot joint commands
- pick/place command path being exercised

## Important Current Limitation

Do not present this as a completed physical grasp demo yet.

The robot motion sync works, but the object grasp is not validated. The current Isaac controller intentionally refuses `attach` if the measured end-effector/object distance is too large. This avoids faking a pick by teleporting the object to the gripper or to the target.

Observed attach diagnostics:

```text
Attach distance for pick_cube_red: about 0.4-0.5 m
Refused attach for pick_cube_red: end-effector is not close enough
```

This means the current MoveIt target/tool-frame/Isaac USD pose alignment is not calibrated enough for a real pick.

## What Was Fixed from the Fake Version

Earlier, `detach` placed the cube directly at a fixed target. That looked like the object moved by script rather than by robot motion.

The current code no longer does that. It:

- receives explicit `attach` and `detach` commands over ROS 2
- checks object/end-effector distance before attach
- refuses attach when the robot is not close enough
- keeps detach at the current object pose instead of teleporting to a fixed place
- logs diagnostic distances and closest robot prims for calibration

## Why the Grasp Still Fails

The Isaac USD prim origin for `/ur3e/wrist_3_link` is not the same as the visible gripper/tool contact point. The MoveIt URDF frame and Isaac USD runtime mesh/frame need a calibrated tool transform.

The likely missing pieces are:

- correct TCP/end-effector frame in Isaac
- matching MoveIt `ik_link_name` to the Isaac TCP
- a real or simulated gripper/suction tool
- collision geometry and grasp constraint
- object pose feedback in the same frame as MoveIt planning

## Next Engineering Steps

1. Add a dedicated TCP prim under the UR3e USD, for example `/ur3e/tcp`.
2. Calibrate TCP transform relative to `wrist_3_link`.
3. Update MoveIt IK requests or SRDF to use the matching TCP/tool link.
4. Add a gripper or suction tool asset.
5. Replace the kinematic object-follow behavior with one of:
   - Isaac surface gripper
   - physics fixed joint during grasp
   - contact-driven suction constraint
6. Add object pose publisher from Isaac to ROS 2.
7. Generate pick/place goals from object pose instead of hard-coded joint targets.
8. Record a new video only after attach succeeds because the robot is actually close enough.

## Honest Demo Claim

Safe claim:

```text
MoveIt2 trajectory execution is synced into Isaac Sim for UR3e, with a colored-object scene and a guarded pick/place command path.
```

Do not claim yet:

```text
The robot physically grasps and places the cube.
```

