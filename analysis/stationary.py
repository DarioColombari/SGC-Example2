"""Identification of stationary operating periods."""

from __future__ import annotations

import pandas as pd


def find_stationary_periods(
    frame: pd.DataFrame,
    *,
    minimum_duration_s: float = 180.0,
    relative_tolerance: float = 0.05,
    minimum_samples: int = 3,
) -> pd.DataFrame:
    """Return samples belonging to stable, sufficiently long operating windows.

    Stability is evaluated on ``P_in`` and ``n_el`` using the range divided by
    the absolute mean. Non-finite values are excluded from candidate windows.
    """
    required = {"elapsed_s", "P_in", "n_el"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Colonne necessarie mancanti: {sorted(missing)}")
    numeric = frame[["elapsed_s", "P_in", "n_el"]].apply(
        pd.to_numeric, errors="coerce"
    )
    finite = numeric.notna()
    for column in numeric.columns:
        finite[column] &= numeric[column].ne(float("inf"))
        finite[column] &= numeric[column].ne(float("-inf"))
    valid = frame.loc[
        finite.all(axis=1) & numeric["P_in"].gt(0)
    ].copy()
    valid[["elapsed_s", "P_in", "n_el"]] = numeric.loc[valid.index]
    if len(valid) < minimum_samples:
        return frame.iloc[0:0].copy()

    valid = valid.sort_values("elapsed_s")
    stable = pd.Series(False, index=valid.index)
    start = 0
    values = valid.reset_index(drop=False)
    for end in range(len(values)):
        duration = values.loc[end, "elapsed_s"] - values.loc[start, "elapsed_s"]
        while duration >= minimum_duration_s and start <= end:
            window = values.iloc[start : end + 1]
            stable.loc[window["index"]] = (
                len(window) >= minimum_samples
                and _relative_range(window["P_in"]) <= relative_tolerance
                and _relative_range(window["n_el"]) <= relative_tolerance
            )
            start += 1
            if start <= end:
                duration = values.loc[end, "elapsed_s"] - values.loc[start, "elapsed_s"]
    return valid.loc[stable.reindex(valid.index, fill_value=False)]


def _relative_range(values: pd.Series) -> float:
    mean = abs(float(values.mean()))
    if mean == 0:
        return float("inf") if values.max() != values.min() else 0.0
    return float((values.max() - values.min()) / mean)
