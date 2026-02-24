from __future__ import annotations

import math
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import Imu
from builtin_interfaces.msg import Time as RosTime


def now_msg(node: Node) -> RosTime:
    t = node.get_clock().now().to_msg()
    return t


class SimImuNode(Node):
    """
    Simulation IMU stub.

    Publishes:
      /imu/data (sensor_msgs/Imu)

    Behavior:
      - constant yaw rate bias optional
      - gaussian noise optional (deterministic seed)
      - for now: stable near-zero motion IMU for bringup
    """

    def __init__(self) -> None:
        super().__init__("sim_imu")

        self.declare_parameter("topic", "/imu/data")
        self.declare_parameter("pub_rate_hz", 100.0)
        self.declare_parameter("yaw_rate_bias_rps", 0.0)

        topic = str(self.get_parameter("topic").value)
        rate = float(self.get_parameter("pub_rate_hz").value)

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self.pub = self.create_publisher(Imu, topic, qos)
        self.timer = self.create_timer(1.0 / rate, self._tick)

        self.get_logger().info(f"sim_imu publishing {topic} at {rate:.1f} Hz")

    def _tick(self) -> None:
        msg = Imu()
        msg.header.stamp = now_msg(self)
        msg.header.frame_id = "imu_link"

        # Orientation unknown in stub -> leave covariance large if used later
        msg.orientation_covariance[0] = -1.0  # convention: orientation not provided

        bias = float(self.get_parameter("yaw_rate_bias_rps").value)
        msg.angular_velocity.z = bias

        # Linear accel: gravity not included in many IMU conventions; keep 0 for stub
        msg.linear_acceleration.x = 0.0
        msg.linear_acceleration.y = 0.0
        msg.linear_acceleration.z = 0.0

        self.pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = SimImuNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
