from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from src.cli import main
from src.data_io import read_measurement
from src.pipeline import PipelineConfig, run_pipeline
from src.statistics import aggregate_efficiency
from src.stationary import identify_stationary_periods


def write_csv(directory: Path, name: str, rows: list[str]) -> Path:
    path = directory / name
    path.write_text(
        "metadata;ignored\n"
        "Time; WT01; n_el; extra\n"
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )
    return path


def test_read_measurement_cleans_header_decimal_and_h2(tmp_path: Path) -> None:
    path = write_csv(tmp_path, "prova_auto_10_costante.csv", ["23:59:50; 15,0; 0,25; 1"])

    frame = read_measurement(path)

    assert frame.loc[0, "WT01"] == pytest.approx(15.0)
    assert frame.loc[0, "n_el"] == pytest.approx(0.25)
    assert frame.loc[0, "h2_percent"] == pytest.approx(10.0)
    assert frame.loc[0, "source_file"] == path.name
    assert " extra" not in frame.columns


def test_read_measurement_converts_missing_and_infinite_values_to_na(tmp_path: Path) -> None:
    path = write_csv(
        tmp_path,
        "prova_auto_0.csv",
        ["23:59:59;15,0;Inf;1", "00:00:09;;-Inf;2", "00:00:19;15,0;;3"],
    )

    frame = read_measurement(path)

    assert frame["n_el"].isna().all()
    assert frame["WT01"].isna().sum() == 1


def test_midnight_rows_are_kept_in_input_order(tmp_path: Path) -> None:
    path = write_csv(
        tmp_path,
        "prova_auto_5.csv",
        ["23:59:59;15,0;0,2;1", "00:00:09;15,0;0,3;2"],
    )

    frame = read_measurement(path)

    assert frame["Time"].tolist() == ["23:59:59", "00:00:09"]


def test_stationary_periods_select_stable_run() -> None:
    frame = pd.DataFrame(
        {
            "WT01": [1.0, 1.1, 0.9, 5.0, 6.0, 6.1, 5.9, 6.0],
            "n_el": [0.1] * 8,
            "h2_percent": [0.0] * 8,
        }
    )

    stationary = identify_stationary_periods(
        frame, window_size=3, std_threshold=0.1, min_points=3
    )

    assert stationary["WT01"].tolist() == pytest.approx([6.1, 5.9, 6.0])
    assert (stationary["WT01"] >= 5.9).all()
    assert stationary["stationary_period"].nunique() == 1


def test_no_stationary_period_returns_empty_frame() -> None:
    frame = pd.DataFrame({"WT01": [0.0, 1.0, 2.0, 3.0], "n_el": [0.1] * 4})

    stationary = identify_stationary_periods(
        frame, window_size=3, std_threshold=0.1, min_points=3
    )

    assert stationary.empty


def test_single_sample_load_group_is_removed_without_merging_levels() -> None:
    frame = pd.DataFrame(
        {
            "WT01": [14.49, 14.51, 14.49],
            "n_el": [0.20, 0.21, 0.22],
            "h2_percent": [0.0, 0.0, 0.0],
        }
    )

    stationary = identify_stationary_periods(
        frame, window_size=3, std_threshold=0.1, min_points=3
    )
    summary = aggregate_efficiency(stationary, load_step=1.0)

    assert len(stationary) == 3
    assert stationary["stationary_period"].nunique() == 1
    assert len(summary) == 1
    assert summary.loc[0, "load_level"] == 14.0
    assert summary.loc[0, "n_samples"] == 2


def test_distinct_load_levels_in_one_period_are_preserved() -> None:
    frame = pd.DataFrame(
        {
            "WT01": [10.1, 10.2, 19.8, 19.9],
            "n_el": [0.20, 0.21, 0.30, 0.31],
            "h2_percent": [0.0] * 4,
            "stationary_period": [0] * 4,
        }
    )

    summary = aggregate_efficiency(frame, load_step=10)

    assert summary["load_level"].tolist() == [10.0, 20.0]
    assert summary["n_samples"].tolist() == [2, 2]


def test_invalid_efficiencies_do_not_leave_one_negative_sample() -> None:
    frame = pd.DataFrame(
        {
            "WT01": [15.0, 15.0, 15.0],
            "n_el": [-0.1, float("inf"), -999.0],
            "h2_percent": [0.0, 0.0, 0.0],
        }
    )

    stationary = identify_stationary_periods(
        frame, window_size=3, std_threshold=0.1, min_points=3
    )
    summary = aggregate_efficiency(stationary)

    assert len(stationary) == 3
    assert summary.empty


def test_missing_wt01_separates_two_valid_stationary_periods() -> None:
    frame = pd.DataFrame(
        {
            "WT01": [10.0, 10.0, 10.0, float("nan"), 20.0, 20.0, 20.0],
            "n_el": [0.2, 0.2, 0.2, 0.2, 0.3, 0.3, 0.3],
            "h2_percent": [0.0] * 7,
        }
    )

    stationary = identify_stationary_periods(
        frame, window_size=3, std_threshold=0.1, min_points=3
    )

    assert stationary["stationary_period"].nunique() == 2
    assert stationary["WT01"].tolist() == [10.0, 10.0, 10.0, 20.0, 20.0, 20.0]


def test_stationary_validation_rejects_even_window() -> None:
    frame = pd.DataFrame({"WT01": [1.0, 1.0, 1.0]})

    with pytest.raises(ValueError, match="odd"):
        identify_stationary_periods(frame, window_size=2)


def test_statistics_keep_only_present_h2_load_combinations() -> None:
    frame = pd.DataFrame(
        {
            "WT01": [10.1, 10.2, 20.0],
            "n_el": [0.2, 0.4, 0.5],
            "h2_percent": [0.0, 0.0, 10.0],
        }
    )

    summary = aggregate_efficiency(frame, load_step=10)

    assert set(map(tuple, summary[["h2_percent", "load_level"]].to_numpy())) == {
        (0.0, 10.0),
    }
    row = summary[(summary["h2_percent"] == 0.0) & (summary["load_level"] == 10.0)].iloc[0]
    assert row["mean_n_el"] == pytest.approx(0.3)
    assert row["std_n_el"] == pytest.approx(0.1414213562)
    assert row["n_samples"] == 2


def test_sentinel_values_are_excluded_from_statistics() -> None:
    frame = pd.DataFrame(
        {"WT01": [10.0, 10.0], "n_el": [-999.0, 0.25], "h2_percent": [0.0, 0.0]}
    )

    summary = aggregate_efficiency(frame)

    assert summary.empty


def test_two_valid_samples_are_kept_after_cleaning() -> None:
    frame = pd.DataFrame(
        {
            "WT01": [15.0, 15.0, 15.0],
            "n_el": [0.2, 0.3, float("inf")],
            "h2_percent": [0.0, 0.0, 0.0],
        }
    )
    stationary = identify_stationary_periods(
        frame, window_size=3, std_threshold=0.1, min_points=3
    )

    summary = aggregate_efficiency(stationary)

    assert summary.loc[0, "mean_n_el"] == pytest.approx(0.25)
    assert summary.loc[0, "n_samples"] == 2


def test_missing_dataset_is_reported() -> None:
    with pytest.raises(FileNotFoundError, match="No CSV files"):
        run_pipeline(PipelineConfig(Path("does-not-exist"), Path("unused")))


def test_cli_generates_summary_and_png_and_closes_figures(tmp_path: Path, monkeypatch) -> None:
    dataset_dir = tmp_path / "dataset"
    output_dir = tmp_path / "output"
    dataset_dir.mkdir()
    write_csv(
        dataset_dir,
        "prova_auto_0.csv",
        [
            "23:59:00;15,0;0,20;1",
            "23:59:10;15,1;0,22;1",
            "23:59:20;14,9;0,24;1",
            "23:59:30;15,0;0,26;1",
        ],
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["python -m src", "--dataset-dir", str(dataset_dir), "--output-dir", str(output_dir)],
    )

    main()

    assert (output_dir / "efficiency_summary.csv").is_file()
    assert (output_dir / "electrical_efficiency.png").is_file()
    assert plt.get_fignums() == []
