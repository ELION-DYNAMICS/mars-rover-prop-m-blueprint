#!/usr/bin/env python3
"""
scripts/export_bag.py

Export a packaged run bag (MCAP) into analysis-friendly artifacts.

Inputs:
  datasets/<run_id>/run.mcap
  datasets/<run_id>/run_metadata.json   (optional but recommended)

Outputs (default):
  datasets/<run_id>/exports/
    manifest.json
    topics.txt
    <topic_name_sanitized>.csv          (best-effort)
    diagnostics.json                    (errors/warnings)

Philosophy:
- Export is a convenience layer, not the source of truth.
- The source of truth remains the MCAP + metadata.
- Fail loudly on missing bag; degrade explicitly when a feature is unavailable.

Export backends:
1) Preferred: rosbag2_py (direct read) -> CSV rows for selected message types
2) Fallback: ros2 bag convert (if available) -> writes CSV (varies by distro)

By default this script exports only "core" topics:
  /cmd_vel_safe, /odometry/filtered, /mission/state, /imu/data

You can override with --topics.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


CORE_TOPICS = [
    "/cmd_vel_safe",
    "/odometry/filtered",
    "/mission/state",
    "/imu/data",
]


# -----------------------------
# Utils
# -----------------------------

def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sanitize_topic(topic: str) -> str:
    # /odometry/filtered -> odometry__filtered
    s = topic.strip().lstrip("/")
    s = s.replace("/", "__")
    s = re.sub(r"[^a-zA-Z0-9_]+", "_", s)
    return s or "topic"


def stamp_to_sec(stamp_msg: Any) -> float:
    return float(stamp_msg.sec) + float(stamp_msg.nanosec) * 1e-9


def try_import_rosbag() -> Tuple[bool, str]:
    try:
        import rosbag2_py  # noqa: F401
        import rclpy.serialization  # noqa: F401
        import rosidl_runtime_py.utilities  # noqa: F401
        return True, ""
    except Exception as e:
        return False, str(e)


# -----------------------------
# Rosbag2 direct reader
# -----------------------------

@dataclass
class BagRow:
    t: float
    fields: Dict[str, Any]


def rosbag_read_rows(mcap_path: Path, topic: str) -> Tuple[List[BagRow], str]:
    """
    Best-effort conversion for a single topic into a list of rows (dicts).
    Supports a small set of message types we care about in Phase 0.
    Returns (rows, msg_type_string).
    """
    import rosbag2_py
    from rclpy.serialization import deserialize_message
    from rosidl_runtime_py.utilities import get_message

    storage_options = rosbag2_py.StorageOptions(uri=str(mcap_path), storage_id="mcap")
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr",
    )

    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    topic_types = {t.name: t.type for t in reader.get_all_topics_and_types()}
    if topic not in topic_types:
        return [], ""

    msg_type = topic_types[topic]
    msg_cls = get_message(msg_type)

    rows: List[BagRow] = []
    while reader.has_next():
        t_name, data, t_ns = reader.read_next()
        if t_name != topic:
            continue
        msg = deserialize_message(data, msg_cls)
        t = float(t_ns) * 1e-9

        # Phase 0 supported message types
        # geometry_msgs/Twist
        if msg_type == "geometry_msgs/msg/Twist":
            rows.append(BagRow(t=t, fields={
                "linear_x": float(msg.linear.x),
                "linear_y": float(msg.linear.y),
                "linear_z": float(msg.linear.z),
                "angular_x": float(msg.angular.x),
                "angular_y": float(msg.angular.y),
                "angular_z": float(msg.angular.z),
            }))
            continue

        # nav_msgs/Odometry
        if msg_type == "nav_msgs/msg/Odometry":
            p = msg.pose.pose.position
            q = msg.pose.pose.orientation
            v = msg.twist.twist.linear
            w = msg.twist.twist.angular
            rows.append(BagRow(t=t, fields={
                "pos_x": float(p.x),
                "pos_y": float(p.y),
                "pos_z": float(p.z),
                "ori_x": float(q.x),
                "ori_y": float(q.y),
                "ori_z": float(q.z),
                "ori_w": float(q.w),
                "lin_vx": float(v.x),
                "lin_vy": float(v.y),
                "lin_vz": float(v.z),
                "ang_wx": float(w.x),
                "ang_wy": float(w.y),
                "ang_wz": float(w.z),
            }))
            continue

        # std_msgs/String
        if msg_type == "std_msgs/msg/String":
            rows.append(BagRow(t=t, fields={"data": str(msg.data)}))
            continue

        # sensor_msgs/Imu
        if msg_type == "sensor_msgs/msg/Imu":
            q = msg.orientation
            av = msg.angular_velocity
            la = msg.linear_acceleration
            rows.append(BagRow(t=t, fields={
                "ori_x": float(q.x),
                "ori_y": float(q.y),
                "ori_z": float(q.z),
                "ori_w": float(q.w),
                "ang_vx": float(av.x),
                "ang_vy": float(av.y),
                "ang_vz": float(av.z),
                "lin_ax": float(la.x),
                "lin_ay": float(la.y),
                "lin_az": float(la.z),
            }))
            continue

        # Unsupported type: do not silently pretend
        # Record only timestamp count as export failure
        rows.append(BagRow(t=t, fields={"_unsupported_type": msg_type}))

    return rows, msg_type


def write_csv(path: Path, rows: List[BagRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        # still create an empty CSV with header
        path.write_text("t\n", encoding="utf-8")
        return

    # Union of keys for header
    keys: List[str] = ["t"]
    field_keys = sorted({k for r in rows for k in r.fields.keys()})
    keys += field_keys

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            row = {"t": f"{r.t:.9f}"}
            for k, v in r.fields.items():
                row[k] = v
            w.writerow(row)


# -----------------------------
# Fallback exporter (ros2 bag convert)
# -----------------------------

def try_ros2_bag_convert(mcap_path: Path, out_dir: Path) -> Tuple[bool, str]:
    """
    Uses ros2 bag convert --output-format csv (availability varies).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = ["ros2", "bag", "convert", "-i", str(mcap_path), "-o", str(out_dir), "--output-format", "csv"]
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if p.returncode != 0:
            return False, p.stderr.strip() or p.stdout.strip()
        return True, p.stdout.strip()
    except FileNotFoundError:
        return False, "ros2 CLI not found in PATH"
    except Exception as e:
        return False, str(e)


