from __future__ import annotations

import math
import time
from dataclasses import dataclass

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from geometry_msgs.msg import Twist
from std_msgs.msg import Float64


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def apply_deadband(x: float, deadband: float) -> float:
    return 0.0 if abs(x) < deadband else x


@dataclass
class Limits:
    v_max: float
    w_max: float
    a_max: float
    alpha_max: float


class RoverControlNode(Node):
    """
    Safety shaping node.

    Contract:
      /cmd_vel      (in)  geometry_msgs/Twist
      /cmd_vel_safe (out) geometry_msgs/Twist

    Enforces:
      - SI units only
      - deadband
      - velocity clamps
      - acceleration (ramp) limits
      - watchdog timeout (stop on stale command)
      - optional slip-based scaling
    """

    def __init__(self) -> None:
        super().__init__("rover_control")

        # Parameters (safe defaults; override via YAML)
        self.declare_parameter("input_topic", "/cmd_vel")
        self.declare_parameter("output_topic", "/cmd_vel_safe")
        self.declare_parameter("cmd_timeout_s", 0.5)

        self.declare_parameter("deadband_v_mps", 0.005)
        self.declare_parameter("deadband_omega_rps", 0.01)

        # Mode (modern | prop_m). Bringup can set this.
        self.declare_parameter("mode", "modern")

        # Limits per mode
        self.declare_parameter("limits.v_max_mps.modern", 0.20)
        self.declare_parameter("limits.v_max_mps.prop_m", 0.05)
        self.declare_parameter("limits.omega_max_rps.modern", 0.60)
        self.declare_parameter("limits.omega_max_rps.prop_m", 0.30)
        self.declare_parameter("limits.a_max_mps2.modern", 0.15)
        self.declare_parameter("limits.a_max_mps2.prop_m", 0.05)
        self.declare_parameter("limits.alpha_max_rps2.modern", 0.80)
        self.declare_parameter("limits.alpha_max_rps2.prop_m", 0.30)

        # Slip containment (optional)
        self.declare_parameter("slip.enabled", True)
        self.declare_parameter("slip.topic", "/wheel/slip_estimate")
        self.declare_parameter("slip.s_threshold.modern", 0.30)
        self.declare_parameter("slip.s_threshold.prop_m", 0.20)
        self.declare_parameter("slip.s_hard_limit.modern", 0.60)
        self.declare_parameter("slip.s_hard_limit.prop_m", 0.40)
        self.declare_parameter("slip.speed_scale_gamma.modern", 0.80)
        self.declare_parameter("slip.speed_scale_gamma.prop_m", 0.70)

        # Internal state
        self._last_cmd_time = None  # type: float | None
        self._cmd_in_v = 0.0
        self._cmd_in_w = 0.0

        self._v_safe = 0.0
        self._w_safe = 0.0

        self._last_update_monotonic = time.monotonic()

        self._slip_enabled = bool(self.get_parameter("slip.enabled").value)
        self._slip_value = 0.0
        self._slip_time = None  # type: float | None

        # QoS: commands should be RELIABLE
        cmd_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        # Slip can be BEST_EFFORT in practice; keep it RELIABLE for now.
        slip_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        in_topic = str(self.get_parameter("input_topic").value)
        out_topic = str(self.get_parameter("output_topic").value)

        self._sub_cmd = self.create_subscription(Twist, in_topic, self._on_cmd, cmd_qos)
        self._pub_safe = self.create_publisher(Twist, out_topic, cmd_qos)

        if self._slip_enabled:
            slip_topic = str(self.get_parameter("slip.topic").value)
            self._sub_slip = self.create_subscription(Float64, slip_topic, self._on_slip, slip_qos)

        # Control loop tick
        self._timer = self.create_timer(0.02, self._tick)  # 50 Hz safety shaping

        self.get_logger().info(f"rover_control online: {in_topic} -> {out_topic}")

    def _mode(self) -> str:
        m = str(self.get_parameter("mode").value).strip().lower()
        return "prop_m" if m in ("prop_m", "prop-m", "prop") else "modern"

    def _limits(self) -> Limits:
        m = self._mode()
        v_max = float(self.get_parameter(f"limits.v_max_mps.{m}").value)
        w_max = float(self.get_parameter(f"limits.omega_max_rps.{m}").value)
        a_max = float(self.get_parameter(f"limits.a_max_mps2.{m}").value)
        alpha_max = float(self.get_parameter(f"limits.alpha_max_rps2.{m}").value)
        return Limits(v_max=v_max, w_max=w_max, a_max=a_max, alpha_max=alpha_max)

    def _slip_params(self) -> tuple[float, float, float]:
        m = self._mode()
        s_th = float(self.get_parameter(f"slip.s_threshold.{m}").value)
        s_hard = float(self.get_parameter(f"slip.s_hard_limit.{m}").value)
        gamma = float(self.get_parameter(f"slip.speed_scale_gamma.{m}").value)
        return s_th, s_hard, gamma

    def _on_cmd(self, msg: Twist) -> None:
        # ICD semantics: use only linear.x and angular.z
        v = float(msg.linear.x)
        w = float(msg.angular.z)

        self._cmd_in_v = v
        self._cmd_in_w = w
        self._last_cmd_time = time.monotonic()

    def _on_slip(self, msg: Float64) -> None:
        self._slip_value = float(msg.data)
        self._slip_time = time.monotonic()

    def _tick(self) -> None:
        now = time.monotonic()
        dt = now - self._last_update_monotonic
        self._last_update_monotonic = now
        if dt <= 0.0 or dt > 0.2:
            # If system paused or jumped, be conservative.
            dt = 0.02

        limits = self._limits()

        # Watchdog: stale command -> ramp to zero
        timeout_s = float(self.get_parameter("cmd_timeout_s").value)
        cmd_fresh = (self._last_cmd_time is not None) and ((now - self._last_cmd_time) <= timeout_s)

        v_des = self._cmd_in_v if cmd_fresh else 0.0
        w_des = self._cmd_in_w if cmd_fresh else 0.0

        # Deadband
        dv = float(self.get_parameter("deadband_v_mps").value)
        dw = float(self.get_parameter("deadband_omega_rps").value)
        v_des = apply_deadband(v_des, dv)
        w_des = apply_deadband(w_des, dw)

        # Hard clamps
        v_des = clamp(v_des, -limits.v_max, limits.v_max)
        w_des = clamp(w_des, -limits.w_max, limits.w_max)

        # Slip containment (scales down, never scales up)
        if self._slip_enabled and self._slip_time is not None:
            s_th, s_hard, gamma = self._slip_params()
            s = self._slip_value

            if s >= s_hard:
                # Hard limit response: stop (command shaping layer)
                v_des = 0.0
                w_des = 0.0
            elif s > s_th:
                # Soft degradation
                v_des *= gamma
                w_des *= gamma

        # Acceleration limiting (ramp)
        v_err = v_des - self._v_safe
        w_err = w_des - self._w_safe

        dv_max = limits.a_max * dt
        dw_max = limits.alpha_max * dt

        self._v_safe += clamp(v_err, -dv_max, dv_max)
        self._w_safe += clamp(w_err, -dw_max, dw_max)

        # Publish safe command
        out = Twist()
        out.linear.x = float(self._v_safe)
        out.angular.z = float(self._w_safe)
        self._pub_safe.publish(out)


def main() -> None:
    rclpy.init()
    node = RoverControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
