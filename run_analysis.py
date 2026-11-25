"""Run the engine analysis and create the consolidated efficiency plot."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from src.aggregation import aggregate_efficiency
from src.data_loading import load_measurement_file
from src.stationary import identify_stationary_periods


DEFAULT_DATASET_DIR = Path("experimentalResults")
DEFAULT_OUTPUT_DIR = Path("results")
OUTPUT_FILENAME = "electrical_efficiency_by_load.png"
PER_FILE_OUTPUT_FILENAME = "electrical_efficiency_by_file.png"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser, including the production dataset default."""
    parser = argparse.ArgumentParser(
        description="Analyse CSV measurements and plot n_el versus engine load.",
        epilog=(
            "The default dataset directory is /experimentalResults. "
            "Use --dataset-dir to select another directory."
        ),
    )
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=DEFAULT_DATASET_DIR,
        help="directory containing the measurement CSV files "
        "(default: /experimentalResults)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="directory for the generated PNG (default: results)",
    )
    return parser


def load_files_individually(dataset_dir: Path) -> pd.DataFrame:
    """Load each CSV separately and combine the cleaned measurements."""
    files = sorted(dataset_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {dataset_dir}")
    return pd.concat(
        [load_measurement_file(path) for path in files],
        ignore_index=True,
    )


def plot_efficiency_by_load(
    aggregated: pd.DataFrame,
    output_path: Path,
) -> Path:
    """Save n_el versus load, with one standard-colour series per H2 value."""
    required = {"h2_percent", "load_percent", "n_el_mean", "n_el_std"}
    missing = required.difference(aggregated.columns)
    if missing:
        raise ValueError(f"Missing plotting columns: {sorted(missing)}")
    if aggregated.empty:
        raise ValueError("No aggregated stationary measurements available")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(9, 6))
    try:
        for h2_percent, group in aggregated.groupby("h2_percent", sort=True):
            ordered = group.sort_values("load_percent")
            axis.errorbar(
                ordered["load_percent"],
                ordered["n_el_mean"],
                yerr=ordered["n_el_std"],
                marker="o",
                capsize=4,
                label=f"{h2_percent:g}% H₂",
            )

        axis.set_title("Electrical efficiency versus engine load")
        axis.set_xlabel("Engine load (%)")
        axis.set_ylabel("Electrical efficiency n_el (-)")
        axis.grid(True, alpha=0.3)
        axis.legend(title="Hydrogen in fuel mixture")
        figure.tight_layout()
        figure.savefig(output_path, dpi=300, format="png")
    finally:
        plt.close(figure)
    return output_path


def plot_efficiency_by_file(
    stationary: pd.DataFrame,
    output_path: Path,
) -> Path:
    """Save one n_el versus load subplot for every source CSV file."""
    required = {"source_file", "h2_percent", "load_percent", "n_el"}
    missing = required.difference(stationary.columns)
    if missing:
        raise ValueError(f"Missing per-file plotting columns: {sorted(missing)}")
    if stationary.empty:
        raise ValueError("No stationary measurements available for per-file plot")

    grouped_files = list(stationary.groupby("source_file", sort=True))
    columns = min(4, len(grouped_files))
    rows = math.ceil(len(grouped_files) / columns)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(
        rows,
        columns,
        figsize=(5 * columns, 4 * rows),
        squeeze=False,
    )
    try:
        flattened_axes = axes.ravel()
        for axis, (source_file, group) in zip(flattened_axes, grouped_files):
            ordered = group.sort_values("load_percent")
            h2_values = group["h2_percent"].dropna().unique()
            h2_label = f"{h2_values[0]:g}%" if len(h2_values) else "unknown"
            axis.scatter(
                ordered["load_percent"],
                ordered["n_el"],
                s=12,
                alpha=0.7,
            )
            axis.set_title(f"{source_file}\nH₂: {h2_label}")
            axis.set_xlabel("Engine load (%)")
            axis.set_ylabel("Electrical efficiency n_el (-)")
            axis.grid(True, alpha=0.3)

        for axis in flattened_axes[len(grouped_files):]:
            axis.set_visible(False)
        figure.tight_layout()
        figure.savefig(output_path, dpi=300, format="png")
    finally:
        plt.close(figure)
    return output_path


def main(argv: Sequence[str] | None = None) -> int:
    """Execute loading, stationary-period detection, aggregation and plotting."""
    arguments = build_parser().parse_args(argv)
    measurements = load_files_individually(arguments.dataset_dir)
    stationary = identify_stationary_periods(measurements)
    aggregated = aggregate_efficiency(stationary)
    summary_path = plot_efficiency_by_load(
        aggregated,
        arguments.output_dir / OUTPUT_FILENAME,
    )
    per_file_path = plot_efficiency_by_file(
        stationary,
        arguments.output_dir / PER_FILE_OUTPUT_FILENAME,
    )
    print(f"Generated: {summary_path}")
    print(f"Generated: {per_file_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
