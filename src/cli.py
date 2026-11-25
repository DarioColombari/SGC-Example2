"""Command-line entry point for the engine data analysis pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .pipeline import analyse_dataset
from .plotting import plot_efficiency_summary


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser used by both CLI and VS Code runs."""
    parser = argparse.ArgumentParser(
        description="Analyse engine measurements and create an efficiency summary plot."
    )
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=Path("sampleResults"),
        help="directory containing measurement CSV files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results") / "sample",
        help="directory where generated outputs are saved",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the analysis and save its summary plot."""
    arguments = build_parser().parse_args(argv)
    _, aggregated = analyse_dataset(arguments.dataset_dir)
    output_path = plot_efficiency_summary(
        aggregated,
        arguments.output_dir / "efficiency_summary.png",
    )
    print(f"Generated: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
