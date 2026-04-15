from __future__ import annotations

import importlib.util
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _load_metrics_module():
    script_path = _repo_root() / "scripts" / "evaluate_metrics.py"
    if not script_path.exists():
        raise FileNotFoundError(f"metrics evaluator script not found: {script_path}")

    spec = importlib.util.spec_from_file_location("rover_metrics_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load metrics evaluator module from {script_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate_metrics(dataset_dir: Path, *, strict: bool = True) -> Path:
    """
    Generate metrics.json using the repository's primary evidence-based evaluator.

    The canonical implementation lives in scripts/evaluate_metrics.py so the CLI,
    documentation, and batch tooling use the same logic.
    """
    module = _load_metrics_module()
    return module.evaluate(Path(dataset_dir), strict=strict)
