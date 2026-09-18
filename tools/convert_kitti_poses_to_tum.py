from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np


def rotation_matrix_to_quaternion(R: np.ndarray) -> tuple[float, float, float, float]:
    """Convert a 3x3 rotation matrix to (qx, qy, qz, qw)."""
    trace = float(np.trace(R))
    if trace > 0.0:
        s = (trace + 1.0) ** 0.5 * 2.0
        qw = 0.25 * s
        qx = (R[2, 1] - R[1, 2]) / s
        qy = (R[0, 2] - R[2, 0]) / s
        qz = (R[1, 0] - R[0, 1]) / s
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = (1.0 + R[0, 0] - R[1, 1] - R[2, 2]) ** 0.5 * 2.0
        qw = (R[2, 1] - R[1, 2]) / s
        qx = 0.25 * s
        qy = (R[0, 1] + R[1, 0]) / s
        qz = (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] > R[2, 2]:
        s = (1.0 + R[1, 1] - R[0, 0] - R[2, 2]) ** 0.5 * 2.0
        qw = (R[0, 2] - R[2, 0]) / s
        qx = (R[0, 1] + R[1, 0]) / s
        qy = 0.25 * s
        qz = (R[1, 2] + R[2, 1]) / s
    else:
        s = (1.0 + R[2, 2] - R[0, 0] - R[1, 1]) ** 0.5 * 2.0
        qw = (R[1, 0] - R[0, 1]) / s
        qx = (R[0, 2] + R[2, 0]) / s
        qy = (R[1, 2] + R[2, 1]) / s
        qz = 0.25 * s
    q = np.asarray([qx, qy, qz, qw], dtype=np.float64)
    q /= max(float(np.linalg.norm(q)), 1e-12)
    return tuple(float(v) for v in q)


def main() -> None:
    ap = argparse.ArgumentParser(description="Convert KITTI 3x4 poses into row-aligned TUM pose format.")
    ap.add_argument("--poses", required=True, help="KITTI poses file, one flattened 3x4 matrix per row")
    ap.add_argument("--times", default=None, help="Optional KITTI times file")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    pose_lines = [x.strip() for x in Path(args.poses).read_text().splitlines() if x.strip()]
    times = None
    if args.times:
        times = [float(x.strip()) for x in Path(args.times).read_text().splitlines() if x.strip()]
        if len(times) != len(pose_lines):
            raise ValueError("times and poses must contain the same number of rows")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for i, line in enumerate(pose_lines):
            vals = np.asarray([float(x) for x in line.split()], dtype=np.float64)
            if vals.size != 12:
                raise ValueError(f"pose row {i} does not contain 12 values")
            T = vals.reshape(3, 4)
            t = T[:, 3]
            qx, qy, qz, qw = rotation_matrix_to_quaternion(T[:, :3])
            ts = times[i] if times is not None else float(i)
            f.write(f"{ts:.9f} {t[0]:.9f} {t[1]:.9f} {t[2]:.9f} {qx:.9f} {qy:.9f} {qz:.9f} {qw:.9f}\n")

    print(f"Wrote {len(pose_lines)} poses to {out}")


if __name__ == "__main__":
    main()
