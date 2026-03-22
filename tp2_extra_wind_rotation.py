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
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
    stream_name: str

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
        inflow_per_step: int,
        inflow_fraction: Optional[float],
        inflow_mode: str,
        max_particles: int,
        respawn_on_edge: bool,
        alignment_strength: float,
        turn_inertia: float,
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
        self.inflow_per_step = max(0, inflow_per_step)
        self.inflow_fraction = None if inflow_fraction is None else max(0.0, min(1.0, inflow_fraction))
        self.inflow_mode = inflow_mode
        self.max_particles = max(max_particles, n_particles)
        self.respawn_on_edge = respawn_on_edge
        self.alignment_strength = min(max(alignment_strength, 0.0), 1.0)
        self.turn_inertia = min(max(turn_inertia, 0.0), 0.99)
        self.dt = dt
        self.center = (self.L / 2.0, self.L / 2.0)
        self.total_respawns = 0
        self.total_stream_injections = 0
        self.total_edge_respawns = 0
        self.step_count = 0
        self.inflow_cursor = 0

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        self.particles: List[Particle] = []
        self._init_particles()
        self.next_particle_id = len(self.particles)

    def save_state(self, state_path: str) -> None:
        p = Path(state_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            str(p),
            step_count=np.array([self.step_count], dtype=np.int64),
            total_respawns=np.array([self.total_respawns], dtype=np.int64),
            total_stream_injections=np.array([self.total_stream_injections], dtype=np.int64),
            total_edge_respawns=np.array([self.total_edge_respawns], dtype=np.int64),
            inflow_cursor=np.array([self.inflow_cursor], dtype=np.int64),
            next_particle_id=np.array([self.next_particle_id], dtype=np.int64),
            n=np.array([len(self.particles)], dtype=np.int64),
            id=np.array([p.id for p in self.particles], dtype=np.int64),
            x=np.array([p.x for p in self.particles], dtype=float),
            y=np.array([p.y for p in self.particles], dtype=float),
            theta=np.array([p.theta for p in self.particles], dtype=float),
            ttl=np.array([p.ttl for p in self.particles], dtype=np.int64),
            spawn_x=np.array([p.spawn_x for p in self.particles], dtype=float),
            spawn_y=np.array([p.spawn_y for p in self.particles], dtype=float),
            spawn_theta=np.array([p.spawn_theta for p in self.particles], dtype=float),
            active=np.array([p.active for p in self.particles], dtype=bool),
            release_step=np.array([p.release_step for p in self.particles], dtype=np.int64),
            stream_name=np.array([p.stream_name for p in self.particles], dtype=str),
        )

    def load_state(self, state_path: str) -> None:
        data = np.load(state_path, allow_pickle=True)
        self.step_count = int(data["step_count"][0])
        self.total_respawns = int(data["total_respawns"][0])
        self.total_stream_injections = int(data["total_stream_injections"][0])
        self.total_edge_respawns = int(data["total_edge_respawns"][0])
        self.inflow_cursor = int(data["inflow_cursor"][0])
        self.next_particle_id = int(data["next_particle_id"][0])
        n = int(data["n"][0])
        self.particles = []
        for i in range(n):
            self.particles.append(
                Particle(
                    id=int(data["id"][i]),
                    x=float(data["x"][i]),
                    y=float(data["y"][i]),
                    theta=float(data["theta"][i]),
                    ttl=int(data["ttl"][i]),
                    spawn_x=float(data["spawn_x"][i]),
                    spawn_y=float(data["spawn_y"][i]),
                    spawn_theta=float(data["spawn_theta"][i]),
                    active=bool(data["active"][i]),
                    release_step=int(data["release_step"][i]),
                    stream_name=str(data["stream_name"][i]),
                )
            )

    def _random_ttl(self) -> int:
        if self.ttl_max <= self.ttl_min:
            return self.ttl_min
        return random.randint(self.ttl_min, self.ttl_max)

    def _vortex_tangent_angle(self, x: float, y: float) -> float:
        cx, cy = self.center
        dx = x - cx
        dy = y - cy
        dx, dy = self._vector_direct(dx, dy)
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
        if self.feed_pattern == "vortex_ccw":
            # User-requested diagonal forcing:
            # west->southeast, east->northwest, north->southwest, sw->northeast.
            return [
                ("west", -math.pi / 4.0),
                ("east", 3.0 * math.pi / 4.0),
                ("north", -3.0 * math.pi / 4.0),
                ("sw", math.pi / 4.0),
            ]
        if self.feed_pattern == "vortex_cw":
            # Opposite diagonal forcing.
            return [
                ("west", math.pi / 4.0),
                ("east", -3.0 * math.pi / 4.0),
                ("north", -math.pi / 4.0),
            ]
        if self.feed_pattern == "user_combo":
            # Requested by user:
            # west -> east, east -> west, NW -> SE, NE -> SW, SW -> NE
            return [
                ("west", 0.0),
                ("east", math.pi),
                ("nw", -math.pi / 4.0),
                ("ne", -3.0 * math.pi / 4.0),
                ("sw", math.pi / 4.0),
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
        if stream_name == "sw":
            return (random.random() * 0.2 * self.L, random.random() * 0.2 * self.L)
        return (eps, random.random() * self.L)

    def _apply_bounds(self, x: float) -> float:
        if x < 0.0:
            return 0.0
        if x > self.L:
            return self.L
        return x

    def _vector_direct(self, dx: float, dy: float) -> Tuple[float, float]:
        return dx, dy

    @staticmethod
    def _blend_angles(theta_from: float, theta_to: float, alpha: float) -> float:
        delta = math.atan2(math.sin(theta_to - theta_from), math.cos(theta_to - theta_from))
        return theta_from + alpha * delta

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
                self.particles.append(Particle(i, px, py, stream_theta, ttl, x, y, stream_theta, active, release_step, stream_name))
            return

        positions = np.random.rand(self.n, 2) * self.L
        for i in range(self.n):
            x = float(positions[i, 0])
            y = float(positions[i, 1])
            theta = self._sample_theta(x, y, self.init_mode)
            ttl = self._random_ttl()
            self.particles.append(Particle(i, x, y, theta, ttl, x, y, theta, True, 0, ""))

    def _respawn_particle(self, p: Particle, refresh_spawn: bool = True) -> None:
        if self.feed_mode == "streams" and p.stream_name and refresh_spawn:
            x, y = self._sample_edge_spawn(p.stream_name)
            p.spawn_x = x
            p.spawn_y = y
        p.x = p.spawn_x
        p.y = p.spawn_y
        p.theta = p.spawn_theta
        p.ttl = self._random_ttl()
        p.active = True

    def _current_inflow_count(self) -> int:
        if self.inflow_fraction is None:
            return self.inflow_per_step
        active_n = sum(1 for p in self.particles if p.active)
        base = active_n if active_n > 0 else len(self.particles)
        return int(round(self.inflow_fraction * base))

    def _build_spatial_grid(self, cell_size: float) -> Dict[Tuple[int, int], List[int]]:
        grid: Dict[Tuple[int, int], List[int]] = {}
        if cell_size <= 0.0:
            return grid
        for i, p in enumerate(self.particles):
            if not p.active:
                continue
            cx = int(p.x // cell_size)
            cy = int(p.y // cell_size)
            key = (cx, cy)
            if key not in grid:
                grid[key] = []
            grid[key].append(i)
        return grid

    def _neighbor_average_angle(self, idx: int, grid: Optional[Dict[Tuple[int, int], List[int]]] = None, cell_size: float = 0.0) -> float:
        p = self.particles[idx]
        if not p.active:
            return p.theta
        cos_sum = 0.0
        sin_sum = 0.0

        if grid is None or cell_size <= 0.0:
            for q in self.particles:
                if not q.active:
                    continue
                dx = q.x - p.x
                dy = q.y - p.y
                dx, dy = self._vector_direct(dx, dy)
                if dx * dx + dy * dy <= self.r0 * self.r0:
                    cos_sum += math.cos(q.theta)
                    sin_sum += math.sin(q.theta)
        else:
            cx = int(p.x // cell_size)
            cy = int(p.y // cell_size)
            for dx_cell in (-1, 0, 1):
                for dy_cell in (-1, 0, 1):
                    bucket = grid.get((cx + dx_cell, cy + dy_cell))
                    if not bucket:
                        continue
                    for j in bucket:
                        q = self.particles[j]
                        dx = q.x - p.x
                        dy = q.y - p.y
                        dx, dy = self._vector_direct(dx, dy)
                        if dx * dx + dy * dy <= self.r0 * self.r0:
                            cos_sum += math.cos(q.theta)
                            sin_sum += math.sin(q.theta)
        if cos_sum == 0.0 and sin_sum == 0.0:
            return p.theta
        return math.atan2(sin_sum, cos_sum)

    def step(self) -> None:
        for p in self.particles:
            if not p.active and self.step_count >= p.release_step:
                self._respawn_particle(p, refresh_spawn=True)

        inflow_now = self._current_inflow_count()
        if self.feed_mode == "streams" and inflow_now > 0:
            inactive_ids = [i for i, p in enumerate(self.particles) if not p.active]
            spawned = 0
            if inactive_ids:
                n_spawn = min(inflow_now, len(inactive_ids))
                for i in range(n_spawn):
                    idx = inactive_ids[(self.inflow_cursor + i) % len(inactive_ids)]
                    self._respawn_particle(self.particles[idx], refresh_spawn=True)
                spawned = n_spawn
                self.total_stream_injections += n_spawn
                self.inflow_cursor = (self.inflow_cursor + n_spawn) % max(1, len(inactive_ids))

            remaining = inflow_now - spawned
            if remaining > 0 and self.inflow_mode == "replace_active":
                # Continuous feed by replacing active particles when needed.
                active_ids = [i for i, p in enumerate(self.particles) if p.active]
                if active_ids:
                    for i in range(remaining):
                        idx = active_ids[(self.inflow_cursor + i) % len(active_ids)]
                        self._respawn_particle(self.particles[idx], refresh_spawn=True)
                    self.total_stream_injections += remaining
                    self.inflow_cursor = (self.inflow_cursor + remaining) % len(active_ids)
            elif remaining > 0 and self.inflow_mode == "append_new":
                # True stream growth: append new particles instead of replacing existing ones.
                specs = self._stream_specs()
                if specs and len(self.particles) < self.max_particles:
                    can_add = min(remaining, self.max_particles - len(self.particles))
                    for i in range(can_add):
                        stream_name, stream_theta = specs[(self.inflow_cursor + i) % len(specs)]
                        x, y = self._sample_edge_spawn(stream_name)
                        ttl = self._random_ttl()
                        self.particles.append(
                            Particle(
                                self.next_particle_id,
                                x,
                                y,
                                stream_theta,
                                ttl,
                                x,
                                y,
                                stream_theta,
                                True,
                                0,
                                stream_name,
                            )
                        )
                        self.next_particle_id += 1
                    self.total_stream_injections += can_add
                    self.inflow_cursor = (self.inflow_cursor + can_add) % len(specs)

        new_thetas = [p.theta for p in self.particles]
        cell_size = self.r0 if self.r0 > 0.0 else 0.0
        grid = self._build_spatial_grid(cell_size) if cell_size > 0.0 else None
        for i in range(len(self.particles)):
            if not self.particles[i].active:
                continue
            avg = self._neighbor_average_angle(i, grid=grid, cell_size=cell_size)
            aligned = self._blend_angles(self.particles[i].theta, avg, self.alignment_strength)
            noisy_target = aligned + (random.random() - 0.5) * self.noise
            # Angular inertia: keep part of previous heading to avoid abrupt turns.
            turn_alpha = 1.0 - self.turn_inertia
            new_thetas[i] = self._blend_angles(self.particles[i].theta, noisy_target, turn_alpha)

        replaced_this_step = 0
        for i, p in enumerate(self.particles):
            if not p.active:
                continue
            p.theta = new_thetas[i]
            vx, vy = p.velocity(self.v0)
            nx = p.x + vx * self.dt
            ny = p.y + vy * self.dt
            if self.respawn_on_edge and (nx <= 0.0 or nx >= self.L or ny <= 0.0 or ny >= self.L):
                self._respawn_particle(p, refresh_spawn=True)
                self.total_edge_respawns += 1
                continue
            p.x = self._apply_bounds(nx)
            p.y = self._apply_bounds(ny)
            p.ttl -= 1
            if p.ttl <= 0:
                self._respawn_particle(p, refresh_spawn=True)
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
            dx, dy = self._vector_direct(p.x - cx, p.y - cy)
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
        resume: bool = False,
    ) -> Tuple[str, str, str]:
        os.makedirs(out_dir, exist_ok=True)
        traj_path = os.path.join(out_dir, f"{prefix}_trajectory.txt")
        order_path = os.path.join(out_dir, f"{prefix}_order.txt")
        circ_path = os.path.join(out_dir, f"{prefix}_circulation.txt")
        state_path = os.path.join(out_dir, f"{prefix}_state_latest.npz")
        file_mode = "a" if resume else "w"
        t_start = self.step_count if resume else 0

        with open(traj_path, file_mode, encoding="utf-8") as ftraj, open(order_path, file_mode, encoding="utf-8") as forder, open(circ_path, file_mode, encoding="utf-8") as fcirc:
            if not resume:
                ftraj.write("# t id x y vx vy\n")
                forder.write("# t order\n")
                fcirc.write("# t circulation\n")
            for t in range(t_start, t_max + 1):
                if t % output_interval == 0:
                    order_now = self.order_parameter()
                    circ_now = self.circulation_parameter()
                    forder.write(f"{t} {order_now:.6f}\n")
                    fcirc.write(f"{t} {circ_now:.6f}\n")
                    for p in self.particles:
                        vx, vy = p.velocity(self.v0)
                        ftraj.write(f"{t} {p.id} {p.x:.6f} {p.y:.6f} {vx:.6f} {vy:.6f}\n")
                    self.save_state(state_path)
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
        self.save_state(state_path)
        return traj_path, order_path, circ_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TP2 EXTRA: Natural rotation (vortex-friendly initial conditions).")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    parser.add_argument(
        "--preset",
        choices=["none", "rotation_ccw", "rotation_cw"],
        default="none",
        help="Apply a pre-tuned parameter set",
    )
    parser.add_argument("--L", type=float, default=10.0, help="Box side length")
    parser.add_argument("--rho", type=float, default=50.0, help="Particle density")
    parser.add_argument("--r0", type=float, default=0.45, help="Interaction radius")
    parser.add_argument("--v0", type=float, default=0.025, help="Particle speed")
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
        choices=["user_combo", "cw", "ccw", "vortex_ccw", "vortex_cw"],
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
    parser.add_argument("--inflow-per-step", type=int, default=6, help="Number of stream particles reinjected each timestep")
    parser.add_argument(
        "--inflow-fraction",
        type=float,
        default=None,
        help="Fraction of active particles reinjected per timestep (overrides --inflow-per-step)",
    )
    parser.add_argument(
        "--inflow-mode",
        choices=["replace_active", "inactive_only", "append_new"],
        default="inactive_only",
        help="`inactive_only`: no replacement; `replace_active`: replace active; `append_new`: keep adding particles",
    )
    parser.add_argument("--max-particles", type=int, default=6000, help="Upper bound when --inflow-mode=append_new")
    parser.add_argument("--respawn-on-edge", action="store_true", help="Respawn particles when they hit any box edge")
    parser.add_argument(
        "--alignment-strength",
        type=float,
        default=0.35,
        help="Neighbor alignment weight in [0,1] (lower = weaker influence)",
    )
    parser.add_argument(
        "--turn-inertia",
        type=float,
        default=0.0,
        help="Angular inertia in [0,1): higher = smoother/slower turning",
    )
    parser.add_argument("--live-check", action="store_true", help="Print live rotation diagnostics while sim runs")
    parser.add_argument(
        "--live-check-interval",
        type=int,
        default=25,
        help="Timesteps between live diagnostics prints",
    )
    parser.add_argument("--resume", action="store_true", help="Resume from latest saved state for this prefix/out-dir")
    return parser.parse_args()


def apply_preset(args: argparse.Namespace) -> None:
    if args.preset == "none":
        return

    # Rotation-biased defaults tuned for visible swirl in this model.
    # Apply only when value still equals parser default, so explicit CLI args win.
    if args.feed_mode == "streams":
        args.feed_mode = "streams"
    if args.feed_pattern == "user_combo":
        args.feed_pattern = "vortex_ccw" if args.preset == "rotation_ccw" else "vortex_cw"
    if args.L == 4.0:
        args.L = 4.0
    if args.rho == 50.0:
        args.rho = 35.0
    if args.r0 == 0.45:
        args.r0 = 0.30
    if args.v0 == 0.025:
        args.v0 = 0.020
    if args.eta == 0.2:
        args.eta = 0.8
    if args.ttl_min == 260:
        args.ttl_min = 700
    if args.ttl_max == 520:
        args.ttl_max = 1200
    if args.inflow_per_step == 6:
        args.inflow_per_step = 1
    if args.alignment_strength == 0.35:
        args.alignment_strength = 0.22
    if args.chunk_size == 120:
        args.chunk_size = 20
    if args.chunk_interval == 8:
        args.chunk_interval = 12
    if args.tmax < 300:
        args.tmax = 300


def main() -> None:
    args = parse_args()
    apply_preset(args)
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
        inflow_per_step=max(0, args.inflow_per_step),
        inflow_fraction=args.inflow_fraction,
        inflow_mode=args.inflow_mode,
        max_particles=max(1, args.max_particles),
        respawn_on_edge=args.respawn_on_edge,
        alignment_strength=args.alignment_strength,
        turn_inertia=args.turn_inertia,
        dt=1.0,
        seed=args.seed,
    )
    state_path = os.path.join(args.out_dir, f"{args.prefix}_state_latest.npz")
    if args.resume:
        if not os.path.exists(state_path):
            raise FileNotFoundError(f"--resume requested but state file not found: {state_path}")
        sim.load_state(state_path)
        print(f"[ok] resumed state: {state_path} (step_count={sim.step_count})")
    traj_path, order_path, circ_path = sim.run(
        t_max=args.tmax,
        output_interval=args.output_interval,
        out_dir=args.out_dir,
        prefix=args.prefix,
        live_check=args.live_check,
        live_check_interval=max(1, args.live_check_interval),
        resume=args.resume,
    )
    print(f"[ok] trajectory: {traj_path}")
    print(f"[ok] order: {order_path}")
    print(f"[ok] circulation: {circ_path}")
    print(f"[ok] ttl reinjections: {sim.total_respawns}")
    print(f"[ok] stream injections: {sim.total_stream_injections}")
    print(f"[ok] edge respawns: {sim.total_edge_respawns}")

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
            trail_length=3,
            show_arrows=False,
        )
        print(f"[ok] animation: {args.animate_out}")


if __name__ == "__main__":
    main()
