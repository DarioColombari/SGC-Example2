from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .data_io import read_dataset
from .plotting import save_efficiency_plot
from .statistics import aggregate_efficiency
from .stationary import identify_stationary_periods


@dataclass(frozen=True)
class PipelineConfig:
    dataset_dir: Path
    output_dir: Path
    window_size: int = 3
    stationary_std: float = 0.5
    min_points: int = 3
    load_step: float = 1.0


def run_pipeline(config: PipelineConfig):
    measurements = read_dataset(config.dataset_dir)
    stationary = identify_stationary_periods(
        measurements,
        window_size=config.window_size,
        std_threshold=config.stationary_std,
        min_points=config.min_points,
    )
    summary = aggregate_efficiency(stationary, load_step=config.load_step)
    config.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = config.output_dir / "efficiency_summary.csv"
    plot_path = config.output_dir / "electrical_efficiency.png"
    summary.to_csv(summary_path, index=False)
    save_efficiency_plot(summary, plot_path)
    return summary, summary_path, plot_path

