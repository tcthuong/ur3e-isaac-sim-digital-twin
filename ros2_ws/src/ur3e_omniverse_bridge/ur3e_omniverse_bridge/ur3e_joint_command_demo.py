import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

from ur3e_omniverse_bridge.joint_utils import resolve_joint_names, sine_positions


class UR3eJointCommandDemo(Node):
    def __init__(self):
        super().__init__("ur3e_joint_command_demo")
        self.declare_parameter("topic", "/joint_command")
        self.declare_parameter("name_mode", "ros")
        self.declare_parameter("joint_names_csv", "")
        self.declare_parameter("rate_hz", 30.0)
        self.declare_parameter("amplitude", 0.35)
        self.declare_parameter("speed", 0.6)

        topic = self.get_parameter("topic").value
        name_mode = self.get_parameter("name_mode").value
        custom_names = self.get_parameter("joint_names_csv").value
        self.joint_names = resolve_joint_names(name_mode, custom_names)
        self.amplitude = float(self.get_parameter("amplitude").value)
        self.speed = float(self.get_parameter("speed").value)
        rate_hz = max(1.0, float(self.get_parameter("rate_hz").value))

        self.publisher = self.create_publisher(JointState, topic, 10)
        self.started_at = time.monotonic()
        self.timer = self.create_timer(1.0 / rate_hz, self.publish_command)

        self.get_logger().info(
            f"Publishing UR3e demo JointState to {topic} with joints: {', '.join(self.joint_names)}"
        )

    def publish_command(self):
        elapsed = time.monotonic() - self.started_at
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(self.joint_names)
        msg.position = sine_positions(
            elapsed_seconds=elapsed,
            joint_count=len(self.joint_names),
            amplitude=self.amplitude,
            speed=self.speed,
        )
        self.publisher.publish(msg)


def main():
    rclpy.init()
    node = UR3eJointCommandDemo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
