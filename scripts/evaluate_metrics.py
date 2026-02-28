#!/usr/bin/env python3
"""
scripts/evaluate_metrics.py

Program-grade metrics evaluation for a packaged dataset.

Inputs:
  datasets/<run_id>/
    run.mcap
    run_metadata.json

Outputs:
  datasets/<run_id>/metrics.json

Design intent:
- Deterministic, auditable metrics derived from recorded evidence (MCAP).
- Hard fail on missing required artifacts.
- Degrade explicitly if rosbag2_py is unavailable (no silent success).

Metrics (Phase 0):
- run duration (s)
- message counts per required topic
- mission phase durations (DRIVE / STOP_MEASURE / TRANSMIT_LOG / REPEAT / DONE)
- commanded distance proxy (integral of cmd_vel_safe linear.x)
- achieved distance proxy (odom path length)
- slip proxy: 1 - achieved/commanded (clamped)
- stop-measure drift (max displacement during STOP_MEASURE)

This script is intentionally conservative: if it cannot compute a metric, it records
"status": "partial" and lists why.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# -----------------------------
# Utilities
# -----------------------------

def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def stamp_to_sec(stamp_msg: Any) -> float:
    # builtin_interfaces/msg/Time
    return float(stamp_msg.sec) + float(stamp_msg.nanosec) * 1e-9


# -----------------------------
# Topic names (program defaults)
# -----------------------------

TOPIC_CMD = "/cmd_vel_safe"
TOPIC_ODOM = "/odometry/filtered"
TOPIC_STATE = "/mission/state"


# -----------------------------
# Optional rosbag2 parsing
# -----------------------------

@dataclass
class BagSample:
    t: float
    msg: Any


def try_import_rosbag() -> Tuple[bool, str]:
    try:
        import rosbag2_py  # noqa: F401
        import rclpy.serialization  # noqa: F401
        import rosidl_runtime_py.utilities  # noqa: F401
        return True, ""
    except Exception as e:
        return False, str(e)


def load_mcap_samples(mcap_path: Path, topics_of_interest: List[str]) -> Tuple[Dict[str, List[BagSample]], List[str]]:
    """
    Read MCAP with rosbag2_py SequentialReader. Returns samples and warnings.
    """
    warnings: List[str] = []
    samples: Dict[str, List[BagSample]] = {t: [] for t in topics_of_interest}

    try:
        import rosbag2_py
        from rclpy.serialization import deserialize_message
        from rosidl_runtime_py.utilities import get_message
    except Exception as e:
        raise RuntimeError(f"rosbag2_py stack not available: {e}")

    if not mcap_path.exists():
        raise FileNotFoundError(f"MCAP not found: {mcap_path}")

    storage_options = rosbag2_py.StorageOptions(uri=str(mcap_path), storage_id="mcap")
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr",
    )

    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    # Map topic -> ROS message type string
    topic_types: Dict[str, str] = {}
    for t in reader.get_all_topics_and_types():
        topic_types[t.name] = t.type

    missing = [t for t in topics_of_interest if t not in topic_types]
    if missing:
        warnings.append(f"topics missing from bag: {missing}")

    # Pre-build message classes for topics we can parse
    msg_classes: Dict[str, Any] = {}
    for t in topics_of_interest:
        if t in topic_types:
            try:
                msg_classes[t] = get_message(topic_types[t])
            except Exception as e:
                warnings.append(f"cannot resolve msg type for {t} ({topic_types[t]}): {e}")

    while reader.has_next():
        topic, data, t_ns = reader.read_next()
        if topic not in samples:
            continue
        if topic not in msg_classes:
            continue

        try:
            msg = deserialize_message(data, msg_classes[topic])
        except Exception as e:
            warnings.append(f"deserialize failed for {topic}: {e}")
            continue

        t = float(t_ns) * 1e-9
        samples[topic].append(BagSample(t=t, msg=msg))

    # Sort (should already be ordered, but enforce)
    for t in topics_of_interest:
        samples[t].sort(key=lambda s: s.t)

    return samples, warnings


# -----------------------------
# Metric computations
# -----------------------------

def compute_phase_durations(state_samples: List[BagSample]) -> Dict[str, float]:
    """
    From std_msgs/String mission state.
    Computes total time spent in each phase.
    """
    durations: Dict[str, float] = {}
    if len(state_samples) < 2:
        return durations

    # state at time i applies until next sample
    for i in range(len(state_samples) - 1):
        s0 = str(getattr(state_samples[i].msg, "data", "")).strip()
        t0 = state_samples[i].t
        t1 = state_samples[i + 1].t
        dt = max(0.0, t1 - t0)
        if not s0:
            s0 = "UNKNOWN"
        durations[s0] = durations.get(s0, 0.0) + dt

    return durations


def integrate_cmd_distance(cmd_samples: List[BagSample]) -> float:
    """
    Integrate commanded forward distance proxy: ∫ max(vx,0) dt
    Uses geometry_msgs/Twist linear.x
    """
    if len(cmd_samples) < 2:
        return 0.0

    dist = 0.0
    for i in range(len(cmd_samples) - 1):
        v = float(cmd_samples[i].msg.linear.x)
        v = max(0.0, v)  # forward-only proxy; reverse is a different story
        dt = max(0.0, cmd_samples[i + 1].t - cmd_samples[i].t)
        dist += v * dt
    return dist


def odom_path_length(odom_samples: List[BagSample]) -> float:
    """
    Compute achieved distance proxy from odometry pose positions.
    """
    if len(odom_samples) < 2:
        return 0.0

    def xy(sample: BagSample) -> Tuple[float, float]:
        p = sample.msg.pose.pose.position
        return float(p.x), float(p.y)

    length = 0.0
    x0, y0 = xy(odom_samples[0])
    for s in odom_samples[1:]:
        x1, y1 = xy(s)
        dx, dy = x1 - x0, y1 - y0
        length += math.hypot(dx, dy)
        x0, y0 = x1, y1
    return length


def stop_measure_drift(odom_samples: List[BagSample], state_samples: List[BagSample]) -> Optional[float]:
    """
    Max displacement during STOP_MEASURE windows, based on odom positions.
    Returns None if insufficient data.
    """
    if len(odom_samples) < 2 or len(state_samples) < 2:
        return None

    # Build time->state intervals from mission/state
    intervals: List[Tuple[float, float]] = []
    for i in range(len(state_samples) - 1):
        s0 = str(getattr(state_samples[i].msg, "data", "")).strip()
        if s0 == "STOP_MEASURE":
            intervals.append((state_samples[i].t, state_samples[i + 1].t))

    if not intervals:
        return None

    def pos_at(sample: BagSample) -> Tuple[float, float]:
        p = sample.msg.pose.pose.position
        return float(p.x), float(p.y)

    max_drift = 0.0
    # For each STOP_MEASURE interval, compute displacement between first and last odom sample within interval
    for (t0, t1) in intervals:
        window = [s for s in odom_samples if t0 <= s.t <= t1]
        if len(window) < 2:
            continue
        x_start, y_start = pos_at(window[0])
        x_end, y_end = pos_at(window[-1])
        drift = math.hypot(x_end - x_start, y_end - y_start)
        max_drift = max(max_drift, drift)

    return max_drift


# -----------------------------
# Main
# -----------------------------

def evaluate(dataset_dir: Path, *, out_path: Optional[Path] = None, strict: bool = True) -> Path:
    run_meta_path = dataset_dir / "run_metadata.json"
    mcap_path = dataset_dir / "run.mcap"

    if strict:
        if not dataset_dir.exists():
            raise FileNotFoundError(f"dataset dir not found: {dataset_dir}")
        if not run_meta_path.exists():
            raise FileNotFoundError(f"missing run_metadata.json: {run_meta_path}")
        if not mcap_path.exists():
            raise FileNotFoundError(f"missing run.mcap: {mcap_path}")

    meta = read_json(run_meta_path) if run_meta_path.exists() else {}
    run_id = str(meta.get("run_id", dataset_dir.name))

    metrics: Dict[str, Any] = {
        "schema_version": "0.1",
        "run_id": run_id,
        "status": "ok",
        "notes": [],
        "topics": {},
        "time": {},
        "mission": {},
        "mobility": {},
        "quality": {},
    }

    # Attempt to parse bag
    ok_rosbag, why = try_import_rosbag()
    if not ok_rosbag:
        metrics["status"] = "partial"
        metrics["notes"].append(
            "rosbag2_py not available; cannot compute evidence-based metrics from MCAP. "
            f"Install rosbag2_py stack. Import error: {why}"
        )
        # Still write a metrics file (honest partial)
        out = out_path or (dataset_dir / "metrics.json")
        write_json(out, metrics)
        return out

    samples, warnings = load_mcap_samples(mcap_path, [TOPIC_CMD, TOPIC_ODOM, TOPIC_STATE])
    for w in warnings:
        metrics["notes"].append(w)

    # Message counts
    for t, lst in samples.items():
        metrics["topics"][t] = {"count": len(lst)}

    # Time coverage (use all samples)
    all_times: List[float] = []
    for lst in samples.values():
        all_times += [s.t for s in lst]
    all_times.sort()

    if len(all_times) >= 2:
        metrics["time"]["start_s"] = all_times[0]
        metrics["time"]["end_s"] = all_times[-1]
        metrics["time"]["duration_s"] = max(0.0, all_times[-1] - all_times[0])
    else:
        metrics["status"] = "partial"
        metrics["notes"].append("insufficient timestamps to compute run duration")

    # Mission phase durations
    phase_durs = compute_phase_durations(samples[TOPIC_STATE])
    metrics["mission"]["phase_durations_s"] = phase_durs

    # Mobility proxies
    cmd_dist = integrate_cmd_distance(samples[TOPIC_CMD])
    odom_dist = odom_path_length(samples[TOPIC_ODOM])
    metrics["mobility"]["commanded_distance_m_proxy"] = cmd_dist
    metrics["mobility"]["achieved_distance_m_proxy"] = odom_dist

    slip_proxy = None
    if cmd_dist > 1e-6:
        slip_proxy = clamp(1.0 - (odom_dist / cmd_dist), 0.0, 1.0)
        metrics["mobility"]["slip_proxy"] = slip_proxy
    else:
        metrics["status"] = "partial"
        metrics["notes"].append("commanded distance proxy is ~0; slip proxy undefined")

    drift = stop_measure_drift(samples[TOPIC_ODOM], samples[TOPIC_STATE])
    if drift is not None:
        metrics["mission"]["stop_measure_max_drift_m"] = drift
    else:
        metrics["status"] = "partial"
        metrics["notes"].append("cannot compute stop_measure drift (missing states or odom windows)")

    # Basic data quality flags
    metrics["quality"]["has_cmd_vel_safe"] = len(samples[TOPIC_CMD]) > 0
    metrics["quality"]["has_odom_filtered"] = len(samples[TOPIC_ODOM]) > 0
    metrics["quality"]["has_mission_state"] = len(samples[TOPIC_STATE]) > 0

    if strict:
        if not metrics["quality"]["has_cmd_vel_safe"]:
            metrics["status"] = "partial"
            metrics["notes"].append(f"missing required topic samples: {TOPIC_CMD}")
        if not metrics["quality"]["has_odom_filtered"]:
            metrics["status"] = "partial"
            metrics["notes"].append(f"missing required topic samples: {TOPIC_ODOM}")
        if not metrics["quality"]["has_mission_state"]:
            metrics["status"] = "partial"
            metrics["notes"].append(f"missing required topic samples: {TOPIC_STATE}")

    out = out_path or (dataset_dir / "metrics.json")
    write_json(out, metrics)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Evaluate Phase-0 metrics from a packaged dataset.")
    ap.add_argument("dataset_dir", type=str, help="Path to datasets/<run_id>/")
    ap.add_argument("--out", type=str, default="", help="Optional output path for metrics.json")
    ap.add_argument("--non-strict", action="store_true", help="Do not hard-fail on missing artifacts")

    args = ap.parse_args()
    dataset_dir = Path(args.dataset_dir).resolve()
    out_path = Path(args.out).resolve() if args.out else None
    strict = not args.non_strict

    try:
        out = evaluate(dataset_dir, out_path=out_path, strict=strict)
    except Exception as e:
        print(f"[evaluate_metrics] ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)

    print(str(out))


if __name__ == "__main__":
    main()
