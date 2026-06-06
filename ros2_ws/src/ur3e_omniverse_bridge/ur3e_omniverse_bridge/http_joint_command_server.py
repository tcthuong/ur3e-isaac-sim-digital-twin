import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

from ur3e_omniverse_bridge.joint_utils import joint_payload_to_names_positions, resolve_joint_names


class JointCommandHttpNode(Node):
    def __init__(self):
        super().__init__("http_joint_command_server")
        self.declare_parameter("host", "0.0.0.0")
        self.declare_parameter("port", 8000)
        self.declare_parameter("output_topic", "/joint_command")
        self.declare_parameter("name_mode", "ros")
        self.declare_parameter("joint_names_csv", "")

        self.output_topic = self.get_parameter("output_topic").value
        self.default_names = resolve_joint_names(
            self.get_parameter("name_mode").value,
            self.get_parameter("joint_names_csv").value,
        )
        self.publisher = self.create_publisher(JointState, self.output_topic, 10)

        host = self.get_parameter("host").value
        port = int(self.get_parameter("port").value)
        self.server = self._make_server(host, port)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()

        self.get_logger().info(
            f"HTTP joint command server listening on http://{host}:{port}; publishing to {self.output_topic}"
        )

    def _make_server(self, host: str, port: int):
        node = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                node.get_logger().info(fmt % args)

            def do_GET(self):
                if self.path != "/health":
                    self.send_error(404, "Use POST /joint_command or GET /health")
                    return
                self._send_json(200, {"ok": True, "topic": node.output_topic})

            def do_POST(self):
                if self.path != "/joint_command":
                    self.send_error(404, "Use POST /joint_command")
                    return

                content_length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(content_length)
                try:
                    payload = json.loads(raw.decode("utf-8"))
                    names, positions = joint_payload_to_names_positions(payload, node.default_names)
                    node.publish_joint_command(names, positions)
                except Exception as exc:
                    self._send_json(400, {"ok": False, "error": str(exc)})
                    return

                self._send_json(200, {"ok": True, "joints": names})

            def _send_json(self, status, payload):
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        return ThreadingHTTPServer((host, port), Handler)

    def publish_joint_command(self, names, positions):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(names)
        msg.position = [float(value) for value in positions]
        self.publisher.publish(msg)

    def destroy_node(self):
        self.server.shutdown()
        self.server.server_close()
        return super().destroy_node()


def main():
    rclpy.init()
    node = JointCommandHttpNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
