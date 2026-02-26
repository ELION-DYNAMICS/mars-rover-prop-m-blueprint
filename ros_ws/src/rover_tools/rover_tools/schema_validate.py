from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


REQUIRED_TOP_LEVEL = [
    "schema_version",
    "run_id",
    "created_utc",
    "mode",
    "backend",
    "scenario",
    "seed",
    "git",
    "clock",
    "physics",
    "robot",
    "params",
    "topics",
    "artifacts",
]


def validate_minimal(meta: Dict[str, Any]) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    for k in REQUIRED_TOP_LEVEL:
        if k not in meta:
            reasons.append(f"missing required key: {k}")
    if "mode" in meta and meta["mode"] not in ("simulation", "hardware"):
        reasons.append("mode must be 'simulation' or 'hardware'")
    if "backend" in meta and meta["backend"] not in ("gazebo", "webots", "pybullet", "hardware"):
        reasons.append("backend must be gazebo|webots|pybullet|hardware")
    if "seed" in meta and not isinstance(meta["seed"], int):
        reasons.append("seed must be integer")
    if "topics" in meta and "recorded" in meta.get("topics", {}) and not meta["topics"]["recorded"]:
        reasons.append("topics.recorded must be non-empty")
    return (len(reasons) == 0), reasons


def main_validate(metadata_path: Path) -> Tuple[bool, List[str]]:
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    return validate_minimal(meta)