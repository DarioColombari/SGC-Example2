from __future__ import annotations

import numpy as np
import pandas as pd

try:
    from scipy.ndimage import uniform_filter1d
except ImportError:
    uniform_filter1d = None


def _rolling_standard_deviation(values: np.ndarray, window: int) -> np.ndarray:
    if uniform_filter1d is not None:
        mean = uniform_filter1d(values, size=window, mode="nearest")
        squared_mean = uniform_filter1d(values * values, size=window, mode="nearest")
    else:
        padding = window // 2
        padded = np.pad(values, padding, mode="edge")
        mean = np.convolve(padded, np.ones(window) / window, mode="valid")
        squared_mean = np.convolve(padded * padded, np.ones(window) / window, mode="valid")
    return np.sqrt(np.maximum(squared_mean - mean * mean, 0.0))


def identify_stationary_periods(
    frame: pd.DataFrame,
    *,
    window_size: int = 3,
    std_threshold: float = 0.5,
    min_points: int = 3,
) -> pd.DataFrame:
    """Return rows belonging to stationary WT01 periods."""
    if window_size < 2 or window_size % 2 == 0:
        raise ValueError("window_size must be an odd integer greater than one")
    if min_points < 1 or std_threshold < 0:
        raise ValueError("min_points and std_threshold must be positive")

    result = frame.copy()
    signal = pd.to_numeric(result["WT01"], errors="coerce").to_numpy(dtype=float)
    valid = np.isfinite(signal)
    smooth_std = np.full(len(signal), np.inf)
    source_files = (
        result["source_file"].astype("string").to_numpy()
        if "source_file" in result
        else np.full(len(result), "")
    )
    segment_ids = np.full(len(result), -1, dtype=int)
    segment = 0
    start = 0
    while start < len(signal):
        if not valid[start]:
            start += 1
            continue
        end = start + 1
        while end < len(signal) and valid[end] and source_files[end] == source_files[start]:
            end += 1
        segment_ids[start:end] = segment
        if end - start >= window_size:
            smooth_std[start:end] = _rolling_standard_deviation(signal[start:end], window_size)
        segment += 1
        start = end
    stationary = valid & (smooth_std <= std_threshold)

    labels = np.full(len(result), -1, dtype=int)
    period = 0
    start = 0
    while start < len(stationary):
        if not stationary[start]:
            start += 1
            continue
        end = start
        while (
            end < len(stationary)
            and stationary[end]
            and segment_ids[end] == segment_ids[start]
        ):
            end += 1
        if end - start >= min_points:
            labels[start:end] = period
            period += 1
        start = end

    result["stationary_period"] = labels
    result = result[result["stationary_period"] >= 0].copy()
    result.attrs["min_points"] = min_points
    return result

