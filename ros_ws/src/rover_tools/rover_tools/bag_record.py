from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List, Optional

from .utils import read_yaml_simple


def record_bag(
    output_dir: Path,
    topics_yaml: Path,
    *,
    storage_id: str = "mcap",
    max_cache_size: int = 0,
) -> int:
    cfg = read_yaml_simple(topics_yaml)
    topics: List[str] = list(cfg.get("topics", []))
    if not topics:
        raise ValueError(f"No topics found in {topics_yaml}")

    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = ["ros2", "bag", "record", "--storage", storage_id, "-o", str(output_dir)]
    if max_cache_size > 0:
        cmd += ["--max-cache-size", str(max_cache_size)]
    cmd += topics

    return subprocess.call(cmd)