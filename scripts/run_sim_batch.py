#!/usr/bin/env python3
"""
scripts/run_sim_batch.py

Batch runner for simulation scenarios.

This script launches repeatable simulation runs for a given scenario and mode,
records bags, packages datasets, and optionally evaluates metrics.

It is intentionally strict:
- Every run has a run_id.
- Every run produces evidence under /datasets/<run_id>/.
- Failures are recorded with diagnostics; no silent skipping.

Expected repo layout:
  mars-rover-prop-m-blueprint/
    ros_ws/
    datasets/
    datasets/schemas/run_metadata.schema.json
    scenarios/<scenario_name>/scenario.yaml

Requires:
- ROS 2 environment sourced
- rover_sim_gazebo installed (for Gazebo backend)
- rover_tools installed OR scripts/package_dataset.py equivalent (we package here directly)

NOTE:
This runner does not assume your full bringup.launch exists yet.
It launches simulator + (optional) Nav2 + (optional) mission in separate processes.
As the program matures, replace these launch calls with a single bringup.

Phase 0 default:
- start Gazebo world
- (optional) start Nav2
- (optional) start mission bt
- record MCAP for N seconds
- stop everything
- package dataset
- evaluate metrics (optional)

"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Repo-relative defaults
DEFAULT_TOPICS_CFG = "ros_ws/src/rover_tools/config/record_topics_minimal.yaml"

# Conservative topic list fallback if YAML parsing fails
FALLBACK_TOPICS = [
    "/tf",
    "/tf_static",
    "/joint_states",
    "/imu/data",
    "/cmd_vel",
    "/cmd_vel_safe",
    "/odometry/filtered",
    "/mission/state",
]

# Where outputs go
DATASETS_DIR = "datasets"


# -----------------------------
# Small helpers (no dependencies)
# -----------------------------

def now_utc_compact() -> str:
    # ISO-ish compact: YYYYMMDD_HHMMSS
    return time.strftime("%Y%m%d_%H%M%S", time.gmtime())


def run(cmd: List[str], *, env: Optional[Dict[str, str]] = None, cwd: Optional[Path] = None) -> subprocess.Popen:
    return subprocess.Popen(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        preexec_fn=os.setsid,  # so we can kill the entire process group
    )


def kill_proc_group(p: subprocess.Popen, timeout_s: float = 10.0) -> None:
    if p.poll() is not None:
        return
    try:
        os.killpg(os.getpgid(p.pid), signal.SIGINT)
    except Exception:
        pass

    t0 = time.time()
    while time.time() - t0 < timeout_s:
        if p.poll() is not None:
            return
        time.sleep(0.1)

    try:
        os.killpg(os.getpgid(p.pid), signal.SIGKILL)
    except Exception:
        pass


def drain_output(p: subprocess.Popen, max_lines: int = 200) -> List[str]:
    lines: List[str] = []
    if not p.stdout:
        return lines
    try:
        for _ in range(max_lines):
            line = p.stdout.readline()
            if not line:
                break
            lines.append(line.rstrip())
    except Exception:
        pass
    return lines


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_yaml_topics_minimal(path: Path) -> List[str]:
    """
    Minimal YAML parser for:
      topics:
        - /a
        - /b
    """
    try:
        txt = path.read_text(encoding="utf-8")
    except Exception:
        return []
    topics: List[str] = []
    in_topics = False
    for raw in txt.splitlines():
        ln = raw.strip()
        if not ln or ln.startswith("#"):
            continue
        if ln.startswith("topics:"):
            in_topics = True
            continue
        if in_topics and ln.startswith("-"):
            topics.append(ln.split("-", 1)[1].strip())
    return topics


def git_short_hash(repo_root: Path) -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(repo_root), text=True).strip()
        return out
    except Exception:
        return "nogit"


def git_dirty(repo_root: Path) -> bool:
    try:
        out = subprocess.check_output(["git", "status", "--porcelain"], cwd=str(repo_root), text=True)
        return len(out.strip()) > 0
    except Exception:
        return False


# -----------------------------
# Scenario loading
# -----------------------------

def load_scenario(repo_root: Path, scenario_name: str) -> Dict[str, Any]:
    scenario_path = repo_root / "scenarios" / scenario_name / "scenario.yaml"
    if not scenario_path.exists():
        raise FileNotFoundError(f"scenario.yaml not found: {scenario_path}")

    # Minimal YAML reader: we only need a few keys. For Phase 0, parse line-based.
    # If you want full YAML, add PyYAML and do it properly.
    txt = scenario_path.read_text(encoding="utf-8").splitlines()

    def get_value(key: str) -> Optional[str]:
        for ln in txt:
            if ln.strip().startswith(f"{key}:"):
                return ln.split(":", 1)[1].strip().strip('"')
        return None

    # Shallow extraction; world file is nested under defaults/world_gazebo
    world_gazebo = None
    in_defaults = False
    for ln in txt:
        s = ln.rstrip()
        if s.strip() == "defaults:":
            in_defaults = True
            continue
        if in_defaults:
            if s and not s.startswith(" "):  # left indent ended
                in_defaults = False
            if "world_gazebo:" in s:
                world_gazebo = s.split("world_gazebo:", 1)[1].strip()

    return {
        "name": get_value("name") or scenario_name,
        "version": get_value("version") or "unknown",
        "world_gazebo": world_gazebo,
        "scenario_path": str(scenario_path),
    }


# -----------------------------
# Bag recording
# -----------------------------

def record_bag(out_dir: Path, topics: List[str], duration_s: float) -> Path:
    """
    Record MCAP using ros2 bag record. Returns MCAP path.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # ros2 bag record writes <out>_0.mcap etc.
    cmd = ["ros2", "bag", "record", "--storage", "mcap", "-o", str(out_dir)]
    cmd += topics

    p = run(cmd)
    time.sleep(max(0.5, min(2.0, duration_s * 0.1)))  # allow writer to start

    time.sleep(duration_s)
    kill_proc_group(p, timeout_s=10.0)

    # Find produced mcap
    mcaps = sorted(out_dir.parent.glob(out_dir.name + "_*.mcap"))
    if not mcaps:
        # Some distros may write under out_dir directly; check any .mcap
        mcaps = sorted(out_dir.parent.glob("*.mcap"))
    if not mcaps:
        raise RuntimeError(f"no .mcap produced under {out_dir.parent}")
    return mcaps[-1]


