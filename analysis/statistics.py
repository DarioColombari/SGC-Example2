"""Aggregation of stationary electrical efficiency samples."""

from __future__ import annotations

import pandas as pd


def aggregate_efficiency(stationary: pd.DataFrame) -> pd.DataFrame:
    """Compute mean, standard deviation and count of finite ``n_el`` values."""
    required = {"h2_percent", "load_percent", "n_el"}
    missing = required.difference(stationary.columns)
    if missing:
        raise ValueError(f"Colonne necessarie mancanti: {sorted(missing)}")
    values = stationary[pd.notna(stationary["n_el"])].copy()
    values = values[values["n_el"].map(lambda value: abs(float(value)) != float("inf"))]
    result = (
        values.groupby(["h2_percent", "load_percent"], as_index=False)["n_el"]
        .agg(mean="mean", std="std", count="count")
        .rename(columns={"mean": "n_el_mean", "std": "n_el_std", "count": "n_samples"})
    )
    return result.sort_values(["h2_percent", "load_percent"]).reset_index(drop=True)
