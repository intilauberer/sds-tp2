"""Plot order parameter (polarization) vs time from Vicsek simulation output."""

import argparse

import matplotlib.pyplot as plt


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot order parameter vs time.")
    parser.add_argument("--order-file", required=True, help="Path to the order file (vicsek_order.txt)")
    parser.add_argument("--output", default=None, help="Optional output image file")
    args = parser.parse_args()

    t = []
    order = []
    with open(args.order_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            t.append(int(parts[0]))
            order.append(float(parts[1]))

    plt.figure(figsize=(8, 4))
    plt.plot(t, order, marker=".")
    plt.xlabel("time")
    plt.ylabel("order parameter")
    plt.grid(True)
    plt.tight_layout()
    if args.output:
        plt.savefig(args.output, dpi=200)
    else:
        plt.show()


if __name__ == "__main__":
    main()
