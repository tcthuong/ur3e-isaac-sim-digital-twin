import time
from typing import List

import rclpy
from moveit_msgs.msg import DisplayTrajectory
from rclpy.node import Node
from sensor_msgs.msg import JointState

from ur3e_omniverse_bridge.joint_utils import (
    duration_to_seconds,
    map_joint_positions,
    parse_names,
    resolve_joint_names,
)


class DisplayTrajectoryToJointCommand(Node):
    def __init__(self):
        super().__init__("display_trajectory_to_joint_command")
        self.declare_parameter("input_topic", "/display_planned_path")
        self.declare_parameter("output_topic", "/joint_command")
        self.declare_parameter("target_name_mode", "preserve")
        self.declare_parameter("target_joint_names_csv", "")
        self.declare_parameter("playback_rate_hz", 60.0)
        self.declare_parameter("loop", False)

        input_topic = self.get_parameter("input_topic").value
        output_topic = self.get_parameter("output_topic").value
        self.target_name_mode = self.get_parameter("target_name_mode").value
        self.target_names_csv = self.get_parameter("target_joint_names_csv").value
        self.loop = bool(self.get_parameter("loop").value)
        rate_hz = max(1.0, float(self.get_parameter("playback_rate_hz").value))

        self.publisher = self.create_publisher(JointState, output_topic, 10)
        self.subscription = self.create_subscription(DisplayTrajectory, input_topic, self.on_display_trajectory, 10)
        self.timer = self.create_timer(1.0 / rate_hz, self.on_timer)

        self.source_names: List[str] = []
        self.target_names: List[str] = []
        self.points = []
        self.started_at = None

        self.get_logger().info(f"Waiting for MoveIt DisplayTrajectory on {input_topic}; output: {output_topic}")

    def on_display_trajectory(self, msg: DisplayTrajectory):
        if not msg.trajectory:
            self.get_logger().warn("DisplayTrajectory contains no trajectories")
            return

        joint_trajectory = msg.trajectory[-1].joint_trajectory
        if not joint_trajectory.joint_names or not joint_trajectory.points:
            self.get_logger().warn("DisplayTrajectory has no joint trajectory points")
            return

        self.source_names = list(joint_trajectory.joint_names)
        custom_target = parse_names(self.target_names_csv)
        if custom_target:
            self.target_names = custom_target
        elif (self.target_name_mode or "preserve").strip().lower() == "preserve":
            self.target_names = []
        else:
            self.target_names = resolve_joint_names(self.target_name_mode)

        self.points = list(joint_trajectory.points)
        self.started_at = time.monotonic()
        self.get_logger().info(
            f"Playing {len(self.points)} trajectory points from MoveIt with joints: {', '.join(self.source_names)}"
        )

    def on_timer(self):
        if self.started_at is None or not self.points:
            return

        elapsed = time.monotonic() - self.started_at
        point = self.points[-1]
        for candidate in self.points:
            point_time = duration_to_seconds(candidate.time_from_start)
            if point_time >= elapsed:
                point = candidate
                break

        self.publish_point(point)

        last_time = duration_to_seconds(self.points[-1].time_from_start)
        if elapsed >= last_time:
            if self.loop:
                self.started_at = time.monotonic()
            else:
                self.started_at = None

    def publish_point(self, point):
        try:
            names, positions = map_joint_positions(
                incoming_names=self.source_names,
                incoming_positions=point.positions,
                source_names=self.source_names,
                target_names=self.target_names,
            )
        except ValueError as exc:
            self.get_logger().warn(str(exc), throttle_duration_sec=2.0)
            return

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = names
        msg.position = positions
        self.publisher.publish(msg)


def main():
    rclpy.init()
    node = DisplayTrajectoryToJointCommand()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
