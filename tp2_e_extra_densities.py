"""TP2 item (e): extra densities rho=2 and rho=8.

Generates:
- 4 characteristic animations total:
  - rho=2 at low/high noise
  - rho=8 at low/high noise
- 2 comparative plots like item (d):
  - one for rho=2
  - one for rho=8

All outputs are written to a separate directory.
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np

from animate_vicsek import load_trajectory, make_animation
from tp2_bcd import RunConfig, SCENARIOS, parse_eta_values, run_sweep, write_scalar_tables
from vicsek import VicsekSimulation


def plot_d_only(
    out_path: Path,
    config: RunConfig,
    series: Dict[str, Dict[float, np.ndarray]],
    scalar_runs: Dict[str, Dict[float, np.ndarray]],
) -> None:
    eta = np.array(config.eta_values, dtype=float)
    scenario_colors = {"none": "#1f77b4", "fixed": "#2ca02c", "circular": "#d62728"}
    stationary_start = min(max(config.stationary_start, 0), config.tmax)

    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    for scenario in SCENARIOS:
        means = []
        errs = []
        for e in eta:
            vals = scalar_runs[scenario][float(e)]
            means.append(float(np.mean(vals)))
            stationary_vals = series[scenario][float(e)][:, stationary_start:].reshape(-1)
            if stationary_vals.size > 1:
                errs.append(float(np.std(stationary_vals, ddof=1)))
            else:
                errs.append(0.0)
        ax.errorbar(
            eta,
            np.array(means),
            yerr=np.array(errs),
            marker="o",
            lw=1.8,
            capsize=3,
            label=scenario,
            color=scenario_colors[scenario],
        )

    ax.set_xlabel(r"Ruido $\eta$")
    ax.set_ylabel(r"$\langle v_a \rangle$ estacionario")
    ax.set_title(f"Comparacion de escenarios (rho={config.rho:g})")
    ax.grid(alpha=0.3)
    ax.legend()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def run_animation_case(
    out_dir: Path,
    rho: float,
    eta: float,
    seed: int,
    L: float,
    r0: float,
    v0: float,
    tmax: int,
    output_interval: int,
    leader_mode: str,
    fixed_leader_angle: float,
    circle_radius: float,
    fps: int,
    arrow_length: float,
) -> Path:
    n_particles = int(round(rho * L * L))
    sim = VicsekSimulation(
        n_particles=n_particles,
        box_size=L,
        density=rho,
        interaction_radius=r0,
        speed=v0,
        noise=eta,
        dt=1.0,
        seed=seed,
        leader_mode=leader_mode,
        leader_id=0,
        leader_direction=(fixed_leader_angle if leader_mode == "fixed" else None),
        leader_circle_center=(L / 2.0, L / 2.0),
        leader_circle_radius=circle_radius,
    )

    tag = f"rho_{rho:g}_eta_{eta:g}".replace(".", "p")
    case_dir = out_dir / f"rho_{rho:g}" / "animations"
    case_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"vicsek_{tag}"
    sim.run(
        t_max=tmax,
        output_interval=output_interval,
        out_dir=str(case_dir),
        prefix=prefix,
        save_order=True,
    )

    traj_path = case_dir / f"{prefix}_trajectory.txt"
    anim_path = case_dir / f"{tag}.gif"
    times, data = load_trajectory(str(traj_path))
    leader_id = 0 if leader_mode != "none" else -1
    make_animation(
        times=times,
        data=data,
        box_size=L,
        leader_id=leader_id,
        out_path=str(anim_path),
        arrow_length=arrow_length,
        fps=fps,
        dpi=120,
    )
    return anim_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate TP2 item (e): extra densities and characteristic animations.")
    parser.add_argument("--out-dir", default="output/tp2_e", help="Output directory for item (e)")
    parser.add_argument("--densities", type=float, nargs="+", default=[2.0, 8.0], help="One or more extra densities")
    parser.add_argument("--eta-min", type=float, default=0.0)
    parser.add_argument("--eta-max", type=float, default=6.0)
    parser.add_argument("--eta-step", type=float, default=1.0)
    parser.add_argument("--runs-per-eta", type=int, default=2)
    parser.add_argument("--tmax-graphs", type=int, default=750)
    parser.add_argument("--stationary-start", type=int, default=500)
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))

    parser.add_argument("--L", type=float, default=10.0)
    parser.add_argument("--r0", type=float, default=1.0)
    parser.add_argument("--v0", type=float, default=0.03)
    parser.add_argument("--fixed-leader-angle", type=float, default=math.pi / 4.0)
    parser.add_argument("--circle-radius", type=float, default=5.0)

    parser.add_argument("--anim-low-eta", type=float, default=0.6)
    parser.add_argument("--anim-high-eta", type=float, default=6.0)
    parser.add_argument("--anim-leader", choices=["none", "fixed", "circular"], default="none")
    parser.add_argument("--anim-tmax", type=int, default=500)
    parser.add_argument("--anim-output-interval", type=int, default=5)
    parser.add_argument("--anim-fps", type=int, default=12)
    parser.add_argument("--anim-arrow-length", type=float, default=0.25)
    parser.add_argument("--seed-base", type=int, default=30300)
    parser.add_argument("--skip-graphs", action="store_true", help="Skip comparative sweep/plots and tables")
    parser.add_argument("--skip-animations", action="store_true", help="Skip characteristic animations")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    eta_values = parse_eta_values(args.eta_min, args.eta_max, args.eta_step)
    densities = []
    for d in args.densities:
        if d <= 0:
            continue
        # keep order, remove duplicates
        if d not in densities:
            densities.append(d)
    if not densities:
        raise ValueError("No valid positive densities provided in --densities")

    print(
        f"Item (e): densities={densities}, eta_range=[{args.eta_min}, {args.eta_max}] step={args.eta_step}, "
        f"workers={args.workers}, skip_graphs={args.skip_graphs}, skip_animations={args.skip_animations}",
        flush=True,
    )

    for rho_i, rho in enumerate(densities):
        if not args.skip_graphs:
            print(f"\n[rho={rho:g}] Running comparative sweep...", flush=True)
            config = RunConfig(
                L=args.L,
                rho=rho,
                r0=args.r0,
                v0=args.v0,
                tmax=args.tmax_graphs,
                eta_values=eta_values,
                runs_per_eta=args.runs_per_eta,
                stationary_start=args.stationary_start,
                fixed_leader_angle=args.fixed_leader_angle,
                circle_radius=args.circle_radius,
                seed_base=args.seed_base + 10_000 * rho_i,
                workers=args.workers,
            )
            series, scalar_runs = run_sweep(config)

            rho_dir = out_dir / f"rho_{rho:g}"
            write_scalar_tables(rho_dir, config, scalar_runs)
            d_path = rho_dir / f"d_comparacion_escenarios_rho_{rho:g}.png"
            plot_d_only(d_path, config, series, scalar_runs)
            print(f"[rho={rho:g}] Saved comparative figure: {d_path}", flush=True)

        if args.skip_animations:
            continue
        if args.anim_tmax <= 0:
            print(f"[rho={rho:g}] Skipping animations because --anim-tmax <= 0", flush=True)
            continue

        print(f"[rho={rho:g}] Rendering two animations (low/high noise)...", flush=True)
        low_anim = run_animation_case(
            out_dir=out_dir,
            rho=rho,
            eta=args.anim_low_eta,
            seed=args.seed_base + 100 * rho_i + 1,
            L=args.L,
            r0=args.r0,
            v0=args.v0,
            tmax=args.anim_tmax,
            output_interval=args.anim_output_interval,
            leader_mode=args.anim_leader,
            fixed_leader_angle=args.fixed_leader_angle,
            circle_radius=args.circle_radius,
            fps=args.anim_fps,
            arrow_length=args.anim_arrow_length,
        )
        high_anim = run_animation_case(
            out_dir=out_dir,
            rho=rho,
            eta=args.anim_high_eta,
            seed=args.seed_base + 100 * rho_i + 2,
            L=args.L,
            r0=args.r0,
            v0=args.v0,
            tmax=args.anim_tmax,
            output_interval=args.anim_output_interval,
            leader_mode=args.anim_leader,
            fixed_leader_angle=args.fixed_leader_angle,
            circle_radius=args.circle_radius,
            fps=args.anim_fps,
            arrow_length=args.anim_arrow_length,
        )
        print(f"[rho={rho:g}] Animations: {low_anim} | {high_anim}", flush=True)

    print(f"\nDone. Item (e) outputs written to: {out_dir.resolve()}", flush=True)


if __name__ == "__main__":
    main()
