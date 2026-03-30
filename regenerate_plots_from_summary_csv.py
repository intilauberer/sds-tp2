from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt

SCENARIO_ORDER = ["none", "fixed", "circular"]
SCENARIO_COLORS = {"none": "#1f77b4", "fixed": "#2ca02c", "circular": "#d62728"}

FIG_TITLE_SIZE = 20
AXIS_LABEL_SIZE = 18
TICK_LABEL_SIZE = 16
LEGEND_SIZE = 14


def apply_axes_style(ax: plt.Axes) -> None:
    ax.tick_params(axis="both", which="major", labelsize=TICK_LABEL_SIZE)


def load_summary(csv_path: Path) -> List[Dict[str, float | str]]:
    rows: List[Dict[str, float | str]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        needed = {"scenario", "eta", "va_mean", "va_sem"}
        missing = needed - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing columns in {csv_path}: {sorted(missing)}")
        for r in reader:
            rows.append(
                {
                    "scenario": str(r["scenario"]),
                    "eta": float(r["eta"]),
                    "va_mean": float(r["va_mean"]),
                    "va_sem": float(r["va_sem"]),
                }
            )
    return rows


def select_sorted(rows: List[Dict[str, float | str]], scenario: str) -> List[Dict[str, float | str]]:
    out = [r for r in rows if r["scenario"] == scenario]
    out.sort(key=lambda r: float(r["eta"]))
    return out


def plot_c_and_d_from_summary(rows: List[Dict[str, float | str]], c_dir: Path, d_dir: Path) -> None:
    c_dir.mkdir(parents=True, exist_ok=True)
    d_dir.mkdir(parents=True, exist_ok=True)

    # Per scenario (files used by presentation)
    for scenario in SCENARIO_ORDER:
        dfx = select_sorted(rows, scenario)
        x = [float(r["eta"]) for r in dfx]
        y = [float(r["va_mean"]) for r in dfx]
        yerr = [float(r["va_sem"]) for r in dfx]
        fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
        ax.errorbar(
            x,
            y,
            yerr=yerr,
            marker="o",
            lw=1.8,
            capsize=3,
            color=SCENARIO_COLORS[scenario],
        )
        ax.set_xlabel("Ruido angular η", fontsize=AXIS_LABEL_SIZE)
        ax.set_ylabel("Polarización estacionaria <va>", fontsize=AXIS_LABEL_SIZE)
        ax.grid(alpha=0.3)
        apply_axes_style(ax)
        fig.savefig(c_dir / f"c_va_vs_eta_{scenario}.png", dpi=220)
        plt.close(fig)

    # Combined d
    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    for scenario in SCENARIO_ORDER:
        dfx = select_sorted(rows, scenario)
        x = [float(r["eta"]) for r in dfx]
        y = [float(r["va_mean"]) for r in dfx]
        yerr = [float(r["va_sem"]) for r in dfx]
        ax.errorbar(
            x,
            y,
            yerr=yerr,
            marker="o",
            lw=1.8,
            capsize=3,
            label=scenario,
            color=SCENARIO_COLORS[scenario],
        )
    ax.set_xlabel("Ruido angular η", fontsize=AXIS_LABEL_SIZE)
    ax.set_ylabel("Polarización estacionaria <va>", fontsize=AXIS_LABEL_SIZE)
    ax.grid(alpha=0.3)
    apply_axes_style(ax)
    ax.legend(fontsize=LEGEND_SIZE)
    fig.savefig(d_dir / "d_comparacion_escenarios.png", dpi=220)
    plt.close(fig)


def plot_e_density_d(rows: List[Dict[str, float | str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    for scenario in SCENARIO_ORDER:
        dfx = select_sorted(rows, scenario)
        x = [float(r["eta"]) for r in dfx]
        y = [float(r["va_mean"]) for r in dfx]
        yerr = [float(r["va_sem"]) for r in dfx]
        ax.errorbar(
            x,
            y,
            yerr=yerr,
            marker="o",
            lw=1.8,
            capsize=3,
            label=scenario,
            color=SCENARIO_COLORS[scenario],
        )
    ax.set_xlabel("Ruido angular η", fontsize=AXIS_LABEL_SIZE)
    ax.set_ylabel("Polarización estacionaria <va>", fontsize=AXIS_LABEL_SIZE)
    ax.grid(alpha=0.3)
    apply_axes_style(ax)
    ax.legend(fontsize=LEGEND_SIZE)
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate c/d/e plots from existing summary CSV files (no simulation rerun).")
    parser.add_argument("--base-summary", default="b/va_vs_eta_summary.csv")
    parser.add_argument("--c-dir", default="c")
    parser.add_argument("--d-dir", default="d")
    parser.add_argument("--rho2-summary", default="e/rho_2/va_vs_eta_summary.csv")
    parser.add_argument("--rho8-summary", default="e/rho_8/va_vs_eta_summary.csv")
    parser.add_argument(
        "--rerun-b",
        action="store_true",
        help="Also regenerate b temporal plots by rerunning tp2_bcd.py (needed because b cannot be rebuilt from summary CSV).",
    )
    parser.add_argument("--python-bin", default="python3", help="Python executable for optional rerun command")
    parser.add_argument("--b-out-dir", default="b", help="Destination dir for temporal plots b when --rerun-b is used")
    parser.add_argument("--L", type=float, default=10.0)
    parser.add_argument("--rho", type=float, default=4.0)
    parser.add_argument("--r0", type=float, default=1.0)
    parser.add_argument("--v0", type=float, default=0.03)
    parser.add_argument("--tmax", type=int, default=1000)
    parser.add_argument("--runs-per-eta", type=int, default=2)
    parser.add_argument("--eta-min", type=float, default=0.0)
    parser.add_argument("--eta-max", type=float, default=3.0)
    parser.add_argument("--eta-step", type=float, default=0.6)
    parser.add_argument("--stationary-start", type=int, default=175)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()

    base_df = load_summary(Path(args.base_summary))
    plot_c_and_d_from_summary(base_df, Path(args.c_dir), Path(args.d_dir))

    rho2_df = load_summary(Path(args.rho2_summary))
    plot_e_density_d(rho2_df, Path("e/rho_2/d_comparacion_escenarios_rho_2.png"))

    rho8_df = load_summary(Path(args.rho8_summary))
    plot_e_density_d(rho8_df, Path("e/rho_8/d_comparacion_escenarios_rho_8.png"))

    if args.rerun_b:
        temp_out = Path("output/tp2_bcd_pub")
        cmd = [
            args.python_bin,
            "tp2_bcd.py",
            "--out-dir",
            str(temp_out),
            "--L",
            str(args.L),
            "--rho",
            str(args.rho),
            "--r0",
            str(args.r0),
            "--v0",
            str(args.v0),
            "--tmax",
            str(args.tmax),
            "--runs-per-eta",
            str(args.runs_per_eta),
            "--eta-min",
            str(args.eta_min),
            "--eta-max",
            str(args.eta_max),
            "--eta-step",
            str(args.eta_step),
            "--stationary-start",
            str(args.stationary_start),
            "--workers",
            str(args.workers),
        ]
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=True)

        b_dir = Path(args.b_out_dir)
        b_dir.mkdir(parents=True, exist_ok=True)
        for name in [
            "b_evolucion_temporal_va_none.png",
            "b_evolucion_temporal_va_fixed.png",
            "b_evolucion_temporal_va_circular.png",
            "b_evolucion_temporal_comparacion_eta_0.00.png",
            "b_evolucion_temporal_comparacion_eta_1.80.png",
            "b_evolucion_temporal_comparacion_eta_3.00.png",
            "va_vs_eta_summary.csv",
            "va_vs_eta_summary.txt",
        ]:
            src = temp_out / name
            if src.exists():
                (b_dir / name).write_bytes(src.read_bytes())

    print("Done: regenerated c/, d/, and e/rho_{2,8}/ comparative plots from CSV summaries.")
    if not args.rerun_b:
        print("Note: b temporal plots cannot be regenerated from summary CSV. Use --rerun-b to regenerate b by rerunning tp2_bcd.")


if __name__ == "__main__":
    main()
