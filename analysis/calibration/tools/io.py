"""
io.py

Strict IO utilities for the calibration framework.

Responsibilities:
- Load and validate analysis/calibration/data/manifests/dataset_index.json
- Filter datasets by experiment tags (E01–E04), backend, scenario, usable flag
- Validate that referenced dataset paths exist (authoritative root is /datasets)
- Read/write small JSON/YAML artifacts deterministically
- Provide optional MCAP/rosbag2 reading hooks (graceful if unavailable)

Engineering intent:
If datasets are missing or malformed -> fail loudly with actionable errors.
No "best effort" silent behavior. Calibration must be reproducible.

SI units only. Time is UTC ISO-8601 strings in metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import json
import hashlib
import datetime as _dt


JSON = Dict[str, Any]


# -----------------------------
# Data structures
# -----------------------------

@dataclass(frozen=True)
class DatasetEntry:
    run_id: str
    category: str
    experiment_tags: List[str]
    backend: str
    scenario: str
    seed: Optional[int]
    dataset_dir: Path
    mcap_path: Optional[Path]
    metadata_path: Optional[Path]
    metrics_path: Optional[Path]
    usable: bool
    notes: str
    git_commit: Optional[str]
    created_utc: Optional[str]


# -----------------------------
# Basic JSON utilities
# -----------------------------

def read_json(path: Union[str, Path]) -> JSON:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JSON file not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Union[str, Path], obj: Any, *, indent: int = 2) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    # Deterministic JSON: sorted keys, fixed indentation, newline at EOF.
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=indent, sort_keys=True)
        f.write("\n")


def utc_now_iso() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# -----------------------------
# Integrity utilities
# -----------------------------

def sha256_file(path: Union[str, Path], *, chunk_size: int = 1024 * 1024) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Cannot hash missing file: {p}")
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


# -----------------------------
# Dataset index loading + validation
# -----------------------------

def _require(obj: JSON, key: str, where: str) -> Any:
    if key not in obj:
        raise KeyError(f"Missing required key '{key}' in {where}")
    return obj[key]


def load_dataset_index(
    index_path: Union[str, Path] = Path("analysis/calibration/data/manifests/dataset_index.json"),
) -> JSON:
    idx = read_json(index_path)

    _require(idx, "schema_version", "dataset_index.json")
    _require(idx, "datasets", "dataset_index.json")
    if not isinstance(idx["datasets"], list):
        raise TypeError("dataset_index.json: 'datasets' must be a list")

    # Ensure generated_utc exists (populate if missing)
    if "generated_utc" not in idx:
        idx["generated_utc"] = utc_now_iso()

    # Enforce root policy presence (optional but recommended)
    if "root_policy" in idx and "authoritative_dataset_root" in idx["root_policy"]:
        # keep as-is
        pass
    else:
        # Provide safe default
        idx.setdefault("root_policy", {})
        idx["root_policy"].setdefault("authoritative_dataset_root", "/datasets")

    return idx


def parse_entries(
    idx: JSON,
    *,
    require_paths_exist: bool = True
) -> List[DatasetEntry]:
    root = Path(idx.get("root_policy", {}).get("authoritative_dataset_root", "/datasets"))
    entries: List[DatasetEntry] = []

    for i, raw in enumerate(idx.get("datasets", [])):
        where = f"dataset_index.json.datasets[{i}]"
        run_id = str(_require(raw, "run_id", where))
        category = str(raw.get("category", "unknown"))
        backend = str(raw.get("backend", "unknown"))
        scenario = str(raw.get("scenario", "unknown"))
        seed = raw.get("seed", None)
        if seed is not None:
            try:
                seed = int(seed)
            except Exception as e:
                raise TypeError(f"{where}.seed must be int or null, got {seed!r}") from e

        tags = raw.get("experiment_tags", [])
        if not isinstance(tags, list):
            raise TypeError(f"{where}.experiment_tags must be a list")
        tags = [str(t) for t in tags]

        paths = raw.get("paths", {})
        if not isinstance(paths, dict):
            raise TypeError(f"{where}.paths must be an object")

        dataset_dir = Path(paths.get("dataset_dir", root / run_id))
        # Normalize relative paths to repository root
        dataset_dir = dataset_dir if dataset_dir.is_absolute() else Path.cwd() / dataset_dir

        def _p(k: str) -> Optional[Path]:
            v = paths.get(k, None)
            if v is None:
                return None
            p = Path(v)
            return p if p.is_absolute() else Path.cwd() / p

        mcap = _p("mcap")
        metadata = _p("metadata")
        metrics = _p("metrics")

        quality = raw.get("quality", {})
        usable = bool(quality.get("usable", True))
        notes = str(quality.get("notes", ""))

        prov = raw.get("provenance", {})
        git_commit = prov.get("git_commit", None)
        created_utc = prov.get("created_utc", None)

        entry = DatasetEntry(
            run_id=run_id,
            category=category,
            experiment_tags=tags,
            backend=backend,
            scenario=scenario,
            seed=seed,
            dataset_dir=dataset_dir,
            mcap_path=mcap,
            metadata_path=metadata,
            metrics_path=metrics,
            usable=usable,
            notes=notes,
            git_commit=str(git_commit) if git_commit is not None else None,
            created_utc=str(created_utc) if created_utc is not None else None,
        )

        if require_paths_exist:
            validate_entry_paths(entry)

        entries.append(entry)

    return entries


def validate_entry_paths(entry: DatasetEntry) -> None:
    """
    Enforce that referenced paths exist.
    This is strict by design: calibration must not run on phantom datasets.
    """
    if not entry.dataset_dir.exists():
        raise FileNotFoundError(f"[{entry.run_id}] dataset_dir missing: {entry.dataset_dir}")

    # These may be optional early in bring-up, but if present, must exist.
    for label, p in (
        ("mcap", entry.mcap_path),
        ("metadata", entry.metadata_path),
        ("metrics", entry.metrics_path),
    ):
        if p is not None and not p.exists():
            raise FileNotFoundError(f"[{entry.run_id}] {label} path missing: {p}")


# -----------------------------
# Filtering and selection
# -----------------------------

def filter_datasets(
    entries: Sequence[DatasetEntry],
    *,
    experiment_tag: Optional[str] = None,
    backend: Optional[str] = None,
    scenario: Optional[str] = None,
    usable_only: bool = True,
) -> List[DatasetEntry]:
    out: List[DatasetEntry] = []
    for e in entries:
        if usable_only and not e.usable:
            continue
        if experiment_tag is not None and experiment_tag not in e.experiment_tags:
            continue
        if backend is not None and e.backend != backend:
            continue
        if scenario is not None and e.scenario != scenario:
            continue
        out.append(e)
    return out


def select_single_dataset(
    entries: Sequence[DatasetEntry],
    *,
    experiment_tag: str,
    backend: Optional[str] = None,
    scenario: Optional[str] = None,
    seed: Optional[int] = None,
) -> DatasetEntry:
    """
    Select exactly one dataset matching constraints.
    Raises if 0 or >1 match (forces explicitness).
    """
    candidates = filter_datasets(
        entries,
        experiment_tag=experiment_tag,
        backend=backend,
        scenario=scenario,
        usable_only=True,
    )
    if seed is not None:
        candidates = [c for c in candidates if c.seed == seed]

    if len(candidates) == 0:
        raise RuntimeError(
            "No matching dataset found for "
            f"tag={experiment_tag!r}, backend={backend!r}, scenario={scenario!r}, seed={seed!r}"
        )
    if len(candidates) > 1:
        ids = [c.run_id for c in candidates[:10]]
        raise RuntimeError(
            "Multiple datasets match selection. Be explicit (run_id/seed/backend/scenario).\n"
            f"Matches (showing up to 10): {ids}"
        )
    return candidates[0]


# -----------------------------
# Optional ROS bag / MCAP hooks
# -----------------------------

def rosbag2_available() -> bool:
    try:
        import rosbag2_py  # type: ignore
        return True
    except Exception:
        return False


def read_mcap_topics(entry: DatasetEntry) -> List[str]:
    """
    Return topic names present in an MCAP bag.

    Requires rosbag2_py in the environment. If unavailable, raises RuntimeError.
    """
    if entry.mcap_path is None:
        raise ValueError(f"[{entry.run_id}] No MCAP path provided in index.")
    if not entry.mcap_path.exists():
        raise FileNotFoundError(f"[{entry.run_id}] MCAP not found: {entry.mcap_path}")
    if not rosbag2_available():
        raise RuntimeError(
            "rosbag2_py not available. Install ROS 2 + rosbag2 (with MCAP storage plugin) "
            "or run in the project dev container."
        )

    # Minimal metadata read through rosbag2_py
    import rosbag2_py  # type: ignore

    storage_options = rosbag2_py.StorageOptions(uri=str(entry.mcap_path), storage_id="mcap")
    converter_options = rosbag2_py.ConverterOptions(input_serialization_format="cdr", output_serialization_format="cdr")

    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)
    topics = reader.get_all_topics_and_types()
    return sorted([t.name for t in topics])


# -----------------------------
# Convenience: update index timestamps / integrity
# -----------------------------

def update_index_generated_time(idx: JSON) -> JSON:
    idx = dict(idx)
    idx["generated_utc"] = utc_now_iso()
    return idx


def compute_and_store_hashes(
    idx: JSON,
    *,
    index_path: Union[str, Path] = Path("analysis/calibration/data/manifests/dataset_index.json"),
    update_generated_time: bool = True,
    hash_mcap: bool = False,
    hash_metadata: bool = True,
) -> None:
    """
    Compute SHA256 hashes for metadata (and optionally MCAP) and update the index file in-place.

    Note:
    - Hashing MCAP can be expensive. Leave hash_mcap=False for day-to-day dev.
    """
    if update_generated_time:
        idx = update_index_generated_time(idx)

    for raw in idx.get("datasets", []):
        paths = raw.get("paths", {})
        integ = raw.setdefault("integrity", {})

        metadata_path = paths.get("metadata", None)
        mcap_path = paths.get("mcap", None)

        if hash_metadata and metadata_path:
            p = Path(metadata_path)
            if p.exists():
                integ["metadata_sha256"] = sha256_file(p)

        if hash_mcap and mcap_path:
            p = Path(mcap_path)
            if p.exists():
                integ["mcap_sha256"] = sha256_file(p)

    write_json(index_path, idx)
