import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

from ur3e_omniverse_bridge.joint_utils import map_joint_positions, resolve_joint_names


class ExternalJointStateRelay(Node):
    def __init__(self):
        super().__init__("external_joint_state_relay")
        self.declare_parameter("input_topic", "/external_joint_states")
        self.declare_parameter("output_topic", "/joint_command")
        self.declare_parameter("source_name_mode", "ros")
        self.declare_parameter("target_name_mode", "ros")
        self.declare_parameter("source_joint_names_csv", "")
        self.declare_parameter("target_joint_names_csv", "")

        input_topic = self.get_parameter("input_topic").value
        output_topic = self.get_parameter("output_topic").value
        self.source_names = resolve_joint_names(
            self.get_parameter("source_name_mode").value,
            self.get_parameter("source_joint_names_csv").value,
        )
        self.target_names = resolve_joint_names(
            self.get_parameter("target_name_mode").value,
            self.get_parameter("target_joint_names_csv").value,
        )

        self.publisher = self.create_publisher(JointState, output_topic, 10)
        self.subscription = self.create_subscription(JointState, input_topic, self.on_joint_state, 10)

        self.get_logger().info(
            f"Relaying {input_topic} -> {output_topic}; source: {', '.join(self.source_names)}; "
            f"target: {', '.join(self.target_names)}"
        )

    def on_joint_state(self, msg: JointState):
        try:
            names, positions = map_joint_positions(
                incoming_names=msg.name,
                incoming_positions=msg.position,
                source_names=self.source_names,
                target_names=self.target_names,
            )
        except ValueError as exc:
            self.get_logger().warn(str(exc), throttle_duration_sec=2.0)
            return

        out = JointState()
        out.header.stamp = self.get_clock().now().to_msg()
        out.name = names
        out.position = positions
        self.publisher.publish(out)


def main():
    rclpy.init()
    node = ExternalJointStateRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
