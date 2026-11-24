"""Run the efficiency analysis separately for every measurement CSV.

The default input directory is ``experimentalResults``. Each CSV produces its
own summary and plot; a final figure compares all hydrogen percentages.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.data_io import extract_h2_percent, read_measurement
from src.plotting import save_efficiency_lines_plot, save_efficiency_subplots
from src.statistics import aggregate_efficiency
from src.stationary import identify_stationary_periods

P_NOM = 30.0
MAX_SUBPLOT_COLUMNS = 4
SUBPLOT_X_LIMITS = (20.0, 100.0)
SUBPLOT_Y_LIMITS = (0.15, 0.35)


def analyse_file(
    csv_path: Path,
    output_dir: Path,
    *,
    window_size: int = 3,
    stationary_std: float = 0.5,
    min_points: int = 3,
    load_step: float = 1.0,
) -> tuple[pd.DataFrame, Path, Path]:
    """Analyse one CSV and return its summary and plot paths."""
    measurements = read_measurement(csv_path)
    stationary = identify_stationary_periods(
        measurements,
        window_size=window_size,
        std_threshold=stationary_std,
        min_points=min_points,
    )
    summary = aggregate_efficiency(stationary, load_step=load_step)

    h2_percent = extract_h2_percent(csv_path.name)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{csv_path.stem}_H2-{h2_percent:g}"
    summary_path = output_dir / f"{stem}_efficiency_summary.csv"
    plot_path = output_dir / f"{stem}_electrical_efficiency_subplots.png"
    summary.to_csv(summary_path, index=False)
    save_efficiency_subplots(
        summary,
        plot_path,
        p_nom=P_NOM,
        max_columns=MAX_SUBPLOT_COLUMNS,
        x_limits=SUBPLOT_X_LIMITS,
        y_limits=SUBPLOT_Y_LIMITS,
    )
    return summary, summary_path, plot_path


def analyse_directory(
    dataset_dir: Path,
    output_dir: Path,
    *,
    window_size: int = 3,
    stationary_std: float = 0.5,
    min_points: int = 3,
    load_step: float = 1.0,
) -> tuple[list[pd.DataFrame], list[tuple[Path, Path]]]:
    """Analyse CSV files one at a time and return generated output paths."""
    csv_paths = sorted(dataset_dir.glob("*.csv"))
    if not csv_paths:
        raise FileNotFoundError(f"No CSV files found in {dataset_dir}")

    summaries = []
    outputs = []
    for csv_path in csv_paths:
        summary, summary_path, plot_path = analyse_file(
            csv_path,
            output_dir,
            window_size=window_size,
            stationary_std=stationary_std,
            min_points=min_points,
            load_step=load_step,
        )
        summaries.append(summary)
        outputs.append((summary_path, plot_path))
    return summaries, outputs


def save_combined_efficiency_plot(
    summaries: list[pd.DataFrame],
    output_dir: Path,
) -> Path:
    """Save one figure containing a subplot for each hydrogen percentage."""
    combined_summary = pd.concat(summaries, ignore_index=True)
    plot_path = output_dir / "combined_electrical_efficiency_subplots.png"
    save_efficiency_subplots(
        combined_summary,
        plot_path,
        p_nom=P_NOM,
        max_columns=MAX_SUBPLOT_COLUMNS,
        x_limits=SUBPLOT_X_LIMITS,
        y_limits=SUBPLOT_Y_LIMITS,
    )
    return plot_path


def save_combined_efficiency_lines_plot(
    summaries: list[pd.DataFrame],
    output_dir: Path,
) -> Path:
    """Save all hydrogen percentages as separate lines in one plot."""
    combined_summary = pd.concat(summaries, ignore_index=True)
    plot_path = output_dir / "combined_electrical_efficiency_lines.png"
    save_efficiency_lines_plot(
        combined_summary,
        plot_path,
        p_nom=P_NOM,
        x_limits=SUBPLOT_X_LIMITS,
        y_limits=SUBPLOT_Y_LIMITS,
    )
    return plot_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate one generator-load efficiency plot per CSV dataset."
    )
    parser.add_argument("--dataset-dir", type=Path, default=Path("experimentalResults"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/experimental"))
    parser.add_argument("--window-size", type=int, default=3)
    parser.add_argument("--stationary-std", type=float, default=0.5)
    parser.add_argument("--min-points", type=int, default=3)
    parser.add_argument("--load-step", type=float, default=1.0)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summaries, outputs = analyse_directory(
        args.dataset_dir,
        args.output_dir,
        window_size=args.window_size,
        stationary_std=args.stationary_std,
        min_points=args.min_points,
        load_step=args.load_step,
    )
    for summary_path, plot_path in outputs:
        print(f"Summary: {summary_path}")
        print(f"Plot: {plot_path}")
    combined_plot_path = save_combined_efficiency_plot(summaries, args.output_dir)
    print(f"Combined plot: {combined_plot_path}")
    lines_plot_path = save_combined_efficiency_lines_plot(summaries, args.output_dir)
    print(f"Combined lines plot: {lines_plot_path}")


if __name__ == "__main__":
    main()
