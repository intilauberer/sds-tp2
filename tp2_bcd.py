"""TP2 helper for points b, c, d (Vicsek + leader scenarios).

Generates:
- Temporal evolution plots (point b)
- va vs eta with error bars per scenario (point c)
- Combined comparison across scenarios (point d)
- CSV/TXT summary tables
"""

from __future__ import annotations

import argparse
import csv
import math
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

from vicsek import VicsekSimulation


SCENARIOS = ("none", "fixed", "circular")


@dataclass
class RunConfig:
    L: float
    rho: float
    r0: float
    v0: float
    tmax: int
    eta_values: List[float]
    runs_per_eta: int
    stationary_start: int
    fixed_leader_angle: float
    circle_radius: float
    seed_base: int
    workers: int


def get_stationary_start(config: RunConfig) -> int:
    return min(max(config.stationary_start, 0), config.tmax)


def get_representative_etas(eta_values: List[float]) -> List[float]:
    if len(eta_values) < 3:
        return list(eta_values)
    return [eta_values[0], eta_values[len(eta_values) // 2], eta_values[-1]]


def stationary_mean_and_std(order_runs: np.ndarray, stationary_start: int) -> Tuple[float, float]:
    stationary_values = order_runs[:, stationary_start:].reshape(-1)
    mean = float(np.mean(stationary_values))
    if stationary_values.size > 1:
        std = float(np.std(stationary_values, ddof=1))
    else:
        std = 0.0
    return mean, std


def simulate_order_series(config: RunConfig, scenario: str, eta: float, seed: int) -> np.ndarray:
    n_particles = int(round(config.rho * config.L * config.L))
    sim = VicsekSimulation(
        n_particles=n_particles,
        box_size=config.L,
        density=config.rho,
        interaction_radius=config.r0,
        speed=config.v0,
        noise=eta,
        dt=1.0,
        seed=seed,
        leader_mode=scenario,
        leader_id=0,
        leader_direction=(config.fixed_leader_angle if scenario == "fixed" else None),
        leader_circle_center=(config.L / 2.0, config.L / 2.0),
        leader_circle_radius=config.circle_radius,
    )

    orders = np.zeros(config.tmax + 1, dtype=float)
    for t in range(config.tmax + 1):
        orders[t] = sim.order_parameter()
        sim.step()
    return orders


def _simulate_order_task(config: RunConfig, scenario: str, eta: float, seed: int) -> np.ndarray:
    return simulate_order_series(config, scenario, eta, seed)


def run_sweep(config: RunConfig) -> Tuple[Dict[str, Dict[float, np.ndarray]], Dict[str, Dict[float, np.ndarray]]]:
    series: Dict[str, Dict[float, np.ndarray]] = {s: {} for s in SCENARIOS}
    scalar_runs: Dict[str, Dict[float, np.ndarray]] = {s: {} for s in SCENARIOS}
    t_stationary_start = get_stationary_start(config)

    task_count = len(SCENARIOS) * len(config.eta_values) * config.runs_per_eta
    workers = max(1, config.workers)
    if workers > 1:
        print(f"[parallel] workers={workers}, tasks={task_count}", flush=True)
        per_run_by_key: Dict[Tuple[str, float], List[np.ndarray]] = {}
        for scenario in SCENARIOS:
            for eta in config.eta_values:
                per_run_by_key[(scenario, eta)] = [None] * config.runs_per_eta  # type: ignore[list-item]

        future_to_task = {}
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for scenario in SCENARIOS:
                for eta_idx, eta in enumerate(config.eta_values):
                    for run_i in range(config.runs_per_eta):
                        print(
                            f"[run] scenario={scenario:8s} eta={eta:.3f} "
                            f"run={run_i + 1}/{config.runs_per_eta}",
                            flush=True,
                        )
                        seed = config.seed_base + 10_000 * eta_idx + 100 * run_i + SCENARIOS.index(scenario)
                        fut = executor.submit(_simulate_order_task, config, scenario, eta, seed)
                        future_to_task[fut] = (scenario, eta, run_i)

            completed = 0
            for fut in as_completed(future_to_task):
                scenario, eta, run_i = future_to_task[fut]
                order_t = fut.result()
                per_run_by_key[(scenario, eta)][run_i] = order_t
                completed += 1
                print(
                    f"[task-done] {completed}/{task_count} "
                    f"scenario={scenario:8s} eta={eta:.3f} run={run_i + 1}/{config.runs_per_eta}",
                    flush=True,
                )

        for scenario in SCENARIOS:
            for eta in config.eta_values:
                per_run_series = per_run_by_key[(scenario, eta)]
                series[scenario][eta] = np.vstack(per_run_series)
                per_run_scalar = [float(np.mean(order_t[t_stationary_start:])) for order_t in per_run_series]
                scalar_runs[scenario][eta] = np.array(per_run_scalar, dtype=float)
                if len(per_run_scalar) > 1:
                    sem = np.std(per_run_scalar, ddof=1) / math.sqrt(len(per_run_scalar))
                else:
                    sem = 0.0
                print(
                    f"[done] scenario={scenario:8s} eta={eta:.3f} "
                    f"mean_va={np.mean(per_run_scalar):.4f} sem={sem:.4f}",
                    flush=True,
                )
    else:
        for scenario in SCENARIOS:
            for eta_idx, eta in enumerate(config.eta_values):
                per_run_series: List[np.ndarray] = []
                per_run_scalar: List[float] = []
                for run_i in range(config.runs_per_eta):
                    print(
                        f"[run] scenario={scenario:8s} eta={eta:.3f} "
                        f"run={run_i + 1}/{config.runs_per_eta}",
                        flush=True,
                    )
                    seed = config.seed_base + 10_000 * eta_idx + 100 * run_i + SCENARIOS.index(scenario)
                    order_t = simulate_order_series(config, scenario, eta, seed)
                    per_run_series.append(order_t)
                    per_run_scalar.append(float(np.mean(order_t[t_stationary_start:])))

                series[scenario][eta] = np.vstack(per_run_series)
                scalar_runs[scenario][eta] = np.array(per_run_scalar, dtype=float)
                if len(per_run_scalar) > 1:
                    sem = np.std(per_run_scalar, ddof=1) / math.sqrt(len(per_run_scalar))
                else:
                    sem = 0.0
                print(
                    f"[done] scenario={scenario:8s} eta={eta:.3f} "
                    f"mean_va={np.mean(per_run_scalar):.4f} sem={sem:.4f}",
                    flush=True,
                )
    return series, scalar_runs


def write_scalar_tables(
    out_dir: Path,
    config: RunConfig,
    scalar_runs: Dict[str, Dict[float, np.ndarray]],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "va_vs_eta_summary.csv"
    txt_path = out_dir / "va_vs_eta_summary.txt"

    rows = []
    for scenario in SCENARIOS:
        for eta in config.eta_values:
            vals = scalar_runs[scenario][eta]
            mean = float(np.mean(vals))
            std = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
            sem = std / math.sqrt(len(vals)) if len(vals) > 1 else 0.0
            rows.append(
                {
                    "scenario": scenario,
                    "eta": eta,
                    "n_runs": len(vals),
                    "va_mean": mean,
                    "va_std": std,
                    "va_sem": sem,
                }
            )

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    with txt_path.open("w", encoding="utf-8") as f:
        f.write("Resumen TP2 - punto c/d: va vs eta\n")
        f.write(f"Criterio estacionario: t >= {get_stationary_start(config)}\n")
        f.write(
            f"Parametros: L={config.L}, rho={config.rho}, r0={config.r0}, v0={config.v0}, "
            f"tmax={config.tmax}, runs/eta={config.runs_per_eta}\n\n"
        )
        f.write("scenario, eta, n_runs, va_mean, va_std, va_sem\n")
        for r in rows:
            f.write(
                f"{r['scenario']}, {r['eta']:.6f}, {r['n_runs']}, "
                f"{r['va_mean']:.6f}, {r['va_std']:.6f}, {r['va_sem']:.6f}\n"
            )


def plot_temporal_evolution(
    out_dir: Path,
    config: RunConfig,
    series: Dict[str, Dict[float, np.ndarray]],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    chosen_etas = get_representative_etas(config.eta_values)

    t = np.arange(config.tmax + 1)
    t_stationary_start = get_stationary_start(config)
    cmap = plt.cm.viridis

    for scenario in SCENARIOS:
        fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
        for i, eta in enumerate(chosen_etas):
            mean_series = np.mean(series[scenario][eta], axis=0)
            ax.plot(t, mean_series, lw=1.5, color=cmap(i / max(1, len(chosen_etas) - 1)), label=fr"$\eta={eta:.2f}$")
        ax.axvspan(t_stationary_start, config.tmax, color="gray", alpha=0.15, label="ventana estacionaria")
        ax.set_title(f"Escenario: {scenario}")
        ax.set_xlabel("t")
        ax.set_ylabel(r"Polarizacion $v_a(t)$")
        ax.grid(alpha=0.3)
        ax.legend()
        fig.savefig(out_dir / f"b_evolucion_temporal_va_{scenario}.png", dpi=220)
        plt.close(fig)


def plot_temporal_comparison_by_eta(
    out_dir: Path,
    config: RunConfig,
    series: Dict[str, Dict[float, np.ndarray]],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    chosen_etas = get_representative_etas(config.eta_values)
    t = np.arange(config.tmax + 1)
    t_stationary_start = get_stationary_start(config)
    scenario_colors = {"none": "#1f77b4", "fixed": "#2ca02c", "circular": "#d62728"}

    for eta in chosen_etas:
        fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
        for scenario in SCENARIOS:
            mean_series = np.mean(series[scenario][eta], axis=0)
            ax.plot(t, mean_series, lw=1.7, color=scenario_colors[scenario], label=scenario)
        ax.axvspan(t_stationary_start, config.tmax, color="gray", alpha=0.15, label="ventana estacionaria")
        ax.set_title(fr"Comparacion por escenario ($\eta={eta:.2f}$)")
        ax.set_xlabel("t")
        ax.set_ylabel(r"Polarizacion $v_a(t)$")
        ax.grid(alpha=0.3)
        ax.legend()
        fig.savefig(out_dir / f"b_evolucion_temporal_comparacion_eta_{eta:.2f}.png", dpi=220)
        plt.close(fig)


def plot_curves_c_and_d(
    out_dir: Path,
    config: RunConfig,
    series: Dict[str, Dict[float, np.ndarray]],
    scalar_runs: Dict[str, Dict[float, np.ndarray]],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    eta = np.array(config.eta_values, dtype=float)
    t_stationary_start = get_stationary_start(config)
    scenario_colors = {"none": "#1f77b4", "fixed": "#2ca02c", "circular": "#d62728"}

    # Point c: one figure with one panel per scenario
    fig_c, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True, constrained_layout=True)
    for ax, scenario in zip(axes, SCENARIOS):
        means = []
        sems = []
        for e in eta:
            means.append(float(np.mean(scalar_runs[scenario][float(e)])))
            _, std_stationary = stationary_mean_and_std(series[scenario][float(e)], t_stationary_start)
            sems.append(std_stationary)
        means = np.array(means)
        sems = np.array(sems)
        ax.errorbar(
            eta,
            means,
            yerr=sems,
            marker="o",
            lw=1.6,
            capsize=3,
            color=scenario_colors[scenario],
        )
        ax.set_title(f"Escenario: {scenario}")
        ax.set_xlabel(r"Ruido $\eta$")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel(r"$\langle v_a \rangle$ estacionario")
    fig_c.savefig(out_dir / "c_va_vs_eta_por_escenario.png", dpi=220)
    plt.close(fig_c)

    # Point d: comparison in one panel
    fig_d, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    for scenario in SCENARIOS:
        means = []
        sems = []
        for e in eta:
            means.append(float(np.mean(scalar_runs[scenario][float(e)])))
            _, std_stationary = stationary_mean_and_std(series[scenario][float(e)], t_stationary_start)
            sems.append(std_stationary)
        means = np.array(means)
        sems = np.array(sems)
        ax.errorbar(
            eta,
            means,
            yerr=sems,
            marker="o",
            lw=1.8,
            capsize=3,
            label=scenario,
            color=scenario_colors[scenario],
        )
    ax.set_xlabel(r"Ruido $\eta$")
    ax.set_ylabel(r"$\langle v_a \rangle$ estacionario")
    ax.set_title("Comparacion de escenarios (punto d)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig_d.savefig(out_dir / "d_comparacion_escenarios.png", dpi=220)
    plt.close(fig_d)


def parse_eta_values(eta_min: float, eta_max: float, eta_step: float) -> List[float]:
    if eta_step <= 0:
        raise ValueError("--eta-step must be > 0")
    values = []
    cur = eta_min
    while cur <= eta_max + 1e-12:
        values.append(round(cur, 10))
        cur += eta_step
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate TP2 plots for points b/c/d.")
    parser.add_argument("--out-dir", default="output/tp2_bcd", help="Output directory for figures/tables")
    parser.add_argument("--L", type=float, default=10.0)
    parser.add_argument("--rho", type=float, default=4.0)
    parser.add_argument("--r0", type=float, default=1.0)
    parser.add_argument("--v0", type=float, default=0.03)
    parser.add_argument("--tmax", type=int, default=1000, help="Total time steps per run")
    parser.add_argument("--runs-per-eta", type=int, default=2, help="Independent runs for each eta and scenario")
    parser.add_argument("--eta-min", type=float, default=0.0)
    parser.add_argument("--eta-max", type=float, default=3.0)
    parser.add_argument("--eta-step", type=float, default=0.6)
    parser.add_argument("--stationary-start", type=int, default=750, help="Start time for stationary window (t >= stationary-start)")
    parser.add_argument("--fixed-leader-angle", type=float, default=math.pi / 4.0)
    parser.add_argument("--circle-radius", type=float, default=5.0)
    parser.add_argument("--seed-base", type=int, default=12345)
    parser.add_argument("--workers", type=int, default=1, help="Parallel worker processes (1 = sequential)")
    args = parser.parse_args()

    eta_values = parse_eta_values(args.eta_min, args.eta_max, args.eta_step)
    config = RunConfig(
        L=args.L,
        rho=args.rho,
        r0=args.r0,
        v0=args.v0,
        tmax=args.tmax,
        eta_values=eta_values,
        runs_per_eta=args.runs_per_eta,
        stationary_start=args.stationary_start,
        fixed_leader_angle=args.fixed_leader_angle,
        circle_radius=args.circle_radius,
        seed_base=args.seed_base,
        workers=args.workers,
    )
    print(
        f"Running sweep: scenarios={len(SCENARIOS)}, etas={len(config.eta_values)}, "
        f"runs/eta={config.runs_per_eta}, tmax={config.tmax}",
        flush=True,
    )
    series, scalar_runs = run_sweep(config)
    out_dir = Path(args.out_dir)
    write_scalar_tables(out_dir, config, scalar_runs)
    plot_temporal_evolution(out_dir, config, series)
    plot_temporal_comparison_by_eta(out_dir, config, series)
    plot_curves_c_and_d(out_dir, config, series, scalar_runs)
    print(f"Done. Files written to: {out_dir.resolve()}", flush=True)


if __name__ == "__main__":
    main()
