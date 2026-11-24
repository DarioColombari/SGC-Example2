from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


def _header_row(path: Path) -> int:
    with path.open(encoding="utf-8-sig") as file:
        for index, line in enumerate(file):
            if line.lstrip().startswith("Time;"):
                return index
    raise ValueError(f"No CSV header beginning with 'Time;' found in {path}")


def _clean_column_name(name: object) -> str:
    return str(name).strip()


def read_measurement(path: Path) -> pd.DataFrame:
    """Read one measurement file and convert its measurement columns to numbers."""
    frame = pd.read_csv(
        path,
        sep=";",
        decimal=",",
        skiprows=_header_row(path),
        dtype=str,
        engine="python",
    )
    frame.columns = [_clean_column_name(column) for column in frame.columns]
    frame = frame.loc[:, ~frame.columns.str.match(r"^Unnamed")]
    for column in frame.columns:
        if column != "Time":
            values = frame[column].astype("string").str.strip().str.replace(",", ".", regex=False)
            frame[column] = pd.to_numeric(values, errors="coerce")
    if "WT01" not in frame or "n_el" not in frame:
        raise ValueError(f"{path} must contain WT01 and n_el columns")
    frame["source_file"] = path.name
    frame["h2_percent"] = extract_h2_percent(path.name)
    return frame.replace([float("inf"), float("-inf")], pd.NA)


def read_dataset(dataset_dir: Path) -> pd.DataFrame:
    files = sorted(dataset_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {dataset_dir}")
    return pd.concat((read_measurement(path) for path in files), ignore_index=True)


def extract_h2_percent(filename: str) -> float:
    match = re.search(r"(?:^|[_-])(\d+(?:[.,]\d+)?)", Path(filename).stem)
    if match is None:
        raise ValueError(f"Cannot extract H2 percentage from filename {filename}")
    return float(match.group(1).replace(",", "."))

