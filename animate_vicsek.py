"""Create an animation from the Vicsek trajectory output.

Generates an MP4 (or GIF) showing particle velocities as arrows colored by direction.

Usage:
    python animate_vicsek.py --trajectory output/vicsek_trajectory.txt --out out.mp4

"""

import argparse
import math
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


def load_trajectory(path: str):
    # returns dict[t] -> list of (id, x, y, vx, vy)
    data = defaultdict(list)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split()
            if len(parts) < 6:
                continue
            t = int(parts[0])
            pid = int(parts[1])
            x = float(parts[2])
            y = float(parts[3])
            vx = float(parts[4])
            vy = float(parts[5])
            data[t].append((pid, x, y, vx, vy))
    # return ordered times
    times = sorted(data.keys())
    return times, data


def make_animation(
    times,
    data,
    box_size: float,
    leader_id: int,
    out_path: str,
    arrow_length: float,
    fps: int = 10,
    dpi: int = 120,
):
    print(f"Times: {len(times)}, Particles in first frame: {len(data[times[0]]) if times else 0}")
    if not times or not data[times[0]]:
        print("Error: No particle data in trajectory.")
        return
    # Prepare figure
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, box_size)
    ax.set_ylim(0, box_size)
    ax.set_aspect("equal")
    ax.set_title("Vicsek model")
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    # Initial frame
    first = data[times[0]]
    xs = np.array([p[1] for p in first])
    ys = np.array([p[2] for p in first])
    vxs = np.array([p[3] for p in first])
    vys = np.array([p[4] for p in first])
    speeds = np.hypot(vxs, vys)
    safe_speeds = np.where(speeds > 0, speeds, 1.0)
    dir_x = vxs / safe_speeds
    dir_y = vys / safe_speeds
    angles = np.arctan2(vys, vxs)
    colors = (angles + math.pi) / (2 * math.pi)  # normalized 0..1

    # Scatter for all particles, colored by direction
    particle_scatter = ax.scatter(xs, ys, c=colors, cmap="hsv", s=10, alpha=0.7, label="particles")
    quiv = ax.quiver(
        xs,
        ys,
        dir_x,
        dir_y,
        colors,
        cmap="hsv",
        angles="xy",
        scale_units="xy",
        scale=1.0 / arrow_length,
        width=0.004,
    )
    # Leader highlight (if present)
    if leader_id >= 0:
        leader_mask = np.array([p[0] == leader_id for p in first])
        leader_scatter = ax.scatter(
            xs[leader_mask], ys[leader_mask], c="red", s=50, label="leader"
        )
        ax.legend(loc="upper right")
    else:
        # Dummy empty scatter for consistency
        leader_scatter = ax.scatter([], [], c="red", s=50, label="leader")
        ax.legend(loc="upper right")

    def update(frame_idx, quiv, particle_scatter, leader_scatter, data, times, ax, leader_id):
        t = times[frame_idx]
        pts = data[t]
        xs = np.array([p[1] for p in pts])
        ys = np.array([p[2] for p in pts])
        vxs = np.array([p[3] for p in pts])
        vys = np.array([p[4] for p in pts])
        speeds = np.hypot(vxs, vys)
        safe_speeds = np.where(speeds > 0, speeds, 1.0)
        dir_x = vxs / safe_speeds
        dir_y = vys / safe_speeds
        angles = np.arctan2(vys, vxs)
        colors = (angles + math.pi) / (2 * math.pi)
        quiv.set_UVC(dir_x, dir_y)
        quiv.set_offsets(np.column_stack([xs, ys]))
        quiv.set_array(colors)
        particle_scatter.set_offsets(np.column_stack([xs, ys]))
        particle_scatter.set_array(colors)  # Update colors
        if leader_id >= 0:
            leader_mask = np.array([p[0] == leader_id for p in pts])
            leader_scatter.set_offsets(np.column_stack([xs[leader_mask], ys[leader_mask]]))
        else:
            leader_scatter.set_offsets(np.empty((0, 2)))
        ax.set_title(f"Vicsek model (t={t})")
        return quiv, leader_scatter, particle_scatter

    anim = animation.FuncAnimation(fig, update, frames=len(times), interval=100, blit=False, fargs=(quiv, particle_scatter, leader_scatter, data, times, ax, leader_id))

    if out_path.lower().endswith(".gif"):
        writer = animation.PillowWriter(fps=fps)
        anim.save(out_path, writer=writer, dpi=dpi)
    else:
        # mp4 fallback
        writer = animation.FFMpegWriter(fps=fps)
        anim.save(out_path, writer=writer, dpi=dpi)


def main():
    parser = argparse.ArgumentParser(description="Animate Vicsek trajectory output.")
    parser.add_argument("--trajectory", required=True, help="Path to trajectory file")
    parser.add_argument("--out", required=True, help="Output animation path (mp4 or gif)")
    parser.add_argument("--box", type=float, default=10.0, help="Box side length")
    parser.add_argument("--leader-id", type=int, default=-1, help="Leader particle ID (-1 for no leader)")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second")
    parser.add_argument(
        "--arrow-length",
        type=float,
        default=0.25,
        help="Arrow length in plot units (use larger values if arrows look too small)",
    )
    args = parser.parse_args()

    times, data = load_trajectory(args.trajectory)
    if not times:
        print(f"Error: No data found in {args.trajectory}. Run the simulation first.")
        return
    make_animation(
        times,
        data,
        box_size=args.box,
        leader_id=args.leader_id,
        out_path=args.out,
        arrow_length=args.arrow_length,
        fps=args.fps,
    )


if __name__ == "__main__":
    main()
