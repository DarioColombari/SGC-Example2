"""Summary plot generation."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def plot_efficiency(summary: pd.DataFrame, output_path: str | Path) -> Path:
    """Plot an already aggregated efficiency summary and save it at 300 dpi."""
    required = {"h2_percent", "load_percent", "n_el_mean", "n_el_std"}
    missing = required.difference(summary.columns)
    if missing:
        raise ValueError(f"Colonne necessarie mancanti: {sorted(missing)}")
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(8, 5))
    for load, group in summary.groupby("load_percent"):
        axis.errorbar(
            group["h2_percent"],
            group["n_el_mean"],
            yerr=group["n_el_std"].fillna(0),
            marker="o",
            capsize=3,
            label=f"{load:g} % carico",
        )
    axis.set_xlabel("Idrogeno (% vol)")
    axis.set_ylabel("Rendimento elettrico, n_el (-)")
    axis.grid(True, alpha=0.3)
    if not summary.empty:
        axis.legend(title="Livello di carico")
    figure.tight_layout()
    figure.savefig(destination, dpi=300)
    plt.close(figure)
    return destination


def plot_efficiency_by_load(summary: pd.DataFrame, output_path: str | Path) -> Path:
    """Plot efficiency versus load for one hydrogen percentage."""
    required = {"h2_percent", "load_percent", "n_el_mean", "n_el_std"}
    missing = required.difference(summary.columns)
    if missing:
        raise ValueError(f"Colonne necessarie mancanti: {sorted(missing)}")
    h2_values = summary["h2_percent"].dropna().unique()
    if len(h2_values) != 1:
        raise ValueError("Il riepilogo deve contenere una sola percentuale di H2")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    ordered = summary.sort_values("load_percent")
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.errorbar(
        ordered["load_percent"],
        ordered["n_el_mean"],
        yerr=ordered["n_el_std"].fillna(0),
        marker="o",
        capsize=3,
    )
    axis.set_title(f"Efficienza elettrica - H2 {h2_values[0]:g} % vol")
    axis.set_xlabel("Livello di carico (%)")
    axis.set_ylabel("Rendimento elettrico, n_el (-)")
    axis.grid(True, alpha=0.3)
    figure.tight_layout()
    figure.savefig(destination, dpi=300)
    plt.close(figure)
    return destination
