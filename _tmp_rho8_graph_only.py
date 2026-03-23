import math
from pathlib import Path

from tp2_bcd import RunConfig, parse_eta_values, run_sweep, write_scalar_tables
from tp2_e_extra_densities import plot_d_only


def main() -> None:
    rho = 8.0
    eta_values = parse_eta_values(0.0, 6.0, 1.0)
    cfg = RunConfig(
        L=10.0,
        rho=rho,
        r0=1.0,
        v0=0.03,
        tmax=750,
        eta_values=eta_values,
        runs_per_eta=2,
        stationary_start=500,
        fixed_leader_angle=math.pi / 4.0,
        circle_radius=5.0,
        seed_base=40300,
        workers=10,
    )
    print('[rho=8] running sweep with workers=10 ...', flush=True)
    series, scalar_runs = run_sweep(cfg)
    rho_dir = Path('e') / 'rho_8'
    write_scalar_tables(rho_dir, cfg, scalar_runs)
    d_path = rho_dir / 'd_comparacion_escenarios_rho_8.png'
    plot_d_only(d_path, cfg, series, scalar_runs)
    print(f'[ok] graph: {d_path.resolve()}', flush=True)
    print('[done] no animations generated', flush=True)


if __name__ == '__main__':
    main()
