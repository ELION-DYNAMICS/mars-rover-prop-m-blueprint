from __future__ import annotations

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import JointState


class SimEncoderNode(Node):
    """
    Simulation wheel encoder stub.

    Publishes:
      /joint_states (sensor_msgs/JointState)

    This exists so higher layers can run before sim integration is finished.
    Later you will replace this by:
      - subscribing simulator joint states and forwarding them, or
      - reading real encoders on hardware.
    """

    def __init__(self) -> None:
        super().__init__("sim_encoder")

        self.declare_parameter("topic", "/joint_states")
        self.declare_parameter("pub_rate_hz", 50.0)
        self.declare_parameter("left_joint", "wheel_left_joint")
        self.declare_parameter("right_joint", "wheel_right_joint")

        topic = str(self.get_parameter("topic").value)
        rate = float(self.get_parameter("pub_rate_hz").value)
        self.left = str(self.get_parameter("left_joint").value)
        self.right = str(self.get_parameter("right_joint").value)

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self.pub = self.create_publisher(JointState, topic, qos)
        self.timer = self.create_timer(1.0 / rate, self._tick)

        self.get_logger().info(f"sim_encoder publishing {topic} at {rate:.1f} Hz")

    def _tick(self) -> None:
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = [self.left, self.right]

        # Stub: no motion
        msg.position = [0.0, 0.0]
        msg.velocity = [0.0, 0.0]
        msg.effort = [0.0, 0.0]

        self.pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = SimEncoderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