# -----------------------------
# Dataset packaging (lightweight)
# -----------------------------

def package_dataset(repo_root: Path, run_id: str, mcap_path: Path, run_metadata: Dict[str, Any]) -> Path:
    target = repo_root / DATASETS_DIR / run_id
    if target.exists():
        raise FileExistsError(f"dataset already exists: {target}")

    target.mkdir(parents=True, exist_ok=False)
    (target / "run.mcap").write_bytes(mcap_path.read_bytes())
    write_json(target / "run_metadata.json", run_metadata)

    # Do not compute hashes here; your rover_tools does that. Phase 0: keep minimal and honest.
    return target


# -----------------------------
# Launch orchestration
# -----------------------------

@dataclass
class RunConfig:
    scenario: str
    mode: str
    backend: str
    duration_s: float
    seed: int
    start_nav2: bool
    start_mission: bool
    topics_cfg: Path


def launch_gazebo_world(repo_root: Path, world_file: str) -> subprocess.Popen:
    # world file expected inside rover_sim_gazebo/worlds
    cmd = ["ros2", "launch", "rover_sim_gazebo", "sim.launch.py", f"world:={Path(world_file).name}"]
    return run(cmd, cwd=repo_root)


def launch_nav2(repo_root: Path, mode: str) -> subprocess.Popen:
    cmd = ["ros2", "launch", "rover_navigation", "nav2.launch.py", f"mode:={mode}", "use_sim_time:=true"]
    return run(cmd, cwd=repo_root)


def launch_mission(repo_root: Path, mode: str, scenario: str) -> subprocess.Popen:
    # Placeholder: use your future BT runner launch. For now, attempt a generic entry.
    # If rover_mission_bt launch doesn't exist yet, this will fail and be recorded.
    cmd = ["ros2", "launch", "rover_mission_bt", "mission.launch.py", f"mode:={mode}", f"scenario:={scenario}"]
    return run(cmd, cwd=repo_root)


# -----------------------------
# Run metadata
# -----------------------------

def build_run_metadata(repo_root: Path, cfg: RunConfig, scenario_info: Dict[str, Any], topics: List[str]) -> Dict[str, Any]:
    commit = git_short_hash(repo_root)
    dirty = git_dirty(repo_root)

    return {
        "schema_version": "0.1",
        "run_id": "",  # filled by caller
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": "simulation",
        "backend": cfg.backend,
        "scenario": cfg.scenario,
        "seed": int(cfg.seed),
        "git": {
            "commit": commit,
            "dirty": bool(dirty),
        },
        "clock": {
            "use_sim_time": True,
        },
        "physics": {
            "notes": "Mars gravity expected; see scenario world.",
        },
        "robot": {
            "variant": "prop-m-blueprint",
        },
        "params": {
            "mode_profile": cfg.mode,
            "scenario_yaml": scenario_info.get("scenario_path", ""),
        },
        "topics": {
            "recorded": topics,
        },
        "artifacts": {
            "bag": "run.mcap",
            "metrics": "metrics.json",
        },
    }


# -----------------------------
# Main
# -----------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Batch runner for simulation scenarios with dataset packaging.")
    ap.add_argument("--scenario", required=True, help="Scenario name under scenarios/")
    ap.add_argument("--mode", default="modern", choices=["modern", "prop_m"], help="Mode profile")
    ap.add_argument("--backend", default="gazebo", choices=["gazebo"], help="Simulation backend (Phase 0: gazebo only)")
    ap.add_argument("--runs", type=int, default=3, help="Number of runs")
    ap.add_argument("--duration", type=float, default=30.0, help="Record duration per run (seconds)")
    ap.add_argument("--seed", type=int, default=0, help="Base seed (incremented per run)")
    ap.add_argument("--topics-cfg", default=DEFAULT_TOPICS_CFG, help="YAML with topic list for recording")
    ap.add_argument("--no-nav2", action="store_true", help="Do not launch Nav2")
    ap.add_argument("--no-mission", action="store_true", help="Do not launch mission BT")
    ap.add_argument("--evaluate-metrics", action="store_true", help="Run scripts/evaluate_metrics.py after packaging")

    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    cfg = RunConfig(
        scenario=args.scenario,
        mode=args.mode,
        backend=args.backend,
        duration_s=float(args.duration),
        seed=int(args.seed),
        start_nav2=not args.no_nav2,
        start_mission=not args.no_mission,
        topics_cfg=(repo_root / args.topics_cfg).resolve(),
    )

    scenario_info = load_scenario(repo_root, cfg.scenario)
    world_file = scenario_info.get("world_gazebo")
    if not world_file:
        print("[run_sim_batch] ERROR: scenario.yaml missing defaults.world_gazebo", file=sys.stderr)
        raise SystemExit(2)

    # Topics
    topics = read_yaml_topics_minimal(cfg.topics_cfg)
    if not topics:
        topics = FALLBACK_TOPICS

    batch_report: Dict[str, Any] = {
        "schema_version": "0.1",
        "scenario": cfg.scenario,
        "mode": cfg.mode,
        "backend": cfg.backend,
        "runs_requested": args.runs,
        "runs": [],
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    for i in range(int(args.runs)):
        run_seed = cfg.seed + i
        run_id = f"{now_utc_compact()}_{cfg.scenario}_{cfg.mode}_{git_short_hash(repo_root)}_{i:02d}"
        print(f"[run_sim_batch] RUN {i+1}/{args.runs} -> {run_id}")

        diagnostics: Dict[str, Any] = {
            "run_id": run_id,
            "status": "ok",
            "notes": [],
            "logs": {},
        }

        p_gz: Optional[subprocess.Popen] = None
        p_nav2: Optional[subprocess.Popen] = None
        p_mission: Optional[subprocess.Popen] = None

        try:
            # Launch simulator
            p_gz = launch_gazebo_world(repo_root, world_file)
            time.sleep(5.0)  # allow gazebo to come up

            # Launch Nav2
            if cfg.start_nav2:
                p_nav2 = launch_nav2(repo_root, cfg.mode)
                time.sleep(3.0)

            # Launch mission (optional; may not exist yet)
            if cfg.start_mission:
                p_mission = launch_mission(repo_root, cfg.mode, cfg.scenario)
                time.sleep(2.0)

            # Record bag
            tmp_bag_base = repo_root / "analysis" / "batch_tmp" / run_id / "bag"
            tmp_bag_base.parent.mkdir(parents=True, exist_ok=True)
            mcap = record_bag(tmp_bag_base, topics, cfg.duration_s)

            # Package dataset
            meta = build_run_metadata(repo_root, cfg, scenario_info, topics)
            meta["run_id"] = run_id
            meta["seed"] = int(run_seed)

            dataset_dir = package_dataset(repo_root, run_id, mcap, meta)

            # Evaluate metrics (optional)
            if args.evaluate_metrics:
                eval_script = repo_root / "scripts" / "evaluate_metrics.py"
                if eval_script.exists():
                    p = subprocess.run(
                        [sys.executable, str(eval_script), str(dataset_dir)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        check=False,
                    )
                    diagnostics["logs"]["evaluate_metrics"] = p.stdout.splitlines()[-200:]
                    if p.returncode != 0:
                        diagnostics["status"] = "partial"
                        diagnostics["notes"].append("metrics evaluation failed (see logs)")

            diagnostics["dataset_dir"] = str(dataset_dir)

        except Exception as e:
            diagnostics["status"] = "error"
            diagnostics["notes"].append(str(e))

        finally:
            # Drain some logs for post-mortem
            if p_mission:
                diagnostics["logs"]["mission_tail"] = drain_output(p_mission)
            if p_nav2:
                diagnostics["logs"]["nav2_tail"] = drain_output(p_nav2)
            if p_gz:
                diagnostics["logs"]["gazebo_tail"] = drain_output(p_gz)

            # Stop processes
            if p_mission:
                kill_proc_group(p_mission)
            if p_nav2:
                kill_proc_group(p_nav2)
            if p_gz:
                kill_proc_group(p_gz)

        batch_report["runs"].append(diagnostics)

    # Write batch report
    out = repo_root / "analysis" / "batch_reports" / f"batch_{now_utc_compact()}_{cfg.scenario}_{cfg.mode}.json"
    write_json(out, batch_report)
    print(str(out))


if __name__ == "__main__":
    main()
