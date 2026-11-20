"""CSV loading and normalisation."""

from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd

_H2_FROM_NAME = re.compile(r"prova_auto_(\d+(?:[.,]\d+)?)", re.IGNORECASE)
_LOAD_FROM_NAME = re.compile(r"costante[-_](\d+(?:[.,]\d+)?)", re.IGNORECASE)
_SENSOR_SENTINELS = (-2370.37,)


def _read_csv(path: Path) -> pd.DataFrame:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    header_index = next(
        (index for index, line in enumerate(lines) if line.lstrip().startswith("Time;")),
        None,
    )
    if header_index is None:
        raise ValueError(f"CSV senza intestazione Time: {path}")
    if header_index + 1 >= len(lines):
        raise ValueError(f"CSV senza righe di dati: {path}")

    header = lines[header_index].rstrip(";")
    data = "\n".join([header, *lines[header_index + 1 :]])
    return pd.read_csv(
        io.StringIO(data),
        sep=";",
        decimal=",",
        na_values=["", "NA", "N/A"],
        keep_default_na=True,
    )


def _normalise_columns(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result.columns = [str(column).strip() for column in result.columns]
    result = result.loc[:, ~result.columns.str.startswith("Unnamed")]
    for column in result.columns:
        if column != "Time":
            numeric = pd.to_numeric(result[column], errors="coerce")
            result[column] = numeric.mask(numeric.isin(_SENSOR_SENTINELS))
    return result


def _metadata_from_name(path: Path, frame: pd.DataFrame) -> tuple[float, float]:
    h2_match = _H2_FROM_NAME.search(path.stem)
    load_match = _LOAD_FROM_NAME.search(path.stem)
    if h2_match:
        h2 = float(h2_match.group(1).replace(",", "."))
    elif "ZY-FC02" in frame and frame["ZY-FC02"].notna().any():
        h2 = float(frame["ZY-FC02"].dropna().median())
    else:
        raise ValueError(f"Percentuale H2 non determinabile: {path.name}")

    if not load_match:
        raise ValueError(f"Livello di carico non determinabile: {path.name}")
    return h2, float(load_match.group(1).replace(",", "."))


def _elapsed_seconds(values: pd.Series) -> pd.Series:
    parsed = pd.to_timedelta(values.astype(str), errors="coerce").dt.total_seconds()
    seconds = parsed.diff()
    midnight = seconds.lt(0)
    offsets = midnight.cumsum() * 24 * 60 * 60
    return parsed + offsets


def load_dataset(path: str | Path) -> pd.DataFrame:
    """Load one exported test file and add normalised metadata columns."""
    csv_path = Path(path)
    if not csv_path.is_file():
        raise FileNotFoundError(csv_path)
    frame = _normalise_columns(_read_csv(csv_path))
    required = {"Time", "n_el", "P_in"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Colonne obbligatorie mancanti in {csv_path.name}: {sorted(missing)}")
    h2, load = _metadata_from_name(csv_path, frame)
    frame["elapsed_s"] = _elapsed_seconds(frame["Time"])
    frame["h2_percent"] = h2
    frame["load_percent"] = load
    return frame


def load_directory(dataset_dir: str | Path) -> pd.DataFrame:
    """Load all CSV files in a dataset directory."""
    paths = sorted(Path(dataset_dir).glob("*.csv"))
    if not paths:
        raise FileNotFoundError(f"Nessun file CSV in {dataset_dir}")
    return pd.concat((load_dataset(path) for path in paths), ignore_index=True)
