"""High-noise extension for TP2 points c/d (without regenerating point b plots).

This script reuses the TP2 sweep/plot helpers and only writes:
- c_va_vs_eta_por_escenario.png
- d_comparacion_escenarios.png
- va_vs_eta_summary.csv
- va_vs_eta_summary.txt

in a separate output directory.
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path

import numpy as np

from tp2_bcd import RunConfig, SCENARIOS, parse_eta_values, plot_curves_c_and_d, run_sweep, write_scalar_tables


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate TP2 c/d plots with extended noise range.")
    parser.add_argument("--out-dir", default="output/tp2_cd_high_noise", help="Output directory for c/d figures and tables")
    parser.add_argument("--L", type=float, default=10.0)
    parser.add_argument("--rho", type=float, default=4.0)
    parser.add_argument("--r0", type=float, default=1.0)
    parser.add_argument("--v0", type=float, default=0.03)
    parser.add_argument("--tmax", type=int, default=750, help="Total time steps per run")
    parser.add_argument("--runs-per-eta", type=int, default=2, help="Independent runs for each eta and scenario")
    parser.add_argument("--eta-min", type=float, default=0.0)
    parser.add_argument("--eta-max", type=float, default=12.0, help="Extended maximum noise")
    parser.add_argument("--eta-step", type=float, default=1.0)
    parser.add_argument("--stationary-start", type=int, default=500, help="Start time for stationary window (t >= stationary-start)")
    parser.add_argument("--fixed-leader-angle", type=float, default=math.pi / 4.0)
    parser.add_argument("--circle-radius", type=float, default=5.0)
    parser.add_argument("--seed-base", type=int, default=22345)
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, (os.cpu_count() or 2) - 2),
        help="Parallel worker processes",
    )
    parser.add_argument("--target-va", type=float, default=0.10, help="Target stationary mean va at eta_max (per scenario)")
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
        f"Running high-noise sweep: scenarios={len(SCENARIOS)}, etas={len(config.eta_values)} "
        f"(eta_max={args.eta_max:.3f}), runs/eta={config.runs_per_eta}, tmax={config.tmax}, workers={config.workers}",
        flush=True,
    )

    series, scalar_runs = run_sweep(config)
    out_dir = Path(args.out_dir)
    write_scalar_tables(out_dir, config, scalar_runs)
    plot_curves_c_and_d(out_dir, config, series, scalar_runs)

    eta_max = float(config.eta_values[-1])
    print("\nStationary mean va at highest eta:", flush=True)
    all_hit_target = True
    for scenario in SCENARIOS:
        va_mean = float(np.mean(scalar_runs[scenario][eta_max]))
        print(f"  scenario={scenario:8s} eta={eta_max:.3f} mean_va={va_mean:.4f}", flush=True)
        if va_mean > args.target_va:
            all_hit_target = False

    if all_hit_target:
        print(f"[ok] All scenarios reached mean_va <= {args.target_va:.3f} at eta={eta_max:.3f}", flush=True)
    else:
        print(
            f"[warn] Not all scenarios reached mean_va <= {args.target_va:.3f}. "
            f"Try increasing --eta-max.",
            flush=True,
        )

    print(f"Done. Files written to: {out_dir.resolve()}", flush=True)


if __name__ == "__main__":
    main()
