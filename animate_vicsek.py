"""Create an animation from the Vicsek trajectory output.

Generates an MP4 (or GIF) showing particle velocities as arrows colored by direction.

Usage:
    python animate_vicsek.py --trajectory output/vicsek_trajectory.txt --out out.mp4

"""

import argparse
import math
from collections import deque
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.collections import LineCollection


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
    trail_length: int = 0,
    show_arrows: bool = True,
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
    particle_kwargs = {"c": colors, "cmap": "hsv", "s": 10, "alpha": 0.7}
    if leader_id >= 0:
        particle_kwargs["label"] = "particles"
    particle_scatter = ax.scatter(xs, ys, **particle_kwargs)
    quiv = None
    if show_arrows:
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
    trail_coll = None
    trails = {}
    if trail_length > 1:
        for p in first:
            pid = p[0]
            trails[pid] = deque(maxlen=trail_length)
            if 0.0 <= p[1] <= box_size and 0.0 <= p[2] <= box_size:
                trails[pid].append((p[1], p[2]))
        trail_coll = LineCollection([], colors="#66d9ff", linewidths=0.8, alpha=0.6)
        ax.add_collection(trail_coll)
    # Leader highlight (if present)
    if leader_id >= 0:
        leader_mask = np.array([p[0] == leader_id for p in first])
        leader_scatter = ax.scatter(
            xs[leader_mask], ys[leader_mask], c="red", s=50, label="leader"
        )
        ax.legend(loc="upper right")
    else:
        # Dummy empty scatter for consistency
        leader_scatter = ax.scatter([], [], c="red", s=50)

    def update(frame_idx, quiv, particle_scatter, leader_scatter, trail_coll, trails, data, times, ax, leader_id):
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
        if quiv is not None:
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
        if trail_coll is not None:
            for p in pts:
                pid = p[0]
                if pid not in trails:
                    trails[pid] = deque(maxlen=max(2, trail_length))
                x, y = p[1], p[2]
                # Ignore placeholders/out-of-bounds points.
                if not (0.0 <= x <= box_size and 0.0 <= y <= box_size):
                    trails[pid].clear()
                    continue
                # Break contrail on teleports (respawn/reinjection) to avoid screen-crossing artifacts.
                if len(trails[pid]) > 0:
                    x0, y0 = trails[pid][-1]
                    if abs(x - x0) > box_size * 0.25 or abs(y - y0) > box_size * 0.25:
                        trails[pid].clear()
                trails[pid].append((x, y))
            segs = []
            for tr in trails.values():
                if len(tr) < 2:
                    continue
                for i in range(1, len(tr)):
                    x0, y0 = tr[i - 1]
                    x1, y1 = tr[i]
                    if abs(x1 - x0) > box_size / 2.0 or abs(y1 - y0) > box_size / 2.0:
                        continue
                    segs.append([(x0, y0), (x1, y1)])
            trail_coll.set_segments(segs)
        ax.set_title(f"Vicsek model (t={t})")
        artists = [leader_scatter, particle_scatter]
        if quiv is not None:
            artists.append(quiv)
        if trail_coll is not None:
            artists.append(trail_coll)
        return tuple(artists)

    anim = animation.FuncAnimation(
        fig,
        update,
        frames=len(times),
        interval=100,
        blit=False,
        fargs=(quiv, particle_scatter, leader_scatter, trail_coll, trails, data, times, ax, leader_id),
    )

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
    parser.add_argument("--trail-length", type=int, default=0, help="Particle trail length in frames (0 disables trails)")
    parser.add_argument("--no-arrows", action="store_true", help="Disable velocity arrows")
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
        trail_length=max(0, args.trail_length),
        show_arrows=(not args.no_arrows),
    )


if __name__ == "__main__":
    main()
