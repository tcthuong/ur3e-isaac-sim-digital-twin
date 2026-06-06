import time
from typing import Dict, List

from control_msgs.action import FollowJointTrajectory
import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectoryPoint

from ur3e_omniverse_bridge.joint_utils import (
    ROS_UR3E_JOINT_NAMES,
    duration_to_seconds,
    map_joint_positions,
    parse_names,
    resolve_joint_names,
)


class FollowJointTrajectoryToJointCommand(Node):
    def __init__(self):
        super().__init__("follow_joint_trajectory_to_joint_command")
        self.declare_parameter("action_name", "/scaled_joint_trajectory_controller/follow_joint_trajectory")
        self.declare_parameter("output_topic", "/joint_command")
        self.declare_parameter("joint_state_topic", "/joint_states")
        self.declare_parameter("source_joint_names_csv", ",".join(ROS_UR3E_JOINT_NAMES))
        self.declare_parameter("target_joint_names_csv", "")
        self.declare_parameter("target_name_mode", "preserve")
        self.declare_parameter("playback_rate_hz", 100.0)

        action_name = self.get_parameter("action_name").value
        output_topic = self.get_parameter("output_topic").value
        joint_state_topic = self.get_parameter("joint_state_topic").value
        self.source_names = parse_names(self.get_parameter("source_joint_names_csv").value)
        self.target_names_csv = self.get_parameter("target_joint_names_csv").value
        self.target_name_mode = self.get_parameter("target_name_mode").value
        self.rate_hz = max(10.0, float(self.get_parameter("playback_rate_hz").value))

        self.publisher = self.create_publisher(JointState, output_topic, 10)
        self.latest_joint_state: Dict[str, float] = {}
        self.create_subscription(JointState, joint_state_topic, self.on_joint_state, 10)

        callback_group = ReentrantCallbackGroup()
        self.action_server = ActionServer(
            self,
            FollowJointTrajectory,
            action_name,
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=callback_group,
        )
        self.get_logger().info(f"FollowJointTrajectory bridge ready: {action_name} -> {output_topic}")

    def on_joint_state(self, msg: JointState):
        for index, name in enumerate(msg.name):
            if index < len(msg.position):
                self.latest_joint_state[name] = float(msg.position[index])

    def goal_callback(self, goal_request):
        trajectory = goal_request.trajectory
        if not trajectory.joint_names or not trajectory.points:
            self.get_logger().warn("Rejected trajectory goal with no joints or no points")
            return GoalResponse.REJECT

        missing = [name for name in self.source_names if name not in trajectory.joint_names]
        if missing:
            self.get_logger().warn(f"Rejected trajectory missing joints: {', '.join(missing)}")
            return GoalResponse.REJECT

        return GoalResponse.ACCEPT

    def cancel_callback(self, _goal_handle):
        self.get_logger().info("Cancel requested for trajectory execution")
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        trajectory = goal_handle.request.trajectory
        self.get_logger().info(
            f"Executing trajectory with {len(trajectory.points)} points: {', '.join(trajectory.joint_names)}"
        )

        target_names = self.resolve_target_names()
        start_time = time.monotonic()
        period = 1.0 / self.rate_hz
        last_point = trajectory.points[-1]

        while rclpy.ok():
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                return self.result(FollowJointTrajectory.Result.INVALID_GOAL, "Trajectory canceled")

            elapsed = time.monotonic() - start_time
            point = self.point_at_time(trajectory.points, elapsed)
            self.publish_point(trajectory.joint_names, point, target_names)
            goal_handle.publish_feedback(self.feedback(trajectory.joint_names, point))

            if elapsed >= duration_to_seconds(last_point.time_from_start):
                break

            time.sleep(period)

        self.publish_point(trajectory.joint_names, last_point, target_names)
        goal_handle.succeed()
        self.get_logger().info("Trajectory execution finished")
        return self.result(FollowJointTrajectory.Result.SUCCESSFUL, "Trajectory forwarded to Isaac Sim")

    def resolve_target_names(self) -> List[str]:
        custom_target = parse_names(self.target_names_csv)
        if custom_target:
            return custom_target
        if (self.target_name_mode or "preserve").strip().lower() == "preserve":
            return []
        return resolve_joint_names(self.target_name_mode)

    def point_at_time(self, points: List[JointTrajectoryPoint], elapsed: float) -> JointTrajectoryPoint:
        selected = points[-1]
        for point in points:
            if duration_to_seconds(point.time_from_start) >= elapsed:
                selected = point
                break
        return selected

    def publish_point(self, incoming_names: List[str], point: JointTrajectoryPoint, target_names: List[str]):
        names, positions = map_joint_positions(
            incoming_names=incoming_names,
            incoming_positions=point.positions,
            source_names=self.source_names,
            target_names=target_names,
        )
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = names
        msg.position = positions
        self.publisher.publish(msg)

    def feedback(self, names: List[str], desired: JointTrajectoryPoint) -> FollowJointTrajectory.Feedback:
        feedback = FollowJointTrajectory.Feedback()
        feedback.header.stamp = self.get_clock().now().to_msg()
        feedback.joint_names = list(names)
        feedback.desired = desired
        feedback.actual.positions = [self.latest_joint_state.get(name, 0.0) for name in names]
        feedback.error.positions = [
            desired.positions[index] - feedback.actual.positions[index]
            for index in range(min(len(desired.positions), len(feedback.actual.positions)))
        ]
        return feedback

    def result(self, code: int, text: str) -> FollowJointTrajectory.Result:
        result = FollowJointTrajectory.Result()
        result.error_code = code
        result.error_string = text
        return result


def main():
    rclpy.init()
    node = FollowJointTrajectoryToJointCommand()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
