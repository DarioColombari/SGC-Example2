import numpy as np
import pandas as pd
import pytest

from src.aggregation import aggregate_efficiency
from src.data_loading import load_dataset, load_measurement_file
from src.stationary import identify_stationary_periods


HEADER = "Time;WT01;n_el\n"


def _write_csv(path, rows, *, metadata=True):
    prefix = "Start Time: | 23:59:50\n" if metadata else ""
    path.write_text(prefix + HEADER + "\n".join(rows) + "\n", encoding="utf-8")


def _stationary_rows(power, n_el_values):
    return [
        f"{elapsed // 3600:02d}:{(elapsed % 3600) // 60:02d}:{elapsed % 60:02d};"
        f"{power:.1f};{n_el_values[row]:.3f}"
        for row, elapsed in enumerate(range(0, len(n_el_values) * 10, 10))
    ]


def test_loads_metadata_decimal_values_and_midnight_rollover(tmp_path):
    path = tmp_path / "prova_auto_12_test.csv"
    _write_csv(
        path,
        [
            "23:59:50;15,5;0,210",
            "00:00:00;15,6;0,220",
            "00:00:10;15,4;0,230",
        ],
    )

    frame = load_measurement_file(path)

    assert frame["h2_percent"].unique().tolist() == [12.0]
    assert frame["WT01"].tolist() == [15.5, 15.6, 15.4]
    assert frame["n_el"].tolist() == [0.21, 0.22, 0.23]
    assert frame["elapsed_seconds"].tolist() == [0.0, 10.0, 20.0]


def test_drops_missing_and_infinite_measurements(tmp_path):
    path = tmp_path / "prova_auto_0_test.csv"
    _write_csv(
        path,
        [
            "00:00:00;15,0;0,200",
            "00:00:10;15,0;Inf",
            "00:00:20;Inf;0,300",
            "00:00:30;15,0;",
            "00:00:40;15,0;-Inf",
        ],
    )

    frame = load_measurement_file(path)

    assert len(frame) == 1
    assert frame.iloc[0]["n_el"] == pytest.approx(0.2)


def test_rejects_filename_without_hydrogen_percentage(tmp_path):
    path = tmp_path / "prova_auto_test.csv"
    _write_csv(path, ["00:00:00;15,0;0,2"])

    with pytest.raises(ValueError, match="Hydrogen percentage"):
        load_measurement_file(path)


def test_identifies_stationary_period_and_aggregates_observed_combinations(tmp_path):
    first_values = np.full(181, 0.2)
    first_values[0] = 0.1
    second_values = np.full(181, 0.4)
    first = tmp_path / "prova_auto_0_load.csv"
    second = tmp_path / "prova_auto_10_load.csv"
    _write_csv(first, _stationary_rows(15.0, first_values))
    _write_csv(second, _stationary_rows(18.0, second_values))

    measurements = load_dataset(tmp_path)
    stationary = identify_stationary_periods(measurements)
    result = aggregate_efficiency(stationary)

    assert len(stationary) == 362
    assert stationary["load_percent"].unique().tolist() == [50.0, 60.0]
    assert result[["h2_percent", "load_percent"]].values.tolist() == [
        [0.0, 50.0],
        [10.0, 60.0],
    ]
    assert result["sample_count"].tolist() == [181, 181]
    assert result.loc[0, "n_el_mean"] == pytest.approx((0.1 + 180 * 0.2) / 181)
    assert result.loc[0, "n_el_std"] == pytest.approx(
        pd.Series(first_values).std()
    )


def test_ignores_series_shorter_than_documented_duration(tmp_path):
    path = tmp_path / "prova_auto_20_short.csv"
    _write_csv(path, _stationary_rows(15.0, np.full(31, 0.3)))

    measurements = load_dataset(tmp_path)

    assert identify_stationary_periods(measurements).empty


def test_preserves_rows_with_nonuniform_trailing_delimiters(tmp_path):
    path = tmp_path / "prova_auto_5_trailing.csv"
    path.write_text(
        "metadata\n"
        "Time;WT01;n_el\n"
        "00:00:00;15,0;0,2;\n"
        "00:00:10;15,0;0,3\n",
        encoding="utf-8",
    )

    frame = load_measurement_file(path)

    assert len(frame) == 2
    assert frame["n_el"].tolist() == [0.2, 0.3]
