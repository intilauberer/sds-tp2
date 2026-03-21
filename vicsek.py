"""Vicsek-model simulation for self-propelled particles (off-lattice).

This implementation supports:
 - standard Vicsek model (no leader)
 - leader with fixed direction
 - leader with circular trajectory
 - leader moving on a straight line (y = a*x + b in unwrapped space)

Outputs:
 - trajectory file: each line: t id x y vx vy
 - order parameter file: each line: t order

Usage:
    python -m vicsek --help

"""

from __future__ import annotations

import argparse
import math
import os
import random
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

import numpy as np


@dataclass
class Particle:
    id: int
    x: float
    y: float
    theta: float  # direction angle in radians

    def velocity(self, speed: float) -> Tuple[float, float]:
        return (speed * math.cos(self.theta), speed * math.sin(self.theta))


class VicsekSimulation:
    def __init__(
        self,
        n_particles: int,
        box_size: float,
        density: float,
        interaction_radius: float,
        speed: float,
        noise: float,
        dt: float = 1.0,
        seed: Optional[int] = None,
        leader_mode: str = "none",
        leader_id: int = 0,
        leader_direction: Optional[float] = None,
        leader_circle_center: Optional[Tuple[float, float]] = None,
        leader_circle_radius: float = 5.0,
        leader_line_slope: float = 0.0,
        leader_line_intercept: float = 0.0,
    ):
        self.n = n_particles
        self.L = box_size
        self.rho = density
        self.r0 = interaction_radius
        self.v0 = speed
        self.noise = noise
        self.dt = dt
        self.leader_mode = leader_mode
        self.leader_id = leader_id
        self.leader_direction = leader_direction
        self.leader_circle_center = leader_circle_center
        self.leader_circle_radius = leader_circle_radius
        self.leader_line_slope = leader_line_slope
        self.leader_line_intercept = leader_line_intercept

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        self.particles: List[Particle] = []
        self._init_particles()

        # For circular leader
        self._leader_angle = 0.0
        if self.leader_mode == "circular":
            # angular velocity such that v = R * omega
            self._leader_omega = self.v0 / max(1e-9, self.leader_circle_radius)
            self._leader_angle = 0.0
        elif self.leader_mode == "line":
            # Unit direction vector for straight-line motion with slope a.
            norm = math.sqrt(1.0 + self.leader_line_slope * self.leader_line_slope)
            self._leader_line_dx = 1.0 / norm
            self._leader_line_dy = self.leader_line_slope / norm

    def _init_particles(self) -> None:
        # Initialize positions uniformly in box [0,L)
        positions = np.random.rand(self.n, 2) * self.L
        # Initialize directions uniformly [0, 2*pi)
        thetas = np.random.rand(self.n) * 2 * math.pi

        self.particles = [Particle(i, float(positions[i, 0]), float(positions[i, 1]), float(thetas[i])) for i in range(self.n)]

        # If leader has fixed direction, overwrite its theta.
        if self.leader_mode == "fixed":
            if self.leader_direction is None:
                self.leader_direction = random.random() * 2 * math.pi
            self.particles[self.leader_id].theta = self.leader_direction

        # If circular leader, set its initial position on circle
        if self.leader_mode == "circular":
            if self.leader_circle_center is None:
                self.leader_circle_center = (self.L / 2.0, self.L / 2.0)
            cx, cy = self.leader_circle_center
            self.particles[self.leader_id].x = cx + self.leader_circle_radius
            self.particles[self.leader_id].y = cy
            self._leader_angle = 0.0
            # direction tangent to circle (counterclockwise)
            self.particles[self.leader_id].theta = self._leader_angle + math.pi / 2.0

        # If line leader, set initial point from y = a*x + b at x=0.
        if self.leader_mode == "line":
            a = self.leader_line_slope
            b = self.leader_line_intercept
            self.particles[self.leader_id].x = 0.0
            self.particles[self.leader_id].y = self._apply_periodic(b)
            self.particles[self.leader_id].theta = math.atan2(a, 1.0)

    def _apply_periodic(self, x: float) -> float:
        # Periodic boundary [0,L)
        if x < 0:
            return x + self.L
        if x >= self.L:
            return x - self.L
        return x

    def _vector_periodic(self, dx: float, dy: float) -> Tuple[float, float]:
        # Apply periodic boundary differences (minimum image)
        if dx > self.L / 2:
            dx -= self.L
        elif dx < -self.L / 2:
            dx += self.L
        if dy > self.L / 2:
            dy -= self.L
        elif dy < -self.L / 2:
            dy += self.L
        return dx, dy

    def _neighbor_average_angle(self, idx: int) -> float:
        # Compute average direction (angle) of neighbors within r0 (including self)
        p = self.particles[idx]
        cos_sum = 0.0
        sin_sum = 0.0
        for q in self.particles:
            dx = q.x - p.x
            dy = q.y - p.y
            dx, dy = self._vector_periodic(dx, dy)
            dist2 = dx * dx + dy * dy
            if dist2 <= self.r0 * self.r0:
                cos_sum += math.cos(q.theta)
                sin_sum += math.sin(q.theta)
        # Handle case of no neighbors (should not happen)
        if cos_sum == 0 and sin_sum == 0:
            return p.theta
        return math.atan2(sin_sum, cos_sum)

    def _update_leader(self, t: float) -> None:
        leader = self.particles[self.leader_id]
        if self.leader_mode == "none":
            return
        if self.leader_mode == "fixed":
            # direction fixed; position updated as normal
            pass
        elif self.leader_mode == "circular":
            # Update leader angle
            self._leader_angle += self._leader_omega * self.dt
            cx, cy = self.leader_circle_center
            leader.x = cx + self.leader_circle_radius * math.cos(self._leader_angle)
            leader.y = cy + self.leader_circle_radius * math.sin(self._leader_angle)
            # Tangential direction (counter clockwise)
            leader.theta = self._leader_angle + math.pi / 2.0
        elif self.leader_mode == "line":
            leader.x = self._apply_periodic(leader.x + self.v0 * self._leader_line_dx * self.dt)
            leader.y = self._apply_periodic(leader.y + self.v0 * self._leader_line_dy * self.dt)
            leader.theta = math.atan2(self.leader_line_slope, 1.0)

    def step(self) -> None:
        # First compute new directions for all particles except externally-controlled leaders.
        new_thetas = [p.theta for p in self.particles]
        for i, p in enumerate(self.particles):
            if self.leader_mode == "fixed" and i == self.leader_id:
                # fixed leader direction stays constant
                new_thetas[i] = self.leader_direction if self.leader_direction is not None else p.theta
                continue
            if self.leader_mode in ("circular", "line") and i == self.leader_id:
                # will update in _update_leader
                continue
            avg_angle = self._neighbor_average_angle(i)
            # add noise uniformly in [-noise/2, noise/2]
            delta = (random.random() - 0.5) * self.noise
            new_thetas[i] = avg_angle + delta

        # update directions
        for i, p in enumerate(self.particles):
            if self.leader_mode in ("circular", "line") and i == self.leader_id:
                continue
            p.theta = new_thetas[i]

        # Move particles
        for i, p in enumerate(self.particles):
            if self.leader_mode in ("circular", "line") and i == self.leader_id:
                # externally-controlled leader handled separately
                continue
            vx, vy = p.velocity(self.v0)
            p.x = self._apply_periodic(p.x + vx * self.dt)
            p.y = self._apply_periodic(p.y + vy * self.dt)

        # Update leader after motion for externally-controlled cases
        if self.leader_mode in ("circular", "line"):
            self._update_leader(t=0)

    def order_parameter(self) -> float:
        # Polarization magnitude
        vx_sum = 0.0
        vy_sum = 0.0
        for p in self.particles:
            vx, vy = p.velocity(self.v0)
            vx_sum += vx
            vy_sum += vy
        speed = self.v0 * self.n
        if speed == 0:
            return 0.0
        return math.sqrt(vx_sum * vx_sum + vy_sum * vy_sum) / speed

    def run(
        self,
        t_max: int,
        output_interval: int,
        out_dir: str,
        prefix: str = "sim",
        save_order: bool = True,
    ) -> None:
        os.makedirs(out_dir, exist_ok=True)
        traj_path = os.path.join(out_dir, f"{prefix}_trajectory.txt")
        order_path = os.path.join(out_dir, f"{prefix}_order.txt")

        with open(traj_path, "w", encoding="utf-8") as ftraj, open(order_path, "w", encoding="utf-8") as Forder:
            # header
            ftraj.write("# t id x y vx vy\n")
            Forder.write("# t order\n")

            for t in range(t_max + 1):
                if t % output_interval == 0:
                    order = self.order_parameter()
                    Forder.write(f"{t} {order:.6f}\n")
                    for p in self.particles:
                        vx, vy = p.velocity(self.v0)
                        ftraj.write(f"{t} {p.id} {p.x:.6f} {p.y:.6f} {vx:.6f} {vy:.6f}\n")
                self.step()


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Vicsek model simulation (off-lattice).")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    parser.add_argument("--L", type=float, default=10.0, help="Box side length")
    parser.add_argument("--rho", type=float, default=4.0, help="Particle density")
    parser.add_argument("--r0", type=float, default=1.0, help="Interaction radius")
    parser.add_argument("--v0", type=float, default=0.03, help="Particle speed")
    parser.add_argument("--eta", type=float, default=0.1, help="Noise strength (eta)")
    parser.add_argument("--tmax", type=int, default=500, help="Number of time steps")
    parser.add_argument("--output-interval", type=int, default=10, help="Output interval")
    parser.add_argument("--out-dir", type=str, default="output", help="Output directory")
    parser.add_argument("--leader", choices=["none", "fixed", "circular", "line"], default="none", help="Leader mode")
    parser.add_argument("--leader-id", type=int, default=0, help="Leader particle id")
    parser.add_argument("--leader-angle", type=float, default=None, help="Fixed leader direction (rad)")
    parser.add_argument("--circle-radius", type=float, default=5.0, help="Radius for circular leader trajectory")
    parser.add_argument("--line-slope", type=float, default=0.0, help="Slope 'a' for line leader y = a*x + b")
    parser.add_argument("--line-intercept", type=float, default=0.0, help="Intercept 'b' for line leader y = a*x + b")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    n_particles = int(round(args.rho * args.L * args.L))
    sim = VicsekSimulation(
        n_particles=n_particles,
        box_size=args.L,
        density=args.rho,
        interaction_radius=args.r0,
        speed=args.v0,
        noise=args.eta,
        dt=1.0,
        seed=args.seed,
        leader_mode=args.leader,
        leader_id=args.leader_id,
        leader_direction=args.leader_angle,
        leader_circle_center=(args.L / 2.0, args.L / 2.0),
        leader_circle_radius=args.circle_radius,
        leader_line_slope=args.line_slope,
        leader_line_intercept=args.line_intercept,
    )
    sim.run(t_max=args.tmax, output_interval=args.output_interval, out_dir=args.out_dir, prefix="vicsek")


if __name__ == "__main__":
    main()
