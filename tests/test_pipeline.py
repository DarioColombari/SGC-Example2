import sys
from pathlib import Path

import matplotlib
import pandas as pd
import pytest

matplotlib.use("Agg")

from analysis.io import load_dataset
from analysis.plotting import plot_efficiency
from analysis.statistics import aggregate_efficiency
from analysis.stationary import find_stationary_periods


def _write_csv(tmp_path: Path, name: str, rows: list[str], columns: str | None = None) -> Path:
    header = columns or "Time; P_in; n_el; ZY-FC02; AP-02;"
    path = tmp_path / name
    path.write_text(
        "Start Time: | 23:58:00\nSelected mode: | Extracted Data\n"
        "Test Duration: | 1 hr\n" + header + "\n" + "\n".join(rows) + "\n",
        encoding="utf-8",
    )
    return path


def test_load_dataset_cleans_csv_and_unwraps_midnight(tmp_path):
    path = _write_csv(
        tmp_path,
        "prova_auto_5_costante-75.csv",
        [
            "23:59:50; 10,0; 0,25; 5; -2370,37",
            "00:00:00; 10,2; 0,26; 5; -2370,37",
        ],
    )

    frame = load_dataset(path)

    assert list(frame.columns) == ["Time", "P_in", "n_el", "ZY-FC02", "AP-02",
                                   "elapsed_s", "h2_percent", "load_percent"]
    assert frame["h2_percent"].iat[0] == 5
    assert frame["load_percent"].iat[0] == 75
    assert frame["elapsed_s"].tolist() == [0, 10]
    assert pd.isna(frame["AP-02"].iat[0])


def test_load_dataset_uses_h2_column_when_filename_has_no_h2(tmp_path):
    path = _write_csv(
        tmp_path,
        "prova_auto_struttura_costante-50.csv",
        ["00:00:00; 10,0; 0,2; 4; 0"],
    )

    assert load_dataset(path)["h2_percent"].iat[0] == 4


def test_load_dataset_rejects_missing_h2_metadata(tmp_path):
    path = _write_csv(tmp_path, "test_costante-50.csv", ["00:00:00; 10; 0,2; ; 0"])

    with pytest.raises(ValueError, match="H2"):
        load_dataset(path)


def test_load_dataset_preserves_missing_and_infinite_efficiency(tmp_path):
    path = _write_csv(
        tmp_path,
        "prova_auto_0_costante-75.csv",
        ["00:00:00; 0; -Inf; 0; 0", "00:00:10; 10; ; 0; 0"],
    )

    frame = load_dataset(path)

    assert pd.isna(frame["n_el"].iat[1])
    assert frame["n_el"].iat[0] == float("-inf")


def test_stationary_period_requires_three_minutes():
    frame = pd.DataFrame(
        {
            "elapsed_s": [0, 60, 120],
            "P_in": [10.0, 10.1, 10.0],
            "n_el": [0.2, 0.21, 0.2],
        }
    )

    assert find_stationary_periods(frame).empty


def test_stationary_period_excludes_nonfinite_and_zero_input():
    frame = pd.DataFrame(
        {
            "elapsed_s": [0, 60, 120, 180, 240],
            "P_in": [0.0, 10.0, 10.0, 10.0, 10.0],
            "n_el": [float("-inf"), 0.2, 0.2, 0.2, 0.2],
        }
    )

    result = find_stationary_periods(frame)

    assert result["elapsed_s"].tolist() == [60, 120, 180, 240]


def test_aggregate_efficiency_excludes_infinite_values_and_groups_metadata():
    frame = pd.DataFrame(
        {
            "h2_percent": [0, 0, 5],
            "load_percent": [50, 50, 75],
            "n_el": [0.2, float("inf"), 0.3],
        }
    )

    result = aggregate_efficiency(frame)

    assert result[["h2_percent", "load_percent", "n_samples"]].to_dict("records") == [
        {"h2_percent": 0, "load_percent": 50, "n_samples": 1},
        {"h2_percent": 5, "load_percent": 75, "n_samples": 1},
    ]
    assert result["n_el_mean"].tolist() == [0.2, 0.3]
    assert result["n_el_std"].isna().all()


def test_plot_handles_missing_combinations_and_closes_figure(tmp_path):
    summary = pd.DataFrame(
        {
            "h2_percent": [0, 5],
            "load_percent": [50, 50],
            "n_el_mean": [0.2, 0.25],
            "n_el_std": [0.01, 0.02],
        }
    )
    output = tmp_path / "summary.png"

    plot_efficiency(summary, output)

    assert output.exists()
    assert output.stat().st_size > 0
    assert not matplotlib.pyplot.get_fignums()


def test_plot_rejects_unaggregated_input(tmp_path):
    with pytest.raises(ValueError, match="Colonne"):
        plot_efficiency(pd.DataFrame({"n_el": [0.2]}), tmp_path / "plot.png")


def test_cli_reports_missing_dataset(tmp_path, monkeypatch):
    from analysis.__main__ import main

    monkeypatch.setattr(
        sys,
        "argv",
        ["analysis", "--dataset-dir", str(tmp_path / "missing"), "--output-dir",
         str(tmp_path / "out")],
    )

    with pytest.raises(FileNotFoundError):
        main()
