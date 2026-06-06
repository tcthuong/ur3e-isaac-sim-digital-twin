# Training Roadmap with Isaac Lab

First goal: make external app control and Isaac Sim sync reliable.

Training comes after that. For robot arms, the usual route is:

1. Build a stable Isaac Sim articulation with correct joint names, limits, drives, mass, collision, and sensors.
2. Define a task such as reaching a target, following a trajectory, pick-and-place, or avoiding obstacles.
3. Train a policy in Isaac Lab or another RL/imitation-learning stack.
4. Export the policy.
5. Run policy inference as a ROS 2 node or inside Isaac Sim.
6. Send policy actions to `/joint_command` or a lower-level controller.

Official references:

- Isaac Sim ROS 2 RL tutorial: https://docs.isaacsim.omniverse.nvidia.com/latest/ros2_tutorials/tutorial_ros2_rl_controller.html
- Isaac Lab getting started: https://docs.nvidia.com/learning/physical-ai/getting-started-with-isaac-lab/latest/index.html

## Suggested Milestones

### Milestone 1: Manual Joint Control

Use `ur3e_joint_command_demo` and `external_joint_state_relay` until Isaac Sim reliably follows commands.

Done when:

- `/joint_command` is visible with `ros2 topic echo`.
- UR3e moves in Isaac Sim.
- Joint directions and limits look correct.

### Milestone 2: MoveIt Planning

Use Universal Robots MoveIt config for UR3e.

Done when:

- RViz can plan for `ur3e`.
- Planned trajectories can be mirrored into Isaac Sim.
- Collision objects can be added without breaking planning.

### Milestone 3: Closed Loop Simulation

Publish Isaac Sim joint states back to ROS 2 as `/joint_states`.

Done when:

- External app sends command.
- Isaac Sim moves.
- ROS receives simulated joint feedback.

### Milestone 4: Policy Training

Move into Isaac Lab.

Start with a simple reach task before pick-and-place. A reach task is easier to debug because the action is joint velocity or target joint position and the reward can be distance-to-target plus smoothness penalties.

Done when:

- A trained policy reaches random targets in simulation.
- The same policy can be run in inference mode.
- The policy action can be adapted to `/joint_command`.

## Safety Note

Training policies in simulation is not the same as controlling a real UR3e. For real hardware, add:

- speed limits
- workspace limits
- collision checks
- emergency stop
- operator confirmation
- controller-side safety constraints

Never send unvalidated policy actions directly to physical hardware.
