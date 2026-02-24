from __future__ import annotations

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from geometry_msgs.msg import Twist


class SimMotorInterfaceNode(Node):
    """
    Simulation motor interface stub.

    Subscribes:
      /cmd_vel_safe

    Publishes:
      /driver/motor_cmd_vel (for traceability; later becomes wheel velocity/torque commands)

    This is a boundary marker:
      control layer ends at /cmd_vel_safe,
      driver layer begins here.
    """

    def __init__(self) -> None:
        super().__init__("sim_motor_interface")

        self.declare_parameter("in_topic", "/cmd_vel_safe")
        self.declare_parameter("out_topic", "/driver/motor_cmd_vel")

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        in_topic = str(self.get_parameter("in_topic").value)
        out_topic = str(self.get_parameter("out_topic").value)

        self.sub = self.create_subscription(Twist, in_topic, self._on_cmd, qos)
        self.pub = self.create_publisher(Twist, out_topic, qos)

        self.get_logger().info(f"sim_motor_interface: {in_topic} -> {out_topic}")

    def _on_cmd(self, msg: Twist) -> None:
        self.pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = SimMotorInterfaceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
