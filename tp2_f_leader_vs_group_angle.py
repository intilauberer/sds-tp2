"""TP2 punto f: angulo del lider vs angulo del grupo.

Genera una figura con dos paneles:
- lider fijo
- lider circular

En cada panel:
- theta_grupo(t) en [0, 2pi] (linea continua)
- theta_lider(t) en [0, 2pi] (linea punteada)
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np

from vicsek import VicsekSimulation


SCENARIOS = ("fixed", "circular")


def wrap_0_2pi(theta: float) -> float:
    return float(theta % (2.0 * math.pi))


def group_angle(sim: VicsekSimulation) -> float:
    vx_sum = 0.0
    vy_sum = 0.0
    for p in sim.particles:
        vx, vy = p.velocity(sim.v0)
        vx_sum += vx
        vy_sum += vy
    return wrap_0_2pi(math.atan2(vy_sum, vx_sum))


def simulate_angles(
    scenario: str,
    n_particles: int,
    L: float,
    rho: float,
    r0: float,
    v0: float,
    eta: float,
    tmax: int,
    seed: int,
    fixed_leader_angle: float,
    circle_radius: float,
) -> Dict[str, np.ndarray]:
    sim = VicsekSimulation(
        n_particles=n_particles,
        box_size=L,
        density=rho,
        interaction_radius=r0,
        speed=v0,
        noise=eta,
        dt=1.0,
        seed=seed,
        leader_mode=scenario,
        leader_id=0,
        leader_direction=(fixed_leader_angle if scenario == "fixed" else None),
        leader_circle_center=(L / 2.0, L / 2.0),
        leader_circle_radius=circle_radius,
    )

    t = np.arange(tmax + 1, dtype=int)
    theta_group = np.zeros(tmax + 1, dtype=float)
    theta_leader = np.zeros(tmax + 1, dtype=float)

    for i in range(tmax + 1):
        theta_group[i] = group_angle(sim)
        theta_leader[i] = wrap_0_2pi(sim.particles[sim.leader_id].theta)
        sim.step()

    return {"t": t, "theta_group": theta_group, "theta_leader": theta_leader}


def main() -> None:
    parser = argparse.ArgumentParser(description="TP2 f: angulo del lider vs angulo del grupo.")
    parser.add_argument("--out-dir", default="output/tp2_f", help="Directorio de salida")
    parser.add_argument("--out-name", default="f_angulo_lider_vs_grupo.png", help="Nombre del grafico")
    parser.add_argument("--L", type=float, default=10.0)
    parser.add_argument("--rho", type=float, default=4.0)
    parser.add_argument("--r0", type=float, default=1.0)
    parser.add_argument("--v0", type=float, default=0.03)
    parser.add_argument("--eta", type=float, default=1.0, help="Ruido usado en ambos escenarios")
    parser.add_argument("--tmax", type=int, default=750)
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--fixed-leader-angle", type=float, default=math.pi / 4.0)
    parser.add_argument("--circle-radius", type=float, default=5.0)
    args = parser.parse_args()

    n_particles = int(round(args.rho * args.L * args.L))
    results: Dict[str, Dict[str, np.ndarray]] = {}
    for i, scenario in enumerate(SCENARIOS):
        results[scenario] = simulate_angles(
            scenario=scenario,
            n_particles=n_particles,
            L=args.L,
            rho=args.rho,
            r0=args.r0,
            v0=args.v0,
            eta=args.eta,
            tmax=args.tmax,
            seed=args.seed + 1000 * i,
            fixed_leader_angle=args.fixed_leader_angle,
            circle_radius=args.circle_radius,
        )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / args.out_name

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5), sharey=True, constrained_layout=True)
    for ax, scenario in zip(axes, SCENARIOS):
        t = results[scenario]["t"]
        theta_group = results[scenario]["theta_group"]
        theta_leader = results[scenario]["theta_leader"]
        ax.plot(t, theta_group, lw=1.8, color="#1f77b4", label=r"$\theta_{grupo}(t)$")
        ax.plot(t, theta_leader, lw=1.8, ls="--", color="#d62728", label=r"$\theta_{lider}(t)$")
        ax.set_title(f"Escenario: {scenario}")
        ax.set_xlabel("t")
        ax.grid(alpha=0.3)
        ax.set_ylim(0.0, 2.0 * math.pi)
        ax.set_yticks([0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi])
        ax.set_yticklabels(["0", r"$\pi/2$", r"$\pi$", r"$3\pi/2$", r"$2\pi$"])
        ax.legend(loc="upper right")
    axes[0].set_ylabel("Angulo [rad]")

    fig.savefig(out_path, dpi=220)
    plt.close(fig)
    print(f"[ok] figure: {out_path.resolve()}")


if __name__ == "__main__":
    main()
