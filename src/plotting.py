"""Plots for already aggregated engine efficiency data."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


REQUIRED_COLUMNS = {
    "h2_percent",
    "load_percent",
    "n_el_mean",
    "n_el_std",
}


def plot_efficiency_summary(
    aggregated: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    """Save a summary plot from the statistics produced by the data pipeline."""
    missing = REQUIRED_COLUMNS.difference(aggregated.columns)
    if missing:
        raise ValueError(f"Missing plotting columns: {sorted(missing)}")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(9, 6))
    try:
        if aggregated.empty:
            axis.text(
                0.5,
                0.5,
                "No valid stationary periods found",
                ha="center",
                va="center",
                transform=axis.transAxes,
            )
        else:
            for load_percent, group in aggregated.groupby("load_percent", sort=True):
                ordered = group.sort_values("h2_percent")
                axis.errorbar(
                    ordered["h2_percent"],
                    ordered["n_el_mean"],
                    yerr=ordered["n_el_std"],
                    marker="o",
                    capsize=4,
                    label=f"{load_percent:g}% load",
                )

        axis.set_title("Electrical efficiency by hydrogen percentage and load")
        axis.set_xlabel("Hydrogen in fuel mixture H₂ (%)")
        axis.set_ylabel("Electrical efficiency n_el (-)")
        axis.grid(True, alpha=0.3)
        if not aggregated.empty:
            axis.legend(title="Engine load")
        figure.tight_layout()
        figure.savefig(destination, dpi=300, format="png")
    finally:
        plt.close(figure)
    return destination
