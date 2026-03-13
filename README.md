# Vicsek Model Simulation (TP2)

## Overview

This project provides a minimal implementation of the Vicsek self-propelled particle model (off-lattice) with support for a **leader particle** in three scenarios:

- **No leader** (standard Vicsek model)
- **Leader with fixed direction** (constant heading)
- **Leader moving on a circular trajectory** (predefined circular path)

The simulation outputs text files suitable for offline animation and analysis.

## Running the Simulation

```bash
python vicsek.py \
  --L 10.0 \
  --rho 4.0 \
  --r0 1.0 \
  --v0 0.03 \
  --eta 0.2 \
  --tmax 1000 \
  --output-interval 10 \
  --out-dir output \
  --leader fixed \
  --leader-angle 1.5
```

### Output Files

- `output/vicsek_trajectory.txt` — positions and velocities for each particle at each saved time step
- `output/vicsek_order.txt` — order parameter (polarization) vs time

### Analysis helper script

- `plot_order.py` — quick plot of the order parameter vs time (requires `matplotlib`).

## Notes

- The simulation enforces **periodic boundary conditions** in a square box of side `L`.
- The number of particles is computed as `N = rho * L^2`.
- The leader is always particle `id=0` by default (configurable via `--leader-id`).

## Next Steps (for the assignment)

- Use the generated trajectory file to create animations where arrows represent velocity vectors colored by angle.
- Compute the stationary average order parameter from `vicsek_order.txt`.
- Sweep `--eta` to build the `input vs observable` curves required by the assignment.
