"""
plotting.py

Deterministic plotting utilities for calibration experiments.

Principles:
- Matplotlib only (no seaborn, no hidden styles)
- No hard-coded colors unless explicitly required by a spec
- SI units in labels
- Save figures with consistent DPI and tight bounding box
- Never depend on interactive backends (CI/headless safe)

This module is intentionally small: experiment scripts own the narrative.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence, Tuple, Union

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

Array = np.ndarray


def _ensure_parent(path: Union[str, Path]) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def savefig(fig: matplotlib.figure.Figure, path: Union[str, Path], *, dpi: int = 150) -> None:
    p = _ensure_parent(path)
    fig.savefig(p, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def plot_timeseries(
    t: Array,
    y: Array,
    *,
    title: str,
    xlabel: str = "Time (s)",
    ylabel: str = "",
    y2: Optional[Array] = None,
    y2_label: Optional[str] = None,
) -> matplotlib.figure.Figure:
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    if t.shape != y.shape:
        raise ValueError("t and y must have the same shape")

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(t, y, label=ylabel if ylabel else None)

    if y2 is not None:
        y2 = np.asarray(y2, dtype=float)
        if y2.shape != t.shape:
            raise ValueError("t and y2 must have the same shape")
        ax.plot(t, y2, label=y2_label if y2_label else None)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    if (ylabel and ylabel.strip()) or y2 is not None:
        ax.legend(loc="best")

    ax.grid(True)
    return fig


def plot_histogram(
    x: Array,
    *,
    title: str,
    xlabel: str,
    ylabel: str = "Count",
    bins: int = 50,
) -> matplotlib.figure.Figure:
    x = np.asarray(x, dtype=float)
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.hist(x, bins=bins)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    return fig


def plot_scatter_with_fit(
    x: Array,
    y: Array,
    y_fit: Array,
    *,
    title: str,
    xlabel: str,
    ylabel: str,
    fit_label: str = "Fit",
) -> matplotlib.figure.Figure:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    y_fit = np.asarray(y_fit, dtype=float)
    if not (x.shape == y.shape == y_fit.shape):
        raise ValueError("x, y, y_fit must have the same shape")

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(x, y, s=12, label="Measured")
    ax.plot(x, y_fit, label=fit_label)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(loc="best")
    ax.grid(True)
    return fig


def plot_xy_path(
    x: Array,
    y: Array,
    *,
    title: str = "Trajectory",
    xlabel: str = "X (m)",
    ylabel: str = "Y (m)",
    equal_aspect: bool = True,
) -> matplotlib.figure.Figure:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape:
        raise ValueError("x and y must have the same shape")

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(x, y)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if equal_aspect:
        ax.set_aspect("equal", adjustable="box")
    ax.grid(True)
    return fig
