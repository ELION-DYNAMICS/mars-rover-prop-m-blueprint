from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .utils import write_json


def evaluate_metrics_placeholder(dataset_dir: Path) -> Path:
    """
    Placeholder metrics evaluator.

    Writes datasets/<run_id>/metrics.json with a deterministic structure.
    Real MCAP parsing comes next (rosbag2_py or external pipeline).
    """
    metrics = {
        "schema_version": "0.1",
        "status": "placeholder",
        "notes": "MCAP parsing not yet integrated in rover_tools. Replace with rosbag2_py-based evaluator.",
        "metrics": {},
    }
    out = dataset_dir / "metrics.json"
    write_json(out, metrics)
    return out