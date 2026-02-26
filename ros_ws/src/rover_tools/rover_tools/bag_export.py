from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional


def export_bag_to_csv(bag_path: Path, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = ["ros2", "bag", "convert", "-i", str(bag_path), "-o", str(out_dir), "--output-format", "csv"]
    return subprocess.call(cmd)