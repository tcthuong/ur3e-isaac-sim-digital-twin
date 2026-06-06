# Training and Skill Solution Directions

This note captures practical paths for turning the current UR3e Isaac Sim digital twin into a trainable or semi-autonomous robot demo.

## Current Baseline

The repo already supports:

- Isaac Sim UR3e digital twin.
- ROS 2 command sync through `/joint_command`.
- Isaac state sync through `/joint_states` and `/clock`.
- MoveIt2 planning with UR3e `ur_manipulator`.
- MoveIt2 `Plan and Execute` routed into Isaac through a fake `FollowJointTrajectory` controller bridge.
- A scripted pick-place style joint-space demo.

Current data flow:

```text
MoveIt2 / app / demo
  -> FollowJointTrajectory or /joint_command
  -> Isaac Sim Action Graph
  -> UR3e articulation
  -> /joint_states
  -> MoveIt2 / app sync
```

## Fast Demo Direction

The fastest useful demo is not full reinforcement learning. It is a skill/planner pipeline:

```text
High-level skill
  -> choose target pose or joint target
  -> MoveIt2 plans collision-aware motion
  -> trajectory bridge streams command to Isaac
  -> Isaac state sync validates execution
```

This gives a working robot behavior quickly and keeps later training options open.

## Demo 1: Scripted Pick-Place Skill

Goal: show the robot performing a repeatable pick-place motion in Isaac using MoveIt2.

Run:

```bash
./scripts/run_ur3e_ros2_bridge.sh
./scripts/run_moveit_isaac_stack.sh
./scripts/run_moveit_pick_place_demo.sh
```

What it proves:

- MoveIt2 can plan for UR3e.
- MoveIt2 execution can drive Isaac through `FollowJointTrajectory`.
- Isaac publishes state back to ROS 2.

Limit:

- Current UR3e asset does not include a real gripper, so this is arm motion only.

Next upgrade:

- Add a gripper asset.
- Add table and cube.
- Add attach/detach logic during pick/place.

## Demo 2: External App Skill API

Goal: make a small app call robot skills without knowing MoveIt internals.

Proposed interface:

```text
POST /skill/pick_place
{
  "pick": {"x": 0.35, "y": 0.10, "z": 0.12},
  "place": {"x": -0.35, "y": 0.15, "z": 0.12}
}
```

Backend behavior:

```text
HTTP request
  -> skill server
  -> generate waypoints
  -> call MoveIt2
  -> execute through FollowJointTrajectory bridge
  -> return success/failure
```

Implementation steps:

1. Add `skill_server.py` ROS 2 node or FastAPI bridge.
2. Convert pick/place request into joint-space or Cartesian MoveIt goals.
3. Execute through `/move_action`.
4. Report current state from `/joint_states`.

This is the best path for a product-style demo.

## Demo 3: Imitation Data Collection

Goal: collect demonstrations now, train later.

Record every executed MoveIt trajectory:

```text
timestamp
joint_names
joint_positions
joint_velocities
target label
skill phase
object pose
success/failure
```

Initial dataset can come from:

- `run_moveit_pick_place_demo.sh`
- RViz interactive marker plans
- manual HTTP `/joint_command` commands

Suggested output format:

```text
data/demos/YYYYMMDD_HHMMSS_pick_place/
  metadata.json
  joint_states.csv
  joint_commands.csv
  planned_trajectory.json
```

Training later:

- Behavior cloning: observation -> next joint target.
- Skill classifier: current state -> next phase.
- Residual policy: model adjusts MoveIt-generated path.

## Demo 4: Isaac Lab RL Environment

Goal: full training with vectorized simulation.

Use this only after the scene is stable.

Required work:

1. Convert scene to an Isaac Lab task.
2. Add table, object, target zone, and gripper.
3. Define observations:
   - joint positions
   - joint velocities
   - end-effector pose
   - object pose
   - target pose
4. Define actions:
   - joint position deltas, or
   - end-effector deltas
5. Define rewards:
   - distance to object
   - successful grasp
   - object lift height
   - distance to placement target
6. Add reset/randomization:
   - object position
   - target position
   - robot initial pose

Recommended algorithms:

- PPO for first Isaac Lab baseline.
- SAC only after the task is stable.
- Imitation pretraining if demonstrations are available.

## Recommended Roadmap

### Phase 1: Demo Fast

- Use existing MoveIt2 bridge.
- Keep pick-place as scripted joint/waypoint skill.
- Record a clean demo video.
- Add simple HTTP skill endpoint.

### Phase 2: Make It Object-Aware

- Add table and cube.
- Add camera or object pose publisher.
- Generate pick/place targets from object pose.
- Add gripper or fake attach/detach.

### Phase 3: Collect Data

- Record MoveIt plans and executions.
- Store observations and commands.
- Label skill phases.
- Save success/failure.

### Phase 4: Train

- Start with behavior cloning from demos.
- Compare against scripted skill baseline.
- Move to Isaac Lab RL only when task reset/reward is robust.

## Immediate Next Tasks

1. Add table and cube USD scene.
2. Add fake gripper or attach/detach logic.
3. Add `skill_server` endpoint:
   - `/skill/home`
   - `/skill/pick_place`
   - `/state`
4. Add demo recorder:
   - `/joint_states`
   - `/joint_command`
   - `/display_planned_path`
   - `/move_action` result
5. Record 3-5 pick-place demonstrations for future imitation training.

