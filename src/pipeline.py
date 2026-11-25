"""Composition of loading, stationary-period detection and aggregation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .aggregation import aggregate_efficiency
from .data_loading import load_dataset
from .stationary import identify_stationary_periods


def analyse_dataset(dataset_dir: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return stationary samples and their aggregated efficiency statistics."""
    measurements = load_dataset(dataset_dir)
    stationary = identify_stationary_periods(measurements)
    return stationary, aggregate_efficiency(stationary)
