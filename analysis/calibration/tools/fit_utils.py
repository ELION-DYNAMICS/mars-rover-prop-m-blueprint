"""
fit_utils.py

Numerical fitting utilities for calibration experiments (E01–E04).

Design goals:
- Deterministic output (given same inputs + seed)
- Explicit bounds handling
- Minimal dependencies (NumPy-first)
- Optional SciPy acceleration if available
- Engineer-friendly failure modes (fail loudly, return diagnostics)

This module is intentionally generic:
- terramechanics fits (Bekker, Wong proxies)
- slip/traction curve fits
- simple regression and bootstrapped uncertainty estimates

SI units only. Angles in radians internally (degrees only for IO/display).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Union

import math
import numpy as np

Array = np.ndarray


# -----------------------------
# Data structures
# -----------------------------

@dataclass(frozen=True)
class FitResult:
    name: str
    params: Dict[str, float]
    cost: float
    success: bool
    n_iter: int
    message: str
    diagnostics: Dict[str, Union[float, int, str, List[float]]]


# -----------------------------
# Core helpers
# -----------------------------

def set_deterministic_seed(seed: int) -> np.random.Generator:
    """Return a deterministic RNG generator."""
    if not isinstance(seed, int):
        raise TypeError("seed must be an int")
    return np.random.default_rng(seed)


def clamp(x: Union[float, Array], lo: Union[float, Array], hi: Union[float, Array]) -> Union[float, Array]:
    """Clamp scalar/array to [lo, hi]."""
    return np.minimum(np.maximum(x, lo), hi)


def assert_finite(name: str, arr: Array) -> None:
    """Raise if any values are NaN/inf."""
    if not np.all(np.isfinite(arr)):
        bad = np.where(~np.isfinite(arr))[0]
        raise ValueError(f"{name} contains non-finite values at indices {bad[:10].tolist()} (showing up to 10)")


def robust_huber(residuals: Array, delta: float) -> Array:
    """
    Huber loss per-sample.
    For |r| <= delta: 0.5 r^2
    Else: delta*(|r| - 0.5*delta)
    """
    if delta <= 0:
        raise ValueError("delta must be > 0")
    r = residuals
    a = np.abs(r)
    quad = a <= delta
    out = np.empty_like(r, dtype=float)
    out[quad] = 0.5 * r[quad] ** 2
    out[~quad] = delta * (a[~quad] - 0.5 * delta)
    return out


def weighted_mse(residuals: Array, weights: Optional[Array] = None) -> float:
    """Compute weighted MSE; weights need not be normalized."""
    assert_finite("residuals", residuals)
    if weights is None:
        return float(np.mean(residuals ** 2))
    assert_finite("weights", weights)
    if residuals.shape != weights.shape:
        raise ValueError("weights must have same shape as residuals")
    w = np.maximum(weights, 0.0)
    denom = float(np.sum(w)) if float(np.sum(w)) > 0 else float(len(w))
    return float(np.sum(w * (residuals ** 2)) / denom)


def finite_difference_grad(
    f: Callable[[Array], float],
    x: Array,
    eps: float = 1e-6
) -> Array:
    """Central finite-difference gradient for small parameter vectors."""
    if eps <= 0:
        raise ValueError("eps must be > 0")
    x = np.asarray(x, dtype=float)
    g = np.zeros_like(x, dtype=float)
    fx = f(x)
    if not np.isfinite(fx):
        raise ValueError("Objective returned non-finite value at starting point")
    for i in range(x.size):
        x1 = x.copy()
        x2 = x.copy()
        x1[i] += eps
        x2[i] -= eps
        f1 = f(x1)
        f2 = f(x2)
        if not (np.isfinite(f1) and np.isfinite(f2)):
            # If gradient is undefined at a perturbation, keep g[i]=0 and continue.
            continue
        g[i] = (f1 - f2) / (2.0 * eps)
    return g


# -----------------------------
# Lightweight bounded optimizer (NumPy-only)
# -----------------------------

def projected_gradient_descent(
    f: Callable[[Array], float],
    x0: Array,
    bounds: Sequence[Tuple[float, float]],
    *,
    max_iter: int = 500,
    step0: float = 0.1,
    tol: float = 1e-8,
    grad_eps: float = 1e-6,
    backtrack: float = 0.5,
    min_step: float = 1e-8,
    verbose: bool = False
) -> Tuple[Array, float, bool, int, str]:
    """
    Simple projected gradient descent with backtracking line search.

    This is intentionally conservative and deterministic.
    Use SciPy if available for better convergence; this is the fallback.
    """
    x = np.asarray(x0, dtype=float).copy()
    if x.ndim != 1:
        raise ValueError("x0 must be a 1D vector")
    if len(bounds) != x.size:
        raise ValueError("bounds must match x0 dimension")

    lo = np.array([b[0] for b in bounds], dtype=float)
    hi = np.array([b[1] for b in bounds], dtype=float)
    if np.any(lo > hi):
        raise ValueError("Invalid bounds: lower > upper")

    x = clamp(x, lo, hi)
    fx = f(x)
    if not np.isfinite(fx):
        return x, float("inf"), False, 0, "Objective is non-finite at initial point"

    step = float(step0)
    for it in range(1, max_iter + 1):
        g = finite_difference_grad(f, x, eps=grad_eps)
        if not np.all(np.isfinite(g)):
            return x, fx, False, it, "Gradient became non-finite"

        gnorm = float(np.linalg.norm(g))
        if gnorm < tol:
            return x, fx, True, it, "Converged: gradient norm below tolerance"

        # Backtracking line search
        improved = False
        local_step = step
        for _ in range(50):
            x_new = clamp(x - local_step * g, lo, hi)
            f_new = f(x_new)
            if np.isfinite(f_new) and f_new <= fx:
                x, fx = x_new, float(f_new)
                improved = True
                break
            local_step *= backtrack
            if local_step < min_step:
                break

        if verbose:
            print(f"[PGD] iter={it} cost={fx:.6g} step={local_step:.3g} |g|={gnorm:.3g}")

        if not improved:
            return x, fx, False, it, "No improvement (step size underflow or local minimum)"
        step = max(local_step * 1.05, min_step)

    return x, fx, False, max_iter, "Max iterations reached"


# -----------------------------
# SciPy wrapper (optional)
# -----------------------------

def bounded_least_squares(
    residual_fn: Callable[[Array], Array],
    x0: Array,
    bounds: Sequence[Tuple[float, float]],
    *,
    loss: str = "linear",
    f_scale: float = 1.0,
    max_nfev: int = 2000
) -> Tuple[Array, float, bool, int, str]:
    """
    Prefer SciPy's least_squares if available; otherwise fall back to PGD on sum of squares.
    residual_fn(x) -> residual vector
    """
    x0 = np.asarray(x0, dtype=float)
    lo = np.array([b[0] for b in bounds], dtype=float)
    hi = np.array([b[1] for b in bounds], dtype=float)
    x0 = clamp(x0, lo, hi)

    def obj(x: Array) -> float:
        r = residual_fn(x)
        assert_finite("residuals", r)
        return float(np.mean(r ** 2))

    try:
        from scipy.optimize import least_squares  # type: ignore
        res = least_squares(
            fun=residual_fn,
            x0=x0,
            bounds=(lo, hi),
            loss=loss,
            f_scale=f_scale,
            max_nfev=max_nfev,
        )
        cost = float(np.mean(res.fun ** 2)) if res.fun is not None else float("inf")
        return np.asarray(res.x, dtype=float), cost, bool(res.success), int(res.nfev), str(res.message)
    except Exception:
        # Fallback: optimize mean squared residual
        x, cost, ok, it, msg = projected_gradient_descent(
            f=obj,
            x0=x0,
            bounds=bounds,
            max_iter=min(500, max_nfev),
            step0=0.1,
            tol=1e-8,
        )
        return x, float(cost), bool(ok), int(it), msg


# -----------------------------
# Model-specific fit helpers
# -----------------------------

def fit_exp_saturation(
    s: Array,
    F: Array,
    *,
    bounds: Optional[Dict[str, Tuple[float, float]]] = None,
    weights: Optional[Array] = None
) -> FitResult:
    """
    Fit traction saturation model:
      F(s) = F_max * (1 - exp(-s / s0))

    Inputs:
      s: slip ratio (dimensionless), expected s >= 0
      F: measured traction force [N], expected F >= 0 (after sign convention)
    """
    s = np.asarray(s, dtype=float)
    F = np.asarray(F, dtype=float)
    if s.shape != F.shape:
        raise ValueError("s and F must have the same shape")
    assert_finite("s", s)
    assert_finite("F", F)

    # Clamp negatives (engineer choice: force negative traction is a sign bug upstream)
    s_cl = np.maximum(s, 0.0)
    F_cl = np.maximum(F, 0.0)

    b = bounds or {}
    Fmax_lo, Fmax_hi = b.get("F_max", (0.0, float(np.max(F_cl) * 5.0 + 1.0)))
    s0_lo, s0_hi = b.get("s0", (1e-3, 1.0))

    # Reasonable init
    Fmax0 = float(np.max(F_cl) + 1e-6)
    # crude: s0 near slip at ~63% of max
    target = 0.63 * Fmax0
    idx = np.argmin(np.abs(F_cl - target))
    s00 = float(np.clip(s_cl[idx] if s_cl.size else 0.2, s0_lo, s0_hi))

    x0 = np.array([Fmax0, s00], dtype=float)
    bounds_vec = [(Fmax_lo, Fmax_hi), (s0_lo, s0_hi)]

    def residual_fn(x: Array) -> Array:
        Fmax, s0 = float(x[0]), float(x[1])
        pred = Fmax * (1.0 - np.exp(-s_cl / max(s0, 1e-9)))
        r = pred - F_cl
        if weights is not None:
            w = np.sqrt(np.maximum(weights, 0.0))
            return r * w
        return r

    x, cost, ok, n, msg = bounded_least_squares(residual_fn, x0, bounds_vec, loss="linear")

    return FitResult(
        name="exp_saturation",
        params={"F_max": float(x[0]), "s0": float(x[1])},
        cost=float(cost),
        success=bool(ok),
        n_iter=int(n),
        message=msg,
        diagnostics={
            "n_samples": int(s.size),
            "F_max_init": float(Fmax0),
            "s0_init": float(s00),
            "F_max_bounds": [float(Fmax_lo), float(Fmax_hi)],
            "s0_bounds": [float(s0_lo), float(s0_hi)],
        },
    )


def fit_powerlaw_W_vs_z(
    z: Array,
    W: Array,
    *,
    fit_n: bool = True,
    bounds: Optional[Dict[str, Tuple[float, float]]] = None,
) -> FitResult:
    """
    Fit power law:
      W = k * z^(n_plus_1)
    where n_plus_1 = n + 1 (Bekker integrated approximation).

    This fit is used in E03 to estimate n (and k_eq proxy).
    Later mapping to (kc, kphi) requires wheel geometry assumptions.

    Inputs:
      z: sinkage depth [m] (must be > 0)
      W: normal load [N]   (must be > 0)
    """
    z = np.asarray(z, dtype=float)
    W = np.asarray(W, dtype=float)
    if z.shape != W.shape:
        raise ValueError("z and W must have the same shape")
    assert_finite("z", z)
    assert_finite("W", W)

    # Filter strictly positive values (anything else is non-physical for this fit)
    mask = (z > 0) & (W > 0)
    if np.count_nonzero(mask) < 3:
        return FitResult(
            name="powerlaw_W_vs_z",
            params={},
            cost=float("inf"),
            success=False,
            n_iter=0,
            message="Insufficient positive samples for log-fit (need >= 3).",
            diagnostics={"n_samples": int(z.size), "n_positive": int(np.count_nonzero(mask))},
        )

    z1 = z[mask]
    W1 = W[mask]

    # log(W) = log(k) + (n+1)*log(z)
    X = np.log(z1)
    Y = np.log(W1)

    # Linear regression closed-form
    Xc = X - np.mean(X)
    denom = float(np.sum(Xc ** 2))
    if denom <= 0:
        return FitResult(
            name="powerlaw_W_vs_z",
            params={},
            cost=float("inf"),
            success=False,
            n_iter=0,
            message="Degenerate sinkage values; cannot regress slope.",
            diagnostics={"n_samples": int(z.size), "n_positive": int(np.count_nonzero(mask))},
        )
    slope = float(np.sum(Xc * (Y - np.mean(Y))) / denom)
    intercept = float(np.mean(Y) - slope * np.mean(X))

    # Bounds and optional refinement
    b = bounds or {}
    n_lo, n_hi = b.get("n", (0.5, 1.2))
    # slope = n+1
    slope_lo, slope_hi = (n_lo + 1.0, n_hi + 1.0)
    slope = float(np.clip(slope, slope_lo, slope_hi))
    k = float(np.exp(intercept))

    # Evaluate residuals in log space
    Y_pred = np.log(k) + slope * np.log(z1)
    resid = Y_pred - Y
    cost = float(np.mean(resid ** 2))

    params = {
        "k_eq": k,
        "n_plus_1": slope,
        "n": slope - 1.0,
    }

    return FitResult(
        name="powerlaw_W_vs_z",
        params=params,
        cost=cost,
        success=True,
        n_iter=1,
        message="Closed-form log-linear fit (with slope clamped to bounds).",
        diagnostics={
            "n_samples": int(z.size),
            "n_positive": int(np.count_nonzero(mask)),
            "bounds_n": [float(n_lo), float(n_hi)],
        },
    )


# -----------------------------
# Windowing utilities (steady-state selection)
# -----------------------------

def steady_state_window(
    t: Array,
    signal: Array,
    *,
    settle_s: float = 2.0,
    min_window_s: float = 5.0,
    max_std: Optional[float] = None
) -> Tuple[int, int]:
    """
    Pick a simple steady-state window:
    - drop initial settle_s
    - pick longest remaining segment
    - optionally enforce max std

    Returns (i0, i1) indices such that [i0:i1] is the window.

    Engineer note:
    This is intentionally conservative and transparent.
    If you need fancy segmentation, implement in experiment-specific code.
    """
    t = np.asarray(t, dtype=float)
    signal = np.asarray(signal, dtype=float)
    if t.shape != signal.shape:
        raise ValueError("t and signal must have same shape")
    assert_finite("t", t)
    assert_finite("signal", signal)
    if t.size < 5:
        raise ValueError("Need at least 5 samples to select a window")
    if settle_s < 0 or min_window_s <= 0:
        raise ValueError("Invalid settle_s/min_window_s")

    t0 = float(t[0]) + float(settle_s)
    start = int(np.searchsorted(t, t0, side="left"))
    if start >= t.size - 2:
        return 0, t.size

    # Ensure minimum duration
    t_min_end = float(t[start]) + float(min_window_s)
    end_min = int(np.searchsorted(t, t_min_end, side="left"))
    if end_min <= start:
        end_min = min(start + 1, t.size)

    # Default window to end
    i0, i1 = start, t.size

    if max_std is not None:
        # Slide a window and pick first that satisfies variance bound (conservative)
        for j1 in range(end_min, t.size + 1):
            seg = signal[start:j1]
            if seg.size < 5:
                continue
            if float(np.std(seg)) <= float(max_std):
                i0, i1 = start, j1
                break

    return i0, i1


# -----------------------------
# Bootstrap uncertainty (simple, deterministic)
# -----------------------------

def bootstrap_parameter_ci(
    fit_fn: Callable[[Array], Dict[str, float]],
    data: Array,
    *,
    n_boot: int = 200,
    seed: int = 42,
    ci: float = 0.95
) -> Dict[str, Dict[str, float]]:
    """
    Generic bootstrap CI for parameter estimates.

    fit_fn(samples) must return a dict of scalar params.
    data: 2D array (N, D) or 1D (N,) depending on your fit_fn.

    Returns:
      {param_name: {"mean":..., "p_lo":..., "p_hi":..., "std":...}}
    """
    if not (0.0 < ci < 1.0):
        raise ValueError("ci must be in (0,1)")
    rng = set_deterministic_seed(seed)
    data = np.asarray(data)
    N = int(data.shape[0])
    if N < 10:
        raise ValueError("Need at least 10 samples for bootstrap")

    samples: Dict[str, List[float]] = {}
    for _ in range(int(n_boot)):
        idx = rng.integers(0, N, size=N)
        boot = data[idx]
        params = fit_fn(boot)
        for k, v in params.items():
            samples.setdefault(k, []).append(float(v))

    out: Dict[str, Dict[str, float]] = {}
    alpha = (1.0 - ci) / 2.0
    for k, vals in samples.items():
        arr = np.asarray(vals, dtype=float)
        out[k] = {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0,
            "p_lo": float(np.quantile(arr, alpha)),
            "p_hi": float(np.quantile(arr, 1.0 - alpha)),
        }
    return out
