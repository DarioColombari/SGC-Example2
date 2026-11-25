"""Reading and cleaning measurement CSV files."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {"Time", "WT01", "n_el"}
_H2_PATTERN = re.compile(r"prova_auto[_-](\d+(?:[.,]\d+)?)", re.IGNORECASE)


def extract_h2_percentage(path: str | Path) -> float:
    """Extract the hydrogen percentage encoded in a measurement filename."""
    name = Path(path).stem
    match = _H2_PATTERN.search(name)
    if match is None:
        match = re.search(r"\d+(?:[.,]\d+)?", name)
    if match is None:
        raise ValueError(f"Hydrogen percentage not found in filename: {name}")
    return float(match.group(1).replace(",", ".")) if match.lastindex else float(match.group(0).replace(",", "."))


def _header_row(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        for index, line in enumerate(stream):
            columns = {item.strip() for item in line.rstrip("\r\n").split(";")}
            if REQUIRED_COLUMNS.issubset(columns):
                return index
    raise ValueError(f"CSV header with required columns not found: {path}")


def _parse_elapsed_time(values: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(
        values.astype(str).str.strip(),
        format="%H:%M:%S",
        errors="coerce",
    )
    if parsed.isna().any():
        raise ValueError("Invalid value in Time column")

    seconds = parsed.map(
        lambda timestamp: (
            timestamp.hour * 3600
            + timestamp.minute * 60
            + timestamp.second
        )
    ).to_numpy(dtype=float)
    elapsed = np.zeros(len(seconds), dtype=float)
    if len(seconds) > 1:
        intervals = np.diff(seconds)
        rollover = intervals < 0
        intervals[rollover] += 24 * 60 * 60
        elapsed[1:] = np.cumsum(intervals)
    return pd.Series(elapsed, index=values.index, name="elapsed_seconds")


def load_measurement_file(path: str | Path) -> pd.DataFrame:
    """Load one measurement file and return cleaned, numeric measurements."""
    file_path = Path(path)
    header = _header_row(file_path)
    frame = pd.read_csv(
        file_path,
        sep=";",
        decimal=",",
        skiprows=header,
        skipinitialspace=True,
        dtype=str,
        index_col=False,
        usecols=lambda column: not str(column).strip().startswith("Unnamed"),
        encoding="utf-8-sig",
    )
    frame.columns = [str(column).strip() for column in frame.columns]
    frame = frame.loc[:, ~frame.columns.str.match(r"^Unnamed")]
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns in {file_path.name}: {sorted(missing)}")

    frame["Time"] = frame["Time"].astype(str).str.strip()
    frame["elapsed_seconds"] = _parse_elapsed_time(frame["Time"])
    for column in ("WT01", "P_in", "n_th", "n_el"):
        if column in frame:
            values = frame[column].astype(str).str.strip().str.replace(",", ".", regex=False)
            frame[column] = pd.to_numeric(values, errors="coerce").replace([np.inf, -np.inf], np.nan)
    frame["h2_percent"] = extract_h2_percentage(file_path)
    frame["source_file"] = file_path.name
    frame = frame.dropna(subset=["WT01", "n_el"]).reset_index(drop=True)
    return frame


def load_dataset(dataset_dir: str | Path) -> pd.DataFrame:
    """Load all CSV files in a directory, preserving their source metadata."""
    directory = Path(dataset_dir)
    files = sorted(directory.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {directory}")
    frames = [load_measurement_file(path) for path in files]
    return pd.concat(frames, ignore_index=True)
