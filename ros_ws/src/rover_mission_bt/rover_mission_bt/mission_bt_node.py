from __future__ import annotations

import os
import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from std_msgs.msg import String


class RoverMissionBTNode(Node):
    """
    Minimal mission BT runner.

    Today:
      - Loads a BT XML file path (for traceability)
      - Runs a deterministic phase machine: DRIVE -> STOP_MEASURE -> TRANSMIT_LOG -> REPEAT
      - Publishes /mission/state as std_msgs/String

    Tomorrow:
      - Bind DriveToGoal to Nav2 NavigateToPose action
      - Bind StopMotion to /cmd_vel_safe = 0
      - Bind AcquireMeasurements to sensor sampling windows
      - Bind TransmitAndLog to dataset logger / comms stub
    """

    def __init__(self) -> None:
        super().__init__("rover_mission_bt")

        self.declare_parameter("mode", "modern")  # modern | prop_m
        self.declare_parameter("tick_rate_hz", 2.0)

        # BT tree path (traceability even if we don't parse it yet)
        self.declare_parameter("tree_file", "")

        # Phase timings (seconds)
        self.declare_parameter("drive_duration_s.modern", 20.0)
        self.declare_parameter("measure_duration_s.modern", 3.0)
        self.declare_parameter("transmit_duration_s.modern", 4.0)

        self.declare_parameter("drive_duration_s.prop_m", 8.0)
        self.declare_parameter("measure_duration_s.prop_m", 8.0)
        self.declare_parameter("transmit_duration_s.prop_m", 6.0)

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self.pub_state = self.create_publisher(String, "/mission/state", qos)

        self._phase = "DRIVE"
        self._phase_started = time.monotonic()

        rate = float(self.get_parameter("tick_rate_hz").value)
        self.timer = self.create_timer(1.0 / rate, self._tick)

        self._log_startup()

    def _mode(self) -> str:
        m = str(self.get_parameter("mode").value).strip().lower()
        return "prop_m" if m in ("prop_m", "prop-m", "prop") else "modern"

    def _durations(self) -> tuple[float, float, float]:
        m = self._mode()
        d_drive = float(self.get_parameter(f"drive_duration_s.{m}").value)
        d_meas = float(self.get_parameter(f"measure_duration_s.{m}").value)
        d_tx = float(self.get_parameter(f"transmit_duration_s.{m}").value)
        return d_drive, d_meas, d_tx

    def _log_startup(self) -> None:
        mode = self._mode()
        tree_file = str(self.get_parameter("tree_file").value).strip()
        if tree_file:
            self.get_logger().info(f"mission_bt mode={mode} tree_file={tree_file}")
        else:
            self.get_logger().info(f"mission_bt mode={mode} tree_file=(not set)")

    def _publish_state(self) -> None:
        msg = String()
        msg.data = self._phase
        self.pub_state.publish(msg)

    def _advance(self, next_phase: str) -> None:
        self._phase = next_phase
        self._phase_started = time.monotonic()
        self._publish_state()

    def _tick(self) -> None:
        self._publish_state()

        d_drive, d_meas, d_tx = self._durations()
        elapsed = time.monotonic() - self._phase_started

        if self._phase == "DRIVE":
            if elapsed >= d_drive:
                self._advance("STOP_MEASURE")
        elif self._phase == "STOP_MEASURE":
            if elapsed >= d_meas:
                self._advance("TRANSMIT_LOG")
        elif self._phase == "TRANSMIT_LOG":
            if elapsed >= d_tx:
                self._advance("REPEAT")
        elif self._phase == "REPEAT":
            # In real BT: SelectNextGoal, possibly GoalReached check.
            # For now: immediately drive again.
            self._advance("DRIVE")
        else:
            # Unknown state -> fail safe
            self._advance("STOP_MEASURE")


def main() -> None:
    rclpy.init()
    node = RoverMissionBTNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
