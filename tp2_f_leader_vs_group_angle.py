"""TP2 punto f: angulo del lider vs angulo promedio del sistema (sin lider).

Genera figuras separadas por escenario:
- lider fijo
- lider circular

En cada panel:
- theta_S(t) en [0, 2pi] (linea continua)
- theta_lider(t) en [0, 2pi] (linea punteada)

Ademas calcula correlacion angular:
    C(t) = cos(theta_L(t) - theta_S(t))
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

FIG_TITLE_SIZE = 20
AXIS_LABEL_SIZE = 18
TICK_LABEL_SIZE = 16
LEGEND_SIZE = 14


def apply_axes_style(ax: plt.Axes) -> None:
    ax.tick_params(axis="both", which="major", labelsize=TICK_LABEL_SIZE)


def wrap_0_2pi(theta: float) -> float:
    return float(theta % (2.0 * math.pi))


def system_angle_without_leader(sim: VicsekSimulation) -> float:
    """theta_S = atan2(<sin(theta_i)>, <cos(theta_i)>), excluyendo al lider."""
    sin_sum = 0.0
    cos_sum = 0.0
    count = 0
    for i, p in enumerate(sim.particles):
        if i == sim.leader_id:
            continue
        sin_sum += math.sin(p.theta)
        cos_sum += math.cos(p.theta)
        count += 1
    if count == 0:
        return 0.0
    return wrap_0_2pi(math.atan2(sin_sum / count, cos_sum / count))


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
    theta_system = np.zeros(tmax + 1, dtype=float)
    theta_leader = np.zeros(tmax + 1, dtype=float)
    corr = np.zeros(tmax + 1, dtype=float)

    for i in range(tmax + 1):
        theta_system[i] = system_angle_without_leader(sim)
        theta_leader[i] = wrap_0_2pi(sim.particles[sim.leader_id].theta)
        corr[i] = math.cos(theta_leader[i] - theta_system[i])
        sim.step()

    return {"t": t, "theta_system": theta_system, "theta_leader": theta_leader, "corr": corr}


def main() -> None:
    parser = argparse.ArgumentParser(description="TP2 f: angulo del lider vs angulo del grupo.")
    parser.add_argument("--out-dir", default="output/tp2_f", help="Directorio de salida")
    parser.add_argument("--out-name-prefix", default="f_angulo_lider_vs_grupo", help="Prefijo del grafico de angulos")
    parser.add_argument("--corr-out-name-prefix", default="f_correlacion_lider_sistema", help="Prefijo del grafico de C(t)")
    parser.add_argument("--save-series", action="store_true", help="Guardar series theta_S, theta_L y C(t) a txt")
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
    for scenario in SCENARIOS:
        t = results[scenario]["t"]
        theta_system = results[scenario]["theta_system"]
        theta_leader = results[scenario]["theta_leader"]

        out_path = out_dir / f"{args.out_name_prefix}_{scenario}.png"
        fig, ax = plt.subplots(1, 1, figsize=(8.0, 4.5), constrained_layout=True)
        ax.plot(t, theta_system, lw=1.8, color="#1f77b4", label=r"$\theta_{S}(t)$")
        ax.plot(t, theta_leader, lw=1.8, ls="--", color="#d62728", label=r"$\theta_{lider}(t)$")
        ax.set_title(f"Escenario: {scenario}", fontsize=FIG_TITLE_SIZE)
        ax.set_xlabel("Tiempo (pasos)", fontsize=AXIS_LABEL_SIZE)
        ax.set_ylabel("Ángulo (rad)", fontsize=AXIS_LABEL_SIZE)
        ax.grid(alpha=0.3)
        ax.set_ylim(0.0, 2.0 * math.pi)
        ax.set_yticks([0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi])
        ax.set_yticklabels(["0", r"$\pi/2$", r"$\pi$", r"$3\pi/2$", r"$2\pi$"])
        apply_axes_style(ax)
        ax.legend(loc="upper right", fontsize=LEGEND_SIZE)
        fig.savefig(out_path, dpi=220)
        plt.close(fig)
        print(f"[ok] figure: {out_path.resolve()}")

        corr_path = out_dir / f"{args.corr_out_name_prefix}_{scenario}.png"
        fig2, ax2 = plt.subplots(1, 1, figsize=(8.0, 4.0), constrained_layout=True)
        c = results[scenario]["corr"]
        ax2.plot(t, c, lw=1.8, color="#2ca02c", label=r"$C(t)=\cos(\theta_L-\theta_S)$")
        ax2.set_title(f"Escenario: {scenario}", fontsize=FIG_TITLE_SIZE)
        ax2.set_xlabel("Tiempo (pasos)", fontsize=AXIS_LABEL_SIZE)
        ax2.set_ylabel("Correlación angular", fontsize=AXIS_LABEL_SIZE)
        ax2.set_ylim(-1.05, 1.05)
        ax2.grid(alpha=0.3)
        apply_axes_style(ax2)
        ax2.legend(loc="upper right", fontsize=LEGEND_SIZE)
        fig2.savefig(corr_path, dpi=220)
        plt.close(fig2)
        print(f"[ok] correlation figure: {corr_path.resolve()}")

    if args.save_series:
        for scenario in SCENARIOS:
            series_path = out_dir / f"f_series_{scenario}.txt"
            t = results[scenario]["t"]
            theta_s = results[scenario]["theta_system"]
            theta_l = results[scenario]["theta_leader"]
            c = results[scenario]["corr"]
            with open(series_path, "w", encoding="utf-8") as f:
                f.write("# t theta_S theta_L C\n")
                for i in range(len(t)):
                    f.write(f"{int(t[i])} {theta_s[i]:.8f} {theta_l[i]:.8f} {c[i]:.8f}\n")
            print(f"[ok] series: {series_path.resolve()}")


if __name__ == "__main__":
    main()
