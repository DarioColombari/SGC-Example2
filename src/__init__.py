"""Pipeline for analysing engine experimental data."""

from .aggregation import aggregate_efficiency
from .data_loading import load_dataset, load_measurement_file
from .pipeline import analyse_dataset
from .plotting import plot_efficiency_summary
from .stationary import identify_stationary_periods

__all__ = [
    "aggregate_efficiency",
    "identify_stationary_periods",
    "load_dataset",
    "load_measurement_file",
    "analyse_dataset",
    "plot_efficiency_summary",
]
