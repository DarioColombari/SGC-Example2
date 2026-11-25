"""Aggregation of stationary electrical efficiency measurements."""

from __future__ import annotations

import pandas as pd


def aggregate_efficiency(stationary_measurements: pd.DataFrame) -> pd.DataFrame:
    """Aggregate n_el by hydrogen percentage and stationary load level."""
    required = {"h2_percent", "load_percent", "n_el"}
    missing = required.difference(stationary_measurements.columns)
    if missing:
        raise ValueError(f"Missing aggregation columns: {sorted(missing)}")
    result = (
        stationary_measurements.groupby(["h2_percent", "load_percent"], as_index=False)["n_el"]
        .agg(n_el_mean="mean", n_el_std="std", sample_count="count")
        .sort_values(["h2_percent", "load_percent"], ignore_index=True)
    )
    return result
