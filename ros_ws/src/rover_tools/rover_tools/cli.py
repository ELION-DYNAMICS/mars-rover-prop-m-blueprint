from __future__ import annotations

import argparse
import json
from pathlib import Path

from .bag_record import record_bag
from .bag_export import export_bag_to_csv
from .dataset_package import package_dataset
from .metrics_eval import evaluate_metrics


def main() -> None:
    p = argparse.ArgumentParser(prog="rover_tools", description="Rover operations tooling.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("record", help="Record a rosbag2 (MCAP) using a topic set YAML.")
    pr.add_argument("--out", required=True, help="Output directory for bag (ros2 bag -o).")
    pr.add_argument("--topics", required=True, help="YAML file listing topics.")
    pr.add_argument("--storage", default="mcap", help="Storage ID (default: mcap).")

    pp = sub.add_parser("package", help="Package a dataset into datasets/<run_id>/ with metadata + hashes.")
    pp.add_argument("--repo-root", required=True, help="Repo root path containing /datasets and /datasets/schemas.")
    pp.add_argument("--run-id", required=True, help="Run ID (directory name).")
    pp.add_argument("--bag", required=True, help="Path to .mcap file.")
    pp.add_argument("--metadata", required=True, help="Path to run_metadata.json to ingest (will be validated).")
    pp.add_argument("--plots", default="", help="Optional plots directory to copy.")

    pe = sub.add_parser("export", help="Export bag to CSV (requires ros2 bag convert support).")
    pe.add_argument("--bag", required=True, help="Path to .mcap file or bag directory.")
    pe.add_argument("--out", required=True, help="Output directory for CSV export.")

    pm = sub.add_parser("metrics", help="Generate metrics.json from the packaged dataset evidence.")
    pm.add_argument("--dataset", required=True, help="datasets/<run_id>/ directory.")
    pm.add_argument(
        "--non-strict",
        action="store_true",
        help="Allow partial metrics output when required artifacts are missing.",
    )

    args = p.parse_args()

    if args.cmd == "record":
        code = record_bag(Path(args.out), Path(args.topics), storage_id=args.storage)
        raise SystemExit(code)

    if args.cmd == "package":
        repo_root = Path(args.repo_root)
        run_id = args.run_id
        bag = Path(args.bag)
        meta_path = Path(args.metadata)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        plots_dir = Path(args.plots) if args.plots else None

        out_dir = package_dataset(repo_root, run_id, bag, meta, plots_dir=plots_dir)
        print(str(out_dir))
        return

    if args.cmd == "export":
        code = export_bag_to_csv(Path(args.bag), Path(args.out))
        raise SystemExit(code)

    if args.cmd == "metrics":
        out = evaluate_metrics(Path(args.dataset), strict=not args.non_strict)
        print(str(out))
        return
