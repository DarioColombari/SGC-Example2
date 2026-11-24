from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

LOAD_LEVEL_LABEL = "Load level [%]"
EFFICIENCY_LABEL = "Electrical efficiency (n_el)"


def save_efficiency_plot(summary: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(8, 5))
    for h2_percent, group in summary.groupby("h2_percent"):
        axis.errorbar(
            group["load_level"],
            group["mean_n_el"],
            yerr=group["std_n_el"],
            marker="o",
            capsize=3,
            label=f"H2 {h2_percent:g}%",
        )
    axis.set_xlabel("Load level (WT01)")
    axis.set_ylabel("Electrical efficiency (n_el)")
    axis.set_title("Electrical efficiency by load level")
    axis.grid(True, alpha=0.3)
    if not summary.empty:
        axis.legend(title="Hydrogen")
    figure.tight_layout()
    figure.savefig(output_path, dpi=300)
    plt.close(figure)


def save_efficiency_subplots(
    summary: pd.DataFrame,
    output_path: Path,
    *,
    p_nom: float = 30.0,
    max_columns: int = 4,
    x_limits: tuple[float, float] | None = None,
    y_limits: tuple[float, float] | None = None,
) -> None:
    """Save efficiency/load subplots with common limits for every H2 value."""
    if p_nom <= 0:
        raise ValueError("p_nom must be greater than zero")
    if max_columns < 1:
        raise ValueError("max_columns must be greater than zero")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    hydrogen_values = sorted(summary["h2_percent"].dropna().unique())
    if not hydrogen_values:
        hydrogen_values = [None]

    load_percent = summary["load_level"] / p_nom * 100
    if x_limits is None and summary.empty:
        x_limits = (0.0, 100.0)
    elif x_limits is None:
        x_min = float(load_percent.min())
        x_max = float(load_percent.max())
        x_margin = max((x_max - x_min) * 0.05, 1.0)
        x_limits = (x_min - x_margin, x_max + x_margin)
    if y_limits is None and summary.empty:
        y_limits = (0.0, 1.0)
    elif y_limits is None:
        y_min = float((summary["mean_n_el"] - summary["std_n_el"]).min())
        y_max = float((summary["mean_n_el"] + summary["std_n_el"]).max())
        y_margin = max((y_max - y_min) * 0.05, 0.01)
        y_limits = (y_min - y_margin, y_max + y_margin)

    column_count = min(len(hydrogen_values), max_columns)
    row_count = math.ceil(len(hydrogen_values) / column_count)
    figure, axes = plt.subplots(
        row_count,
        column_count,
        figsize=(6 * column_count, 5 * row_count),
        sharex=True,
        sharey=True,
        squeeze=False,
    )
    flat_axes = list(axes.flat)
    for axis, hydrogen in zip(flat_axes, hydrogen_values):
        group = summary if hydrogen is None else summary[summary["h2_percent"] == hydrogen]
        group = group.sort_values("load_level")
        group_load_percent = group["load_level"] / p_nom * 100
        axis.errorbar(
            group_load_percent,
            group["mean_n_el"],
            yerr=group["std_n_el"],
            marker="o",
            capsize=3,
        )
        axis.set_title("Hydrogen: no data" if hydrogen is None else f"H2 {hydrogen:g}%")
        axis.set_xlabel(LOAD_LEVEL_LABEL)
        axis.set_xlim(*x_limits)
        axis.set_ylim(*y_limits)
        axis.grid(True, alpha=0.3)
    for axis in flat_axes[len(hydrogen_values) :]:
        axis.set_visible(False)
    for row_axes in axes:
        row_axes[0].set_ylabel(EFFICIENCY_LABEL)
    figure.tight_layout()
    figure.savefig(output_path, dpi=300)
    plt.close(figure)


def save_efficiency_lines_plot(
    summary: pd.DataFrame,
    output_path: Path,
    *,
    p_nom: float,
    x_limits: tuple[float, float],
    y_limits: tuple[float, float],
) -> None:
    """Save all hydrogen efficiency trends in one plot."""
    if p_nom <= 0:
        raise ValueError("p_nom must be greater than zero")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(9, 6))
    for hydrogen, group in summary.groupby("h2_percent", sort=True):
        group = group.sort_values("load_level")
        load_percent = group["load_level"] / p_nom * 100
        axis.errorbar(
            load_percent,
            group["mean_n_el"],
            yerr=group["std_n_el"],
            marker="o",
            capsize=3,
            label=f"H2 {hydrogen:g}%",
        )
    axis.set_xlabel(LOAD_LEVEL_LABEL)
    axis.set_ylabel(EFFICIENCY_LABEL)
    axis.set_xlim(*x_limits)
    axis.set_ylim(*y_limits)
    axis.grid(True, alpha=0.3)
    if not summary.empty:
        axis.legend(title="Hydrogen")
    figure.tight_layout()
    figure.savefig(output_path, dpi=300)
    plt.close(figure)

