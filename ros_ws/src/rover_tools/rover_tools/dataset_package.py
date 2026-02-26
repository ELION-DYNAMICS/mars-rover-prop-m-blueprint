from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from .utils import sha256_file, write_json
from .schema_validate import main_validate


def package_dataset(
    repo_root: Path,
    run_id: str,
    bag_file: Path,
    run_metadata: Dict[str, Any],
    *,
    plots_dir: Optional[Path] = None,
) -> Path:
    datasets_dir = repo_root / "datasets"
    target_dir = datasets_dir / run_id
    target_dir.mkdir(parents=True, exist_ok=False)

    # Copy bag
    target_bag = target_dir / "run.mcap"
    shutil.copy2(bag_file, target_bag)

    # Write metadata
    meta_path = target_dir / "run_metadata.json"
    write_json(meta_path, run_metadata)

    ok, reasons = main_validate(meta_path)
    if not ok:
        # Hard fail: invalid dataset is not allowed
        raise ValueError("run_metadata.json failed validation:\n- " + "\n- ".join(reasons))

    # Optional plots
    if plots_dir and plots_dir.exists():
        shutil.copytree(plots_dir, target_dir / "plots", dirs_exist_ok=True)

    # Integrity hashes
    # Update metadata file with hashes (append-only update)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta.setdefault("integrity", {})
    meta["integrity"]["mcap_sha256"] = sha256_file(target_bag)
    meta["integrity"]["metadata_sha256"] = sha256_file(meta_path)
    write_json(meta_path, meta)

    return target_dir