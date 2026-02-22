"""
metrics.py

Calibration metrics and evaluation utilities.

Responsibilities:
- Compute slip ratio, basic kinematic/dynamic metrics
- Provide robust time-derivative utilities (with smoothing)
- Provide summary statistics used by E01–E04 and reports
- Provide simple acceptance checks (pass/fail with reasons)

Engineering intent:
Metrics must be deterministic and transparent.
If assumptions are violated -> raise or return explicit failure reasons.

SI units only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

Array = np.ndarray


# -----------------------------
# Data structures
# -----------------------------

@dataclass(frozen=True)
class MetricSummary:
    name: str
    values: Dict[str, float]
    pass_fail: Optional[bool]
    reasons: List[str]


# -----------------------------
# Basic numerical utilities
# -----------------------------

def assert_monotonic_time(t: Array) -> None:
    t = np.asarray(t, dtype=float)
    if t.ndim != 1 or t.size < 2:
        raise ValueError("t must be a 1D array with at least 2 samples")
    dt = np.diff(t)
    if np.any(dt <= 0):
        bad = np.where(dt <= 0)[0]
        raise ValueError(f"time is not strictly increasing (bad indices: {bad[:10].tolist()})")


def moving_average(x: Array, window: int) -> Array:
    x = np.asarray(x, dtype=float)
    if window <= 1:
        return x.copy()
    if window > x.size:
        raise ValueError("window larger than signal length")
    kernel = np.ones(window, dtype=float) / float(window)
    return np.convolve(x, kernel, mode="same")


def deriv(t: Array, x: Array, *, smooth_window: int = 1) -> Array:
    """
    Compute dx/dt using central differences, with optional moving average smoothing
    applied to x before differentiation.

    This is intentionally simple and deterministic.
    """
    t = np.asarray(t, dtype=float)
    x = np.asarray(x, dtype=float)
    if t.shape != x.shape:
        raise ValueError("t and x must have the same shape")
    assert_monotonic_time(t)
    if smooth_window > 1:
        x = moving_average(x, smooth_window)

    dx = np.gradient(x, t)
    return dx


# -----------------------------
# Core metrics
# -----------------------------

def slip_ratio(
    v_ideal: Array,
    v_actual: Array,
    *,
    epsilon: float = 1e-6,
    clamp_nonphysical: bool = True,
) -> Array:
    """
    Slip ratio definition used by this project:

      s = (v_ideal - v_actual) / max(|v_ideal|, epsilon)

    Notes:
    - v_ideal typically = r * omega (per wheel or averaged)
    - v_actual from ground truth derivative or filtered odometry derivative
    - If clamp_nonphysical=True, negative slip is allowed (braking) but can be flagged upstream.
    """
    v_ideal = np.asarray(v_ideal, dtype=float)
    v_actual = np.asarray(v_actual, dtype=float)
    if v_ideal.shape != v_actual.shape:
        raise ValueError("v_ideal and v_actual must have the same shape")

    denom = np.maximum(np.abs(v_ideal), float(epsilon))
    s = (v_ideal - v_actual) / denom

    if clamp_nonphysical:
        # Allow braking slip (negative), but clamp extreme numerical spikes
        s = np.clip(s, -2.0, 2.0)

    return s


def basic_stats(x: Array) -> Dict[str, float]:
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        raise ValueError("Cannot compute stats on empty array")
    return {
        "mean": float(np.mean(x)),
        "std": float(np.std(x, ddof=1)) if x.size > 1 else 0.0,
        "var": float(np.var(x, ddof=1)) if x.size > 1 else 0.0,
        "min": float(np.min(x)),
        "max": float(np.max(x)),
        "p05": float(np.quantile(x, 0.05)),
        "p50": float(np.quantile(x, 0.50)),
        "p95": float(np.quantile(x, 0.95)),
    }


def steady_segment_mask(
    t: Array,
    v_cmd: Array,
    *,
    settle_s: float = 2.0,
    min_speed_mps: float = 0.01,
    max_cmd_std: Optional[float] = None,
) -> Array:
    """
    Compute a boolean mask for a steady-state segment based on command signal.
    Conservative: discard initial settle time and require command above min speed.

    Optional: enforce small command standard deviation (max_cmd_std).
    """
    t = np.asarray(t, dtype=float)
    v_cmd = np.asarray(v_cmd, dtype=float)
    if t.shape != v_cmd.shape:
        raise ValueError("t and v_cmd must have the same shape")
    assert_monotonic_time(t)

    t0 = float(t[0]) + float(settle_s)
    mask = t >= t0
    mask &= np.abs(v_cmd) >= float(min_speed_mps)

    if max_cmd_std is not None:
        # If command is too jittery, reject all (forces upstream fix)
        cmd_std = float(np.std(v_cmd[mask])) if np.any(mask) else float("inf")
        if cmd_std > float(max_cmd_std):
            return np.zeros_like(mask, dtype=bool)

    return mask


# -----------------------------
# Experiment-specific checks (generic)
# -----------------------------

def check_slip_acceptance(
    s: Array,
    *,
    mean_bounds: Tuple[float, float] = (0.05, 0.20),
    var_max: float = 0.01,
    hard_max: float = 0.40,
) -> MetricSummary:
    """
    Basic acceptance check used by E01 and as a sanity check elsewhere.
    """
    s = np.asarray(s, dtype=float)
    stats = basic_stats(s)

    reasons: List[str] = []
    ok = True

    if not (mean_bounds[0] <= stats["mean"] <= mean_bounds[1]):
        ok = False
        reasons.append(f"mean(s)={stats['mean']:.3f} outside bounds {mean_bounds}")

    if stats["var"] > float(var_max):
        ok = False
        reasons.append(f"var(s)={stats['var']:.4f} exceeds {var_max}")

    if stats["max"] > float(hard_max):
        ok = False
        reasons.append(f"max(s)={stats['max']:.3f} exceeds hard_max {hard_max}")

    return MetricSummary(
        name="slip_acceptance",
        values={
            "mean_s": stats["mean"],
            "var_s": stats["var"],
            "p95_s": stats["p95"],
            "max_s": stats["max"],
        },
        pass_fail=ok,
        reasons=reasons,
    )


def force_balance_metrics(
    Fx_measured: Array,
    Fx_model: Array,
    *,
    rel_err_max: float = 0.15,
) -> MetricSummary:
    """
    Evaluate model-or-measured traction force comparison (E04).
    """
    Fx_measured = np.asarray(Fx_measured, dtype=float)
    Fx_model = np.asarray(Fx_model, dtype=float)
    if Fx_measured.shape != Fx_model.shape:
        raise ValueError("Fx_measured and Fx_model must have the same shape")

    denom = np.maximum(np.abs(Fx_measured), 1e-6)
    rel_err = np.abs(Fx_model - Fx_measured) / denom

    stats = basic_stats(rel_err)
    ok = stats["p95"] <= float(rel_err_max)

    reasons: List[str] = []
    if not ok:
        reasons.append(f"p95(relative_error)={stats['p95']:.3f} exceeds {rel_err_max}")

    return MetricSummary(
        name="force_balance",
        values={
            "mean_rel_err": stats["mean"],
            "p95_rel_err": stats["p95"],
            "max_rel_err": stats["max"],
        },
        pass_fail=ok,
        reasons=reasons,
    )
