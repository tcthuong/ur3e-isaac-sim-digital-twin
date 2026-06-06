import time
from pathlib import Path
from typing import Dict, Iterable, List

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, JointConstraint, MoveItErrorCodes
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from std_msgs.msg import String
import yaml

from ur3e_omniverse_bridge.joint_utils import ROS_UR3E_JOINT_NAMES


class MoveItScenarioRunner(Node):
    def __init__(self):
        super().__init__("moveit_scenario_runner")
        self.declare_parameter("scenario_file", "")
        self.client = ActionClient(self, MoveGroup, "/move_action")
        self.pick_place_publisher = self.create_publisher(String, "/pick_place_command", 10)

    def run(self):
        scenario_path = Path(str(self.get_parameter("scenario_file").value)).expanduser()
        if not scenario_path:
            raise RuntimeError("scenario_file parameter is required")
        if not scenario_path.exists():
            raise RuntimeError(f"Scenario file not found: {scenario_path}")

        scenario = self.load_scenario(scenario_path)
        defaults = scenario.get("defaults", {})
        named_targets = scenario.get("named_targets", {})
        steps = scenario.get("steps", [])
        if not isinstance(named_targets, dict) or not named_targets:
            raise RuntimeError("Scenario must define named_targets")
        if not isinstance(steps, list) or not steps:
            raise RuntimeError("Scenario must define steps")

        self.get_logger().info(f"Loaded scenario '{scenario.get('name', scenario_path.name)}'")
        self.get_logger().info("Waiting for MoveIt /move_action")
        self.client.wait_for_server()

        for index, step in enumerate(steps, start=1):
            self.run_step(index, step, defaults, named_targets)

        self.get_logger().info("Scenario finished")
        return 0

    def load_scenario(self, path: Path) -> Dict:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        if not isinstance(data, dict):
            raise RuntimeError("Scenario file must contain a YAML object")
        return data

    def run_step(self, index: int, step: object, defaults: Dict, named_targets: Dict[str, List[float]]):
        if not isinstance(step, dict) or len(step) != 1:
            raise RuntimeError(f"Invalid scenario step #{index}: {step}")

        action, value = next(iter(step.items()))
        if action == "move_joints":
            positions = self.resolve_target(value, named_targets)
            self.get_logger().info(f"Step {index}: move_joints {value}")
            result = self.send_joint_goal(positions, defaults)
            if result.error_code.val != MoveItErrorCodes.SUCCESS:
                raise RuntimeError(f"MoveIt step #{index} failed: error_code={result.error_code.val}")
            time.sleep(float(defaults.get("pause_seconds", 0.0)))
        elif action == "wait":
            self.get_logger().info(f"Step {index}: wait {value}s")
            time.sleep(float(value))
        elif action == "attach":
            self.get_logger().info(f"Step {index}: attach object '{value}'")
            self.publish_pick_place_command("attach", str(value))
        elif action == "detach":
            self.get_logger().info(f"Step {index}: detach object '{value}'")
            self.publish_pick_place_command("detach", str(value))
        else:
            raise RuntimeError(f"Unknown scenario action '{action}' in step #{index}")

    def publish_pick_place_command(self, action: str, object_name: str):
        message = String()
        message.data = f"{action}:{object_name}"
        self.pick_place_publisher.publish(message)
        time.sleep(0.1)

    def resolve_target(self, value: object, named_targets: Dict[str, List[float]]) -> List[float]:
        if isinstance(value, str):
            if value not in named_targets:
                raise RuntimeError(f"Unknown named target: {value}")
            return [float(item) for item in named_targets[value]]
        if isinstance(value, Iterable):
            return [float(item) for item in value]
        raise RuntimeError(f"Invalid move_joints target: {value}")

    def send_joint_goal(self, positions: List[float], defaults: Dict):
        goal = MoveGroup.Goal()
        goal.request.group_name = str(defaults.get("group_name", "ur_manipulator"))
        goal.request.pipeline_id = str(defaults.get("pipeline_id", "ompl"))
        goal.request.planner_id = str(defaults.get("planner_id", "RRTConnectkConfigDefault"))
        goal.request.num_planning_attempts = int(defaults.get("planning_attempts", 5))
        goal.request.allowed_planning_time = float(defaults.get("planning_time", 5.0))
        goal.request.max_velocity_scaling_factor = float(defaults.get("velocity_scale", 0.25))
        goal.request.max_acceleration_scaling_factor = float(defaults.get("acceleration_scale", 0.25))
        goal.request.goal_constraints = [self.joint_constraints(positions)]
        goal.planning_options.plan_only = bool(defaults.get("plan_only", False))
        goal.planning_options.look_around = False
        goal.planning_options.replan = False

        future = self.client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()
        if not goal_handle.accepted:
            raise RuntimeError("MoveIt rejected scenario goal")

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        return result_future.result().result

    def joint_constraints(self, positions: List[float]) -> Constraints:
        if len(positions) != len(ROS_UR3E_JOINT_NAMES):
            raise RuntimeError(f"Expected {len(ROS_UR3E_JOINT_NAMES)} joint positions, got {len(positions)}")

        constraints = Constraints()
        for name, position in zip(ROS_UR3E_JOINT_NAMES, positions):
            joint = JointConstraint()
            joint.joint_name = name
            joint.position = float(position)
            joint.tolerance_above = 0.01
            joint.tolerance_below = 0.01
            joint.weight = 1.0
            constraints.joint_constraints.append(joint)
        return constraints


def main():
    rclpy.init()
    node = MoveItScenarioRunner()
    try:
        raise SystemExit(node.run())
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