# -----------------------------
# Main
# -----------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Export MCAP bag to CSV artifacts (best-effort).")
    ap.add_argument("dataset_dir", type=str, help="Path to datasets/<run_id>/ directory")
    ap.add_argument("--topics", type=str, default="", help="Comma-separated list of topics to export (default: core topics)")
    ap.add_argument("--out", type=str, default="", help="Output directory (default: datasets/<run_id>/exports)")
    ap.add_argument("--prefer-cli", action="store_true", help="Prefer ros2 bag convert fallback even if rosbag2_py exists")

    args = ap.parse_args()
    dataset_dir = Path(args.dataset_dir).resolve()
    mcap_path = dataset_dir / "run.mcap"
    meta_path = dataset_dir / "run_metadata.json"

    if not dataset_dir.exists():
        print(f"[export_bag] ERROR: dataset dir not found: {dataset_dir}", file=sys.stderr)
        raise SystemExit(2)
    if not mcap_path.exists():
        print(f"[export_bag] ERROR: missing run.mcap: {mcap_path}", file=sys.stderr)
        raise SystemExit(2)

    out_dir = Path(args.out).resolve() if args.out else (dataset_dir / "exports")
    out_dir.mkdir(parents=True, exist_ok=True)

    topics = CORE_TOPICS
    if args.topics.strip():
        topics = [t.strip() for t in args.topics.split(",") if t.strip()]

    diagnostics: Dict[str, Any] = {
        "status": "ok",
        "notes": [],
        "dataset_dir": str(dataset_dir),
        "bag": str(mcap_path),
        "export_dir": str(out_dir),
        "topics_requested": topics,
        "topics_exported": {},
    }

    run_meta: Dict[str, Any] = {}
    if meta_path.exists():
        try:
            run_meta = read_json(meta_path)
        except Exception as e:
            diagnostics["status"] = "partial"
            diagnostics["notes"].append(f"failed to parse run_metadata.json: {e}")

    # Write topics list
    (out_dir / "topics.txt").write_text("\n".join(topics) + "\n", encoding="utf-8")

    ok_rosbag, why_rosbag = try_import_rosbag()

    # Optionally prefer CLI convert
    if args.prefer_cli:
        ok, msg = try_ros2_bag_convert(mcap_path, out_dir / "ros2_convert")
        if not ok:
            diagnostics["status"] = "partial"
            diagnostics["notes"].append(f"ros2 bag convert failed: {msg}")
        else:
            diagnostics["notes"].append("exported via ros2 bag convert (csv) into exports/ros2_convert/")
        # Always still produce manifest/diagnostics
        write_json(out_dir / "diagnostics.json", diagnostics)
        write_json(out_dir / "manifest.json", {
            "schema_version": "0.1",
            "run_id": str(run_meta.get("run_id", dataset_dir.name)),
            "export_backend": "ros2_bag_convert",
            "topics": topics,
        })
        print(str(out_dir))
        return

    # Preferred: rosbag2_py
    if ok_rosbag:
        for t in topics:
            try:
                rows, msg_type = rosbag_read_rows(mcap_path, t)
                if not msg_type:
                    diagnostics["status"] = "partial"
                    diagnostics["topics_exported"][t] = {"status": "missing", "count": 0}
                    continue

                out_csv = out_dir / f"{sanitize_topic(t)}.csv"
                write_csv(out_csv, rows)

                diagnostics["topics_exported"][t] = {
                    "status": "ok",
                    "msg_type": msg_type,
                    "count": len(rows),
                    "file": out_csv.name,
                }

                # Flag unsupported message types explicitly
                if rows and "_unsupported_type" in rows[0].fields:
                    diagnostics["status"] = "partial"
                    diagnostics["topics_exported"][t]["status"] = "unsupported_type"
            except Exception as e:
                diagnostics["status"] = "partial"
                diagnostics["topics_exported"][t] = {"status": "error", "error": str(e)}

        write_json(out_dir / "manifest.json", {
            "schema_version": "0.1",
            "run_id": str(run_meta.get("run_id", dataset_dir.name)),
            "export_backend": "rosbag2_py",
            "topics": topics,
            "notes": diagnostics["notes"],
        })
        write_json(out_dir / "diagnostics.json", diagnostics)
        print(str(out_dir))
        return

    # Fallback: ros2 bag convert
    diagnostics["status"] = "partial"
    diagnostics["notes"].append(f"rosbag2_py unavailable: {why_rosbag}")
    ok, msg = try_ros2_bag_convert(mcap_path, out_dir / "ros2_convert")
    if not ok:
        diagnostics["notes"].append(f"ros2 bag convert failed: {msg}")
    else:
        diagnostics["notes"].append("exported via ros2 bag convert (csv) into exports/ros2_convert/")

    write_json(out_dir / "manifest.json", {
        "schema_version": "0.1",
        "run_id": str(run_meta.get("run_id", dataset_dir.name)),
        "export_backend": "ros2_bag_convert",
        "topics": topics,
        "notes": diagnostics["notes"],
    })
    write_json(out_dir / "diagnostics.json", diagnostics)
    print(str(out_dir))


if __name__ == "__main__":
    main()
