import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from PIL import Image

from src import cli, plotting


def _aggregated_frame():
    return pd.DataFrame(
        {
            "h2_percent": [0.0, 10.0, 0.0, 10.0],
            "load_percent": [50.0, 50.0, 60.0, 60.0],
            "n_el_mean": [0.20, 0.22, 0.25, 0.27],
            "n_el_std": [0.01, 0.02, 0.015, 0.025],
            "sample_count": [3, 3, 3, 3],
        }
    )


def _write_stationary_csv(path, h2_percent, efficiency):
    rows = [
        f"{seconds // 3600:02d}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d};"
        f"15,0;{efficiency:.3f}"
        for seconds in range(0, 1810, 10)
    ]
    path.write_text(
        "Time;WT01;n_el\n" + "\n".join(rows) + "\n",
        encoding="utf-8",
    )


def test_plot_uses_aggregated_values_and_closes_figure(tmp_path, monkeypatch):
    aggregated = _aggregated_frame()
    output_path = tmp_path / "nested" / "summary.png"
    captured_figures = []
    captured_errors = []
    original_close = plotting.plt.close
    original_errorbar = plotting.plt.Axes.errorbar

    def close(figure=None):
        captured_figures.append(figure)
        original_close(figure)

    def errorbar(axis, *args, **kwargs):
        captured_errors.append(np.asarray(kwargs["yerr"]))
        return original_errorbar(axis, *args, **kwargs)

    def unexpected_statistics(*args, **kwargs):
        raise AssertionError("plotting must not recalculate statistics")

    monkeypatch.setattr(plotting.plt, "close", close)
    monkeypatch.setattr(plotting.plt.Axes, "errorbar", errorbar)
    monkeypatch.setattr(pd.Series, "mean", unexpected_statistics)
    monkeypatch.setattr(pd.Series, "std", unexpected_statistics)

    result = plotting.plot_efficiency_summary(aggregated, output_path)

    assert result == output_path
    assert output_path.is_file()
    assert output_path.stat().st_size > 0
    assert len(captured_figures) == 1
    assert plt.get_fignums() == []
    assert np.array_equal(captured_errors[0], [0.01, 0.02])
    assert np.array_equal(captured_errors[1], [0.015, 0.025])

    figure = captured_figures[0]
    axis = figure.axes[0]
    assert axis.get_xlabel() == "Hydrogen in fuel mixture H₂ (%)"
    assert axis.get_ylabel() == "Electrical efficiency n_el (-)"
    assert axis.get_title() == "Electrical efficiency by hydrogen percentage and load"
    assert {text.get_text() for text in axis.get_legend().get_texts()} == {
        "50% load",
        "60% load",
    }


def test_plot_saves_valid_png_at_300_dpi_and_uses_agg(tmp_path):
    output_path = plotting.plot_efficiency_summary(
        _aggregated_frame(),
        tmp_path / "summary.png",
    )

    assert matplotlib.get_backend().lower() == "agg"
    with Image.open(output_path) as image:
        assert image.format == "PNG"
        assert image.size[0] > 0
        assert image.size[1] > 0
        assert image.info["dpi"][0] == pytest.approx(300, abs=1)


def test_plot_handles_empty_aggregate_without_inventing_data(tmp_path, monkeypatch):
    empty = _aggregated_frame().iloc[0:0]
    captured_figures = []
    original_close = plotting.plt.close

    def close(figure=None):
        captured_figures.append(figure)
        original_close(figure)

    monkeypatch.setattr(plotting.plt, "close", close)
    output_path = plotting.plot_efficiency_summary(empty, tmp_path / "empty.png")

    assert output_path.is_file()
    assert captured_figures[0].axes[0].texts[0].get_text() == (
        "No valid stationary periods found"
    )


def test_plot_rejects_missing_aggregated_columns(tmp_path):
    with pytest.raises(ValueError, match="Missing plotting columns"):
        plotting.plot_efficiency_summary(
            pd.DataFrame({"h2_percent": [0.0]}),
            tmp_path / "summary.png",
        )


def test_cli_runs_end_to_end_with_synthetic_dataset(tmp_path):
    dataset_dir = tmp_path / "dataset"
    output_dir = tmp_path / "requested-output"
    dataset_dir.mkdir()
    _write_stationary_csv(dataset_dir / "prova_auto_0_load.csv", 0, 0.2)
    _write_stationary_csv(dataset_dir / "prova_auto_10_load.csv", 10, 0.3)

    exit_code = cli.main(
        ["--dataset-dir", str(dataset_dir), "--output-dir", str(output_dir)]
    )

    output_path = output_dir / "efficiency_summary.png"
    assert exit_code == 0
    assert output_path.is_file()
    with Image.open(output_path) as image:
        assert image.format == "PNG"


def test_cli_rejects_missing_option_value():
    with pytest.raises(SystemExit) as error:
        cli.main(["--dataset-dir"])

    assert error.value.code == 2


def test_cli_rejects_unknown_argument():
    with pytest.raises(SystemExit) as error:
        cli.main(["--not-a-cli-option"])

    assert error.value.code == 2
