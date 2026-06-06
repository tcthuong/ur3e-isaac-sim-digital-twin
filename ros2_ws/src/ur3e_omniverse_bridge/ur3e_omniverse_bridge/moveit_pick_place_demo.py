import time
from typing import Iterable, List

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, JointConstraint, MoveItErrorCodes
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from ur3e_omniverse_bridge.joint_utils import ROS_UR3E_JOINT_NAMES


PICK_PLACE_STEPS = [
    ("home", [0.0, -1.0, 1.15, -0.35, 0.55, 0.0]),
    ("approach_pick", [0.35, -1.05, 1.25, -0.45, 0.62, 0.15]),
    ("descend_pick", [0.35, -1.23, 1.45, -0.62, 0.62, 0.15]),
    ("lift_object", [0.35, -0.92, 1.05, -0.32, 0.62, 0.15]),
    ("approach_place", [-0.45, -0.92, 1.05, -0.32, 0.62, -0.2]),
    ("descend_place", [-0.45, -1.2, 1.42, -0.58, 0.62, -0.2]),
    ("release_retreat", [-0.45, -0.9, 1.02, -0.28, 0.62, -0.2]),
    ("home", [0.0, -1.0, 1.15, -0.35, 0.55, 0.0]),
]


class MoveItPickPlaceDemo(Node):
    def __init__(self):
        super().__init__("moveit_pick_place_demo")
        self.declare_parameter("group_name", "ur_manipulator")
        self.declare_parameter("pipeline_id", "ompl")
        self.declare_parameter("planner_id", "RRTConnectkConfigDefault")
        self.declare_parameter("plan_only", False)
        self.declare_parameter("pause_seconds", 0.5)
        self.declare_parameter("velocity_scale", 0.25)
        self.declare_parameter("acceleration_scale", 0.25)
        self.client = ActionClient(self, MoveGroup, "/move_action")

    def run(self):
        self.get_logger().info("Waiting for MoveIt /move_action")
        self.client.wait_for_server()

        for label, positions in PICK_PLACE_STEPS:
            self.get_logger().info(f"MoveIt step: {label}")
            result = self.send_joint_goal(positions)
            if result.error_code.val != MoveItErrorCodes.SUCCESS:
                self.get_logger().error(f"MoveIt step '{label}' failed: error_code={result.error_code.val}")
                return 1
            time.sleep(float(self.get_parameter("pause_seconds").value))

        self.get_logger().info("Pick-place joint-space demo finished")
        return 0

    def send_joint_goal(self, positions: Iterable[float]):
        goal = MoveGroup.Goal()
        goal.request.group_name = self.get_parameter("group_name").value
        goal.request.pipeline_id = self.get_parameter("pipeline_id").value
        goal.request.planner_id = self.get_parameter("planner_id").value
        goal.request.num_planning_attempts = 5
        goal.request.allowed_planning_time = 5.0
        goal.request.max_velocity_scaling_factor = float(self.get_parameter("velocity_scale").value)
        goal.request.max_acceleration_scaling_factor = float(self.get_parameter("acceleration_scale").value)
        goal.request.goal_constraints = [self.joint_constraints(list(positions))]
        goal.planning_options.plan_only = bool(self.get_parameter("plan_only").value)
        goal.planning_options.look_around = False
        goal.planning_options.replan = False

        future = self.client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()
        if not goal_handle.accepted:
            raise RuntimeError("MoveIt rejected goal")

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        return result_future.result().result

    def joint_constraints(self, positions: List[float]) -> Constraints:
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
    node = MoveItPickPlaceDemo()
    try:
        raise SystemExit(node.run())
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
