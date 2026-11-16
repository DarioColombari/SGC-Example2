"""Analyze steady-state electrical efficiency for natural gas/hydrogen blends."""

from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class AnalysisConfig:
    """Centralize physical and statistical criteria for reproducible analyses."""

    # Expressing thresholds in physical units keeps the analysis independent
    # from the sampling frequency of each experimental export.
    nominal_power_kw: float = 30.0
    load_step_percent: int = 10
    minimum_load_percent: int = 30
    rolling_window_seconds: float = 120.0
    minimum_plateau_seconds: float = 180.0
    maximum_setpoint_deviation_kw: float = 0.75
    maximum_power_std_kw: float = 0.20
    maximum_efficiency_std: float = 0.010
    maximum_power_slope_kw_per_minute: float = 0.08
    confidence_level: float = 0.95


class EngineEfficiencyAnalyzer:
    """Load experimental exports and isolate comparable steady-state samples."""

    REQUIRED_COLUMNS = {"Time", "TOTEM-W1", "V_in", "P_in", "n_el"}
    HYDROGEN_PATTERN = re.compile(r"auto_(\d+)-")

    def __init__(self, config: AnalysisConfig) -> None:
        self.config = config

    def analyze_directory(self, dataset_directory: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Analyze every blend and return both raw stationary points and statistics."""

        # Sorting by hydrogen content makes tables and figures deterministic,
        # regardless of the directory order returned by the operating system.
        files = sorted(dataset_directory.glob("*.csv"), key=self._hydrogen_percentage)
        if not files:
            raise FileNotFoundError(f"No CSV files found in {dataset_directory}")

        stationary_frames = [self._analyze_file(path) for path in files]
        stationary_data = pd.concat(stationary_frames, ignore_index=True)
        if stationary_data.empty:
            raise RuntimeError("No stationary operating points satisfy the configured criteria")
        return stationary_data, self._summarize(stationary_data)

    def _analyze_file(self, path: Path) -> pd.DataFrame:
        """Extract stationary operating points from one hydrogen-blend test."""

        hydrogen_percentage = self._hydrogen_percentage(path)
        data = self._read_export(path)
        sample_period_seconds = self._sample_period_seconds(data["Time"])
        electrical_power_kw = pd.to_numeric(data["TOTEM-W1"], errors="coerce")
        efficiency = self._complete_efficiency(data, electrical_power_kw)

        # Tests target discrete 10% load levels. Assigning each observation to
        # its nearest target allows the subsequent tolerance check to reject
        # transitions rather than treating them as separate operating points.
        load_percent = (
            (electrical_power_kw / self.config.nominal_power_kw * 100.0)
            / self.config.load_step_percent
        ).round().mul(self.config.load_step_percent).astype("Int64")

        window_points = self._odd_window_size(
            self.config.rolling_window_seconds, sample_period_seconds
        )
        minimum_points = math.ceil(
            self.config.minimum_plateau_seconds / sample_period_seconds
        ) + 1

        # A low standard deviation alone can accept a slow ramp. The local
        # regression slope therefore provides an independent drift criterion.
        power_slope = rolling_slope(
            electrical_power_kw.to_numpy(dtype=float),
            window_points,
            sample_period_seconds,
        )
        setpoint_kw = (
            load_percent.astype(float) * self.config.nominal_power_kw / 100.0
        )

        # A sample is only a candidate when power, efficiency, and drift are
        # simultaneously stable around a physically valid load setpoint.
        stationary_candidate = (
            load_percent.between(self.config.minimum_load_percent, 100)
            & electrical_power_kw.sub(setpoint_kw).abs().le(
                self.config.maximum_setpoint_deviation_kw
            )
            & efficiency.between(0.10, 0.60)
            & electrical_power_kw.rolling(
                window_points, center=True, min_periods=window_points
            ).std().le(self.config.maximum_power_std_kw)
            & efficiency.rolling(
                window_points, center=True, min_periods=window_points
            ).std().le(self.config.maximum_efficiency_std)
            & pd.Series(power_slope, index=data.index).abs().le(
                self.config.maximum_power_slope_kw_per_minute
            )
        )

        # Requiring one uninterrupted run prevents isolated stable-looking
        # samples inside transients from biasing the operating-point average.
        stationary = retain_long_runs(
            stationary_candidate, load_percent, minimum_points
        )

        return pd.DataFrame(
            {
                "hydrogen_percent": hydrogen_percentage,
                "load_percent": load_percent[stationary].astype(int),
                "electrical_power_kw": electrical_power_kw[stationary],
                "electrical_efficiency_percent": efficiency[stationary] * 100.0,
            }
        )

    def _read_export(self, path: Path) -> pd.DataFrame:
        """Read either locale-specific CSV representation used by the test bench."""

        lines = path.read_text(encoding="utf-8-sig").splitlines()
        if len(lines) < 4:
            raise ValueError(f"{path} does not contain the expected metadata and header")

        # Semicolon-separated exports use decimal commas, while comma-separated
        # exports use decimal points. The header unambiguously identifies both.
        separator = ";" if lines[3].count(";") > lines[3].count(",") else ","
        data = pd.read_csv(
            path,
            sep=separator,
            decimal="," if separator == ";" else ".",
            skiprows=3,
        )
        data.columns = data.columns.str.strip()
        data = data.loc[:, ~data.columns.str.startswith("Unnamed")]
        missing_columns = self.REQUIRED_COLUMNS.difference(data.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"{path} is missing required columns: {missing}")
        return data

    @staticmethod
    def _complete_efficiency(
        data: pd.DataFrame, electrical_power_kw: pd.Series
    ) -> pd.Series:
        """Fill invalid efficiency values using the blend-specific energy factor."""

        recorded_efficiency = pd.to_numeric(data["n_el"], errors="coerce")
        volume_flow = pd.to_numeric(data["V_in"], errors="coerce")
        input_power_kw = pd.to_numeric(data["P_in"], errors="coerce")
        calibration = (input_power_kw / volume_flow).where(
            input_power_kw.gt(0.0) & volume_flow.gt(0.0)
        )
        if calibration.count() < 3:
            raise ValueError("At least three valid P_in/V_in samples are required")

        # The median limits the influence of acquisition spikes. A file-specific
        # factor is necessary because the lower heating value changes with H2.
        energy_factor_kw_per_flow_unit = float(calibration.median())
        reconstructed = electrical_power_kw / (
            volume_flow * energy_factor_kw_per_flow_unit
        )

        # Recorded values remain the primary measurement; reconstruction is
        # restricted to missing or physically implausible calculated samples.
        return recorded_efficiency.where(
            recorded_efficiency.between(0.10, 0.60), reconstructed
        )

    def _summarize(self, stationary_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate mean efficiency and uncertainty for each blend/load pair."""

        grouped = stationary_data.groupby(
            ["hydrogen_percent", "load_percent"], sort=True
        )["electrical_efficiency_percent"]
        summary = grouped.agg(
            sample_count="size",
            mean_efficiency_percent="mean",
            standard_deviation_percent="std",
        ).reset_index()
        standard_error = grouped.apply(
            lambda values: stats.sem(values.to_numpy(), nan_policy="omit")
        ).reset_index(name="standard_error_percent")
        summary = summary.merge(
            standard_error, on=["hydrogen_percent", "load_percent"]
        )
        degrees_of_freedom = summary["sample_count"] - 1
        probability = (1.0 + self.config.confidence_level) / 2.0

        # Student's t interval accounts for the finite number of samples in
        # each plateau instead of assuming a known population variance.
        summary["confidence_interval_95_percent"] = (
            stats.t.ppf(probability, degrees_of_freedom)
            * summary["standard_error_percent"]
        )
        return summary

    @classmethod
    def _hydrogen_percentage(cls, path: Path) -> int:
        match = cls.HYDROGEN_PATTERN.search(path.name)
        if match is None:
            raise ValueError(f"Cannot extract hydrogen percentage from {path.name}")
        return int(match.group(1))

    @staticmethod
    def _sample_period_seconds(time_values: pd.Series) -> float:
        """Infer the representative sampling period, including midnight rollover."""

        elapsed = pd.to_timedelta(time_values.astype(str))
        seconds = elapsed.dt.total_seconds().to_numpy(dtype=float)
        differences = np.diff(seconds)

        # Some twelve-hour tests cross midnight, producing one negative delta.
        differences[differences < 0.0] += 24.0 * 60.0 * 60.0
        valid_differences = differences[
            np.isfinite(differences) & (differences > 0.0)
        ]
        if valid_differences.size == 0:
            raise ValueError("Cannot determine a positive sampling period")
        return float(np.median(valid_differences))

    @staticmethod
    def _odd_window_size(duration_seconds: float, sample_period_seconds: float) -> int:
        """Convert a physical duration to an odd, centered rolling-window size."""

        points = max(3, math.ceil(duration_seconds / sample_period_seconds) + 1)
        return points if points % 2 == 1 else points + 1


def rolling_slope(
    values: np.ndarray, window_points: int, sample_period_seconds: float
) -> np.ndarray:
    """Return centered least-squares slopes in kW/min for all complete windows."""

    slopes = np.full(values.size, np.nan)
    if values.size < window_points:
        return slopes

    # Vectorized windows avoid fitting thousands of independent SciPy models
    # while applying the same ordinary least-squares equation to every sample.
    windows = np.lib.stride_tricks.sliding_window_view(values, window_points)
    time_minutes = np.arange(window_points, dtype=float) * sample_period_seconds / 60.0
    centered_time = time_minutes - time_minutes.mean()
    centered_windows = windows - windows.mean(axis=1, keepdims=True)
    window_slopes = centered_windows @ centered_time / np.square(centered_time).sum()
    half_window = window_points // 2
    slopes[half_window : values.size - half_window] = window_slopes
    return slopes


def retain_long_runs(
    candidates: pd.Series, load_percent: pd.Series, minimum_points: int
) -> pd.Series:
    """Keep candidates belonging to a sufficiently long uninterrupted plateau."""

    # A change in either validity or load starts a new run, ensuring adjacent
    # plateaus at different setpoints can never be merged.
    run_ids = (
        candidates.ne(candidates.shift()) | load_percent.ne(load_percent.shift())
    ).cumsum()
    run_sizes = candidates.groupby(run_ids).transform("sum")
    return candidates & run_sizes.ge(minimum_points)


def create_figure(summary: pd.DataFrame, output_path: Path) -> None:
    """Create a publication-oriented multi-panel SVG with shared axes."""

    hydrogen_levels = sorted(summary["hydrogen_percent"].unique())

    # Viridis remains distinguishable in grayscale and for common forms of
    # color-vision deficiency, which improves publication accessibility.
    colors = plt.colormaps["viridis"](np.linspace(0.08, 0.92, len(hydrogen_levels)))
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 9,
            "axes.linewidth": 0.8,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.top": True,
            "ytick.right": True,
            "svg.fonttype": "none",
        }
    )

    # A fixed 2x4 grid accommodates all seven measured blends while preserving
    # equal panel dimensions and direct visual comparison through shared axes.
    figure, axes = plt.subplots(2, 4, figsize=(11.0, 5.8), sharex=True, sharey=True)
    visible_axes = axes.flat[: len(hydrogen_levels)]
    for axis, hydrogen, color in zip(
        visible_axes, hydrogen_levels, colors, strict=True
    ):
        blend = summary.loc[summary["hydrogen_percent"].eq(hydrogen)]
        axis.errorbar(
            blend["load_percent"],
            blend["mean_efficiency_percent"],
            yerr=blend["confidence_interval_95_percent"],
            color=color,
            marker="o",
            markersize=5.0,
            linewidth=1.4,
            capsize=3.0,
            capthick=1.0,
        )
        axis.set_title(rf"$x_{{\mathrm{{H_2}}}} = {hydrogen}\%$")
        axis.set_xticks(np.arange(30, 101, 10))
        axis.grid(True, color="0.88", linewidth=0.6)
        axis.set_axisbelow(True)

    for axis in axes.flat[len(hydrogen_levels) :]:
        axis.set_visible(False)
    figure.supxlabel(r"Engine load, $P_{\mathrm{el}}/P_{\mathrm{nom}}$ (\%)")
    figure.supylabel(r"Electrical efficiency, $\eta_{\mathrm{el}}$ (\%)")
    figure.suptitle(
        r"Steady-state electrical efficiency of natural gas--hydrogen blends",
        fontsize=12,
        y=0.99,
    )
    figure.text(
        0.5,
        0.015,
        r"Markers show mean values; error bars denote 95\% confidence intervals.",
        ha="center",
        fontsize=8,
    )
    figure.tight_layout(rect=(0.025, 0.05, 1.0, 0.96))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, format="svg", bbox_inches="tight")
    plt.close(figure)


def parse_arguments() -> argparse.Namespace:
    """Parse input and output locations while keeping reproducible defaults."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset-dir", type=Path, default=Path("dataset"), help="Input CSV directory"
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("results"), help="Output directory"
    )
    return parser.parse_args()


def main() -> None:
    """Run the complete extraction, aggregation, and plotting workflow."""

    arguments = parse_arguments()
    analyzer = EngineEfficiencyAnalyzer(AnalysisConfig())
    stationary_data, summary = analyzer.analyze_directory(arguments.dataset_dir)
    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = arguments.output_dir / "electrical_efficiency_summary.csv"
    figure_path = arguments.output_dir / "electrical_efficiency.svg"
    summary.to_csv(summary_path, index=False, float_format="%.6f")
    create_figure(summary, figure_path)
    print(
        f"Analyzed {len(stationary_data):,} stationary samples; "
        f"wrote {summary_path} and {figure_path}."
    )


if __name__ == "__main__":
    main()
