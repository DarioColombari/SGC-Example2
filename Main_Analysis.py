"""Entry point configurabile per eseguire la pipeline in debug mode."""

from argparse import Namespace
from pathlib import Path

import pandas as pd

from analysis.io import load_dataset
from analysis.plotting import plot_efficiency_by_load
from analysis.statistics import aggregate_efficiency
from analysis.stationary import find_stationary_periods


args = Namespace(
    dataset_dir=Path(r"experimentalResults"),  # Inserire qui il percorso del dataset.
    output_dir=Path("results"),
)


def main() -> None:
    csv_paths = sorted(args.dataset_dir.glob("*.csv"))
    if not csv_paths:
        raise FileNotFoundError(f"Nessun file CSV in {args.dataset_dir}")

    stationary_frames = []
    for csv_path in csv_paths:
        data = load_dataset(csv_path)
        stationary = find_stationary_periods(data)
        stationary_frames.append(stationary)
        print(
            f"{csv_path.name}: {len(stationary)} campioni stazionari "
            f"su {len(data)}"
        )

    stationary = pd.concat(stationary_frames, ignore_index=True)
    summary = aggregate_efficiency(stationary)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "efficiency_summary.csv"
    summary.to_csv(summary_path, index=False)

    generated_plots = []
    for h2_percent, h2_summary in summary.groupby("h2_percent"):
        h2_label = f"{h2_percent:g}".replace(".", "_")
        h2_output_dir = args.output_dir / f"h2_{h2_label}"
        h2_summary_path = h2_output_dir / "efficiency_summary.csv"
        plot_path = h2_output_dir / "efficiency_by_load.png"

        h2_output_dir.mkdir(parents=True, exist_ok=True)
        h2_summary.to_csv(h2_summary_path, index=False)
        plot_efficiency_by_load(h2_summary, plot_path)
        generated_plots.append(plot_path)

    print(f"Campioni stazionari totali: {len(stationary)}")
    print(f"Riepilogo: {summary_path}")
    for plot_path in generated_plots:
        print(f"Grafico: {plot_path}")


if __name__ == "__main__":
    main()
