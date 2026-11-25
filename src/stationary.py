"""Identification of stationary operating periods."""

from __future__ import annotations

import numpy as np
import pandas as pd

NOMINAL_POWER_KW = 30.0
MIN_LOAD_PERCENT = 30.0
STATIONARY_TOLERANCE_KW = 1.0
MIN_DURATION_SECONDS = 30.0 * 60.0


def identify_stationary_periods(
    measurements: pd.DataFrame,
    *,
    min_duration_seconds: float = MIN_DURATION_SECONDS,
    tolerance_kw: float = STATIONARY_TOLERANCE_KW,
    nominal_power_kw: float = NOMINAL_POWER_KW,
    min_load_percent: float = MIN_LOAD_PERCENT,
) -> pd.DataFrame:
    """Return samples belonging to valid stationary periods.

    A period is contiguous, has a WT01 range no wider than twice the documented
    +/-1 kW tolerance, lasts at least 30 minutes, and reaches the documented
    30% minimum load.
    """
    required = {"WT01", "n_el", "elapsed_seconds", "h2_percent"}
    missing = required.difference(measurements.columns)
    if missing:
        raise ValueError(f"Missing stationary-period columns: {sorted(missing)}")
    if tolerance_kw <= 0 or min_duration_seconds < 0 or nominal_power_kw <= 0:
        raise ValueError("Stationary-period parameters must be positive")

    valid_groups: list[pd.DataFrame] = []
    grouping_columns = ["source_file"] if "source_file" in measurements.columns else ["h2_percent"]
    for _, group in measurements.groupby(grouping_columns, sort=False):
        group = group.sort_values("elapsed_seconds").reset_index(drop=True)
        power = group["WT01"].to_numpy(dtype=float)
        for start, end in _candidate_runs_with_tolerance(power, tolerance_kw):
            period = group.iloc[start:end]
            duration = float(period["elapsed_seconds"].iloc[-1] - period["elapsed_seconds"].iloc[0])
            load_percent = float(period["WT01"].mean() / nominal_power_kw * 100)
            if duration >= min_duration_seconds and load_percent >= min_load_percent:
                period = period.copy()
                period["period_id"] = len(valid_groups)
                period["load_percent"] = load_percent
                valid_groups.append(period)
    if not valid_groups:
        return measurements.iloc[0:0].copy().assign(period_id=pd.Series(dtype=int), load_percent=pd.Series(dtype=float))
    return pd.concat(valid_groups, ignore_index=True)


def _candidate_runs_with_tolerance(
    power: np.ndarray, tolerance_kw: float
) -> list[tuple[int, int]]:
    """Split a series when its range exceeds the documented tolerance."""
    runs: list[tuple[int, int]] = []
    start = 0
    for index in range(1, len(power)):
        if np.max(power[start : index + 1]) - np.min(power[start : index + 1]) > 2 * tolerance_kw:
            if index - start > 0:
                runs.append((start, index))
            start = index
    if start < len(power):
        runs.append((start, len(power)))
    return runs
