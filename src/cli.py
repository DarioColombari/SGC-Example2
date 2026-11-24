from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import PipelineConfig, run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyse engine measurements.")
    parser.add_argument("--dataset-dir", type=Path, default=Path("sampleResults"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/sample"))
    parser.add_argument("--window-size", type=int, default=3)
    parser.add_argument("--stationary-std", type=float, default=0.5)
    parser.add_argument("--min-points", type=int, default=3)
    parser.add_argument("--load-step", type=float, default=1.0)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary, summary_path, plot_path = run_pipeline(PipelineConfig(**vars(args)))
    print(f"Aggregated groups: {len(summary)}")
    print(f"Summary: {summary_path}")
    print(f"Plot: {plot_path}")

