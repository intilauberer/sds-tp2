"""TP2 EXTRA: Natural rotation in Vicsek model (no external wind force).

Idea:
- Keep standard 2D Vicsek dynamics (alignment + noise).
- Make rotation possible by choosing vortex-like initial directions.
- Reuse existing animation style via animate_vicsek.py.
"""

from __future__ import annotations

import argparse
import math
import os
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np


@dataclass
class Particle:
    id: int
    x: float
    y: float
    theta: float
    ttl: int
    spawn_x: float
    spawn_y: float
    spawn_theta: float
    active: bool
    release_step: int

    def velocity(self, speed: float) -> Tuple[float, float]:
        return (speed * math.cos(self.theta), speed * math.sin(self.theta))


class NaturalRotationVicsekSimulation:
    def __init__(
        self,
        n_particles: int,
        box_size: float,
        interaction_radius: float,
        speed: float,
        noise: float,
        init_mode: str,
        vortex_dir: int,
        init_angle_noise: float,
        ttl_min: int,
        ttl_max: int,
        feed_mode: str,
        feed_angle: float,
        feed_pattern: str,
        chunk_size: int,
        chunk_interval: int,
        dt: float = 1.0,
        seed: Optional[int] = None,
    ) -> None:
        self.n = n_particles
        self.L = box_size
        self.r0 = interaction_radius
        self.v0 = speed
        self.noise = noise
        self.init_mode = init_mode
        self.vortex_dir = vortex_dir
        self.init_angle_noise = init_angle_noise
        self.ttl_min = ttl_min
        self.ttl_max = ttl_max
        self.feed_mode = feed_mode
        self.feed_angle = feed_angle
        self.feed_pattern = feed_pattern
        self.chunk_size = max(1, chunk_size)
        self.chunk_interval = max(1, chunk_interval)
        self.dt = dt
        self.center = (self.L / 2.0, self.L / 2.0)
        self.total_respawns = 0
        self.step_count = 0

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        self.particles: List[Particle] = []
        self._init_particles()

    def _random_ttl(self) -> int:
        if self.ttl_max <= self.ttl_min:
            return self.ttl_min
        return random.randint(self.ttl_min, self.ttl_max)

    def _vortex_tangent_angle(self, x: float, y: float) -> float:
        cx, cy = self.center
        dx = x - cx
        dy = y - cy
        dx, dy = self._vector_periodic(dx, dy)
        base = math.atan2(dy, dx)
        tangent = base + (math.pi / 2.0 if self.vortex_dir >= 0 else -math.pi / 2.0)
        return tangent

    def _sample_theta(self, x: float, y: float, mode: str) -> float:
        if mode == "random":
            return random.random() * 2.0 * math.pi
        if mode == "fixed":
            return self.feed_angle
        tangent = self._vortex_tangent_angle(x, y)
        return tangent + (random.random() - 0.5) * self.init_angle_noise

    def _stream_specs(self) -> List[Tuple[str, float]]:
        # (stream_name, heading)
        if self.feed_pattern == "user_combo":
            # Requested by user:
            # west -> east, east -> west, NW -> SE, NE -> SW
            return [
                ("west", 0.0),
                ("east", math.pi),
                ("nw", -math.pi / 4.0),
                ("ne", -3.0 * math.pi / 4.0),
            ]
        if self.feed_pattern == "cw":
            # Rotation-biased inflow (clockwise tendency)
            return [
                ("west", 0.0),
                ("nw", -math.pi / 4.0),
                ("ne", -3.0 * math.pi / 4.0),
            ]
        # ccw (default): opposite diagonal on NW for counter-clockwise tendency
        return [
            ("west", 0.0),
            ("nw", -3.0 * math.pi / 4.0),
            ("ne", -math.pi / 4.0),
        ]

    def _sample_edge_spawn(self, stream_name: str) -> Tuple[float, float]:
        eps = min(1e-3, 0.001 * self.L)
        if stream_name == "west":
            return (eps, random.random() * self.L)
        if stream_name == "east":
            return (self.L - eps, random.random() * self.L)
        if stream_name == "nw":
            return (random.random() * 0.2 * self.L, self.L - eps)
        if stream_name == "north":
            return (random.random() * self.L, self.L - eps)
        if stream_name == "ne":
            return (self.L - random.random() * 0.2 * self.L, self.L - eps)
        return (eps, random.random() * self.L)

    def _apply_periodic(self, x: float) -> float:
        if x < 0.0:
            return x + self.L
        if x >= self.L:
            return x - self.L
        return x

    def _vector_periodic(self, dx: float, dy: float) -> Tuple[float, float]:
        if dx > self.L / 2.0:
            dx -= self.L
        elif dx < -self.L / 2.0:
            dx += self.L
        if dy > self.L / 2.0:
            dy -= self.L
        elif dy < -self.L / 2.0:
            dy += self.L
        return dx, dy

    def _init_particles(self) -> None:
        self.particles = []
        if self.feed_mode == "streams":
            specs = self._stream_specs()
            n_streams = len(specs)
            for i in range(self.n):
                stream_name, stream_theta = specs[i % n_streams]
                x, y = self._sample_edge_spawn(stream_name)
                ttl = self._random_ttl()
                release_step = (i // self.chunk_size) * self.chunk_interval
                active = release_step == 0
                px, py = (x, y) if active else (-1.0, -1.0)
                self.particles.append(Particle(i, px, py, stream_theta, ttl, x, y, stream_theta, active, release_step))
            return

        positions = np.random.rand(self.n, 2) * self.L
        for i in range(self.n):
            x = float(positions[i, 0])
            y = float(positions[i, 1])
            theta = self._sample_theta(x, y, self.init_mode)
            ttl = self._random_ttl()
            self.particles.append(Particle(i, x, y, theta, ttl, x, y, theta, True, 0))

    def _neighbor_average_angle(self, idx: int) -> float:
        p = self.particles[idx]
        if not p.active:
            return p.theta
        cos_sum = 0.0
        sin_sum = 0.0
        for q in self.particles:
            if not q.active:
                continue
            dx = q.x - p.x
            dy = q.y - p.y
            dx, dy = self._vector_periodic(dx, dy)
            if dx * dx + dy * dy <= self.r0 * self.r0:
                cos_sum += math.cos(q.theta)
                sin_sum += math.sin(q.theta)
        if cos_sum == 0.0 and sin_sum == 0.0:
            return p.theta
        return math.atan2(sin_sum, cos_sum)

    def step(self) -> None:
        for p in self.particles:
            if not p.active and self.step_count >= p.release_step:
                p.active = True
                p.x = p.spawn_x
                p.y = p.spawn_y
                p.theta = p.spawn_theta
                p.ttl = self._random_ttl()

        new_thetas = [p.theta for p in self.particles]
        for i in range(self.n):
            if not self.particles[i].active:
                continue
            avg = self._neighbor_average_angle(i)
            new_thetas[i] = avg + (random.random() - 0.5) * self.noise

        replaced_this_step = 0
        for i, p in enumerate(self.particles):
            if not p.active:
                continue
            p.theta = new_thetas[i]
            vx, vy = p.velocity(self.v0)
            p.x = self._apply_periodic(p.x + vx * self.dt)
            p.y = self._apply_periodic(p.y + vy * self.dt)
            p.ttl -= 1
            if p.ttl <= 0:
                # Respawn at each particle's own original edge source and heading.
                p.x = p.spawn_x
                p.y = p.spawn_y
                p.theta = p.spawn_theta
                p.ttl = self._random_ttl()
                replaced_this_step += 1
        self.total_respawns += replaced_this_step
        self.step_count += 1

    def order_parameter(self) -> float:
        vx_sum = 0.0
        vy_sum = 0.0
        active_n = 0
        for p in self.particles:
            if not p.active:
                continue
            vx, vy = p.velocity(self.v0)
            vx_sum += vx
            vy_sum += vy
            active_n += 1
        denom = self.v0 * active_n
        if denom == 0.0:
            return 0.0
        return math.sqrt(vx_sum * vx_sum + vy_sum * vy_sum) / denom

    def circulation_parameter(self) -> float:
        # +1 means strong CCW vortex, -1 strong CW vortex, ~0 no global rotation.
        cx, cy = self.center
        s = 0.0
        count = 0
        for p in self.particles:
            if not p.active:
                continue
            dx, dy = self._vector_periodic(p.x - cx, p.y - cy)
            r = math.sqrt(dx * dx + dy * dy)
            if r < 1e-12:
                continue
            tx, ty = (-dy / r, dx / r)  # CCW tangent
            vx, vy = p.velocity(1.0)
            s += vx * tx + vy * ty
            count += 1
        if count == 0:
            return 0.0
        return s / count

    def run(
        self,
        t_max: int,
        output_interval: int,
        out_dir: str,
        prefix: str,
        live_check: bool = False,
        live_check_interval: int = 25,
    ) -> Tuple[str, str, str]:
        os.makedirs(out_dir, exist_ok=True)
        traj_path = os.path.join(out_dir, f"{prefix}_trajectory.txt")
        order_path = os.path.join(out_dir, f"{prefix}_order.txt")
        circ_path = os.path.join(out_dir, f"{prefix}_circulation.txt")

        with open(traj_path, "w", encoding="utf-8") as ftraj, open(order_path, "w", encoding="utf-8") as forder, open(circ_path, "w", encoding="utf-8") as fcirc:
            ftraj.write("# t id x y vx vy\n")
            forder.write("# t order\n")
            fcirc.write("# t circulation\n")
            for t in range(t_max + 1):
                if t % output_interval == 0:
                    order_now = self.order_parameter()
                    circ_now = self.circulation_parameter()
                    forder.write(f"{t} {order_now:.6f}\n")
                    fcirc.write(f"{t} {circ_now:.6f}\n")
                    for p in self.particles:
                        vx, vy = p.velocity(self.v0)
                        ftraj.write(f"{t} {p.id} {p.x:.6f} {p.y:.6f} {vx:.6f} {vy:.6f}\n")
                if live_check and (t % max(1, live_check_interval) == 0):
                    active_count = sum(1 for p in self.particles if p.active)
                    circ_live = self.circulation_parameter()
                    rotating = "YES" if abs(circ_live) >= 0.20 else "no"
                    print(
                        f"[live] t={t:4d}/{t_max} active={active_count:4d} "
                        f"circ={circ_live:+.3f} rotating={rotating}",
                        flush=True,
                    )
                self.step()
        return traj_path, order_path, circ_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TP2 EXTRA: Natural rotation (vortex-friendly initial conditions).")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    parser.add_argument("--L", type=float, default=4.0, help="Box side length")
    parser.add_argument("--rho", type=float, default=50.0, help="Particle density")
    parser.add_argument("--r0", type=float, default=0.7, help="Interaction radius")
    parser.add_argument("--v0", type=float, default=0.06, help="Particle speed")
    parser.add_argument("--eta", type=float, default=0.2, help="Noise strength")
    parser.add_argument("--tmax", type=int, default=200, help="Number of time steps")
    parser.add_argument("--output-interval", type=int, default=5, help="Output interval")
    parser.add_argument("--out-dir", type=str, default="output", help="Output directory")
    parser.add_argument("--prefix", type=str, default="tp2_extra", help="Output file prefix")
    parser.add_argument("--init-mode", choices=["vortex", "random"], default="vortex", help="Initial orientation mode")
    parser.add_argument("--vortex-dir", choices=["ccw", "cw"], default="ccw", help="Initial rotation direction")
    parser.add_argument(
        "--init-angle-noise",
        type=float,
        default=0.4,
        help="Initial angular perturbation around vortex tangent (radians)",
    )
    parser.add_argument("--animate-out", type=str, default="", help="Optional output animation path (gif/mp4)")
    parser.add_argument("--fps", type=int, default=20, help="Animation FPS if --animate-out is provided")
    parser.add_argument("--arrow-length", type=float, default=0.25, help="Arrow length for animation")
    parser.add_argument("--ttl-min", type=int, default=260, help="Minimum particle TTL before reinjection")
    parser.add_argument("--ttl-max", type=int, default=520, help="Maximum particle TTL before reinjection")
    parser.add_argument(
        "--feed-mode",
        choices=["streams", "fixed", "vortex", "random"],
        default="streams",
        help="How particles are initialized and respawned",
    )
    parser.add_argument(
        "--feed-pattern",
        choices=["user_combo", "cw", "ccw"],
        default="user_combo",
        help="Stream pattern when --feed-mode=streams",
    )
    parser.add_argument(
        "--feed-angle",
        type=float,
        default=math.pi / 2.0,
        help="Angle used when --feed-mode=fixed",
    )
    parser.add_argument("--chunk-size", type=int, default=120, help="Particles released per chunk at startup")
    parser.add_argument("--chunk-interval", type=int, default=8, help="Timesteps between chunk releases")
    parser.add_argument("--live-check", action="store_true", help="Print live rotation diagnostics while sim runs")
    parser.add_argument(
        "--live-check-interval",
        type=int,
        default=25,
        help="Timesteps between live diagnostics prints",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    n_particles = int(round(args.rho * args.L * args.L))
    vortex_dir = 1 if args.vortex_dir == "ccw" else -1

    sim = NaturalRotationVicsekSimulation(
        n_particles=n_particles,
        box_size=args.L,
        interaction_radius=args.r0,
        speed=args.v0,
        noise=args.eta,
        init_mode=args.init_mode,
        vortex_dir=vortex_dir,
        init_angle_noise=args.init_angle_noise,
        ttl_min=max(1, args.ttl_min),
        ttl_max=max(max(1, args.ttl_min), args.ttl_max),
        feed_mode=args.feed_mode,
        feed_angle=args.feed_angle,
        feed_pattern=args.feed_pattern,
        chunk_size=max(1, args.chunk_size),
        chunk_interval=max(1, args.chunk_interval),
        dt=1.0,
        seed=args.seed,
    )
    traj_path, order_path, circ_path = sim.run(
        t_max=args.tmax,
        output_interval=args.output_interval,
        out_dir=args.out_dir,
        prefix=args.prefix,
        live_check=args.live_check,
        live_check_interval=max(1, args.live_check_interval),
    )
    print(f"[ok] trajectory: {traj_path}")
    print(f"[ok] order: {order_path}")
    print(f"[ok] circulation: {circ_path}")
    print(f"[ok] total reinjected particles: {sim.total_respawns}")

    if args.animate_out:
        from animate_vicsek import load_trajectory, make_animation

        times, data = load_trajectory(traj_path)
        make_animation(
            times=times,
            data=data,
            box_size=args.L,
            leader_id=-1,
            out_path=args.animate_out,
            arrow_length=args.arrow_length,
            fps=args.fps,
        )
        print(f"[ok] animation: {args.animate_out}")


if __name__ == "__main__":
    main()
