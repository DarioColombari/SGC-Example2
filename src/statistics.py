from __future__ import annotations

import numpy as np
import pandas as pd


N_EL_SENTINEL_VALUES = (-999.0,)


def aggregate_efficiency(
    stationary_data: pd.DataFrame,
    *,
    load_step: float = 1.0,
) -> pd.DataFrame:
    """Aggregate finite n_el values by H2 percentage and WT01 load level."""
    if load_step <= 0:
        raise ValueError("load_step must be greater than zero")
    data = stationary_data.copy()
    data["n_el"] = pd.to_numeric(data["n_el"], errors="coerce")
    data["WT01"] = pd.to_numeric(data["WT01"], errors="coerce")
    data["n_el"] = data["n_el"].replace(N_EL_SENTINEL_VALUES, np.nan)
    data = data.replace([np.inf, -np.inf], np.nan)
    data["load_level"] = (data["WT01"] / load_step).round() * load_step
    data = data.dropna(subset=["n_el", "WT01", "h2_percent"])
    if data.empty:
        return pd.DataFrame(columns=["h2_percent", "load_level", "mean_n_el", "std_n_el", "n_samples"])
    summary = (
        data.groupby(["h2_percent", "load_level"], as_index=False)["n_el"]
        .agg(mean_n_el="mean", std_n_el="std", n_samples="count")
    )
    summary = summary[summary["n_samples"] > 1].copy()
    summary["std_n_el"] = summary["std_n_el"].fillna(0.0)
    return summary.sort_values(["h2_percent", "load_level"]).reset_index(drop=True)

