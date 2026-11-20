"""Command-line entry point for the analysis pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from .io import load_directory
from .plotting import plot_efficiency
from .statistics import aggregate_efficiency
from .stationary import find_stationary_periods


def main() -> None:
    parser = argparse.ArgumentParser(description="Analizza i risultati delle prove motore.")
    parser.add_argument("--dataset-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    data = load_directory(args.dataset_dir)
    stationary = find_stationary_periods(data)
    summary = aggregate_efficiency(stationary)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output_dir / "efficiency_summary.csv", index=False)
    plot_efficiency(summary, args.output_dir / "efficiency_summary.png")
    print(f"Campioni stazionari: {len(stationary)}")
    print(f"Riepilogo: {args.output_dir / 'efficiency_summary.csv'}")
    print(f"Grafico: {args.output_dir / 'efficiency_summary.png'}")


if __name__ == "__main__":
    main()
