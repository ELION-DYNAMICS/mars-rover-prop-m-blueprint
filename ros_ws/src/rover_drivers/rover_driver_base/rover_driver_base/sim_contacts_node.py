from __future__ import annotations

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from std_msgs.msg import Bool


class SimContactsNode(Node):
    """
    Simulation contact sensor stub.

    Publishes:
      /contacts/left
      /contacts/right
      /contacts/front

    Default: no contact events.
    Later: bridge from simulator contact sensors.
    """

    def __init__(self) -> None:
        super().__init__("sim_contacts")

        self.declare_parameter("pub_rate_hz", 20.0)
        self.declare_parameter("left_topic", "/contacts/left")
        self.declare_parameter("right_topic", "/contacts/right")
        self.declare_parameter("front_topic", "/contacts/front")

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        left_topic = str(self.get_parameter("left_topic").value)
        right_topic = str(self.get_parameter("right_topic").value)
        front_topic = str(self.get_parameter("front_topic").value)

        self.pub_left = self.create_publisher(Bool, left_topic, qos)
        self.pub_right = self.create_publisher(Bool, right_topic, qos)
        self.pub_front = self.create_publisher(Bool, front_topic, qos)

        rate = float(self.get_parameter("pub_rate_hz").value)
        self.timer = self.create_timer(1.0 / rate, self._tick)

        self.get_logger().info(
            f"sim_contacts publishing {left_topic}, {right_topic}, {front_topic}"
        )

    def _tick(self) -> None:
        msg = Bool()
        msg.data = False
        self.pub_left.publish(msg)
        self.pub_right.publish(msg)
        self.pub_front.publish(msg)


def main() -> None:
    rclpy.init()
    node = SimContactsNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
