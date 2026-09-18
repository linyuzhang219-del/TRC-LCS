from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from make_demo_dataset import main as _unused  # noqa: F401


TASK = "找到客厅里红色椅子旁边的包"


def run(cmd: list[str]) -> tuple[float, str]:
    start = time.perf_counter()
    proc = subprocess.run(cmd, check=True, text=True, capture_output=True)
    return time.perf_counter() - start, proc.stdout


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the reproducible TRC-LCS synthetic smoke benchmark.")
    ap.add_argument("--work-dir", default="outputs/benchmark_demo")
    ap.add_argument("--num-frames", type=int, default=80)
    args = ap.parse_args()

    root = Path(args.work_dir)
    data = root / "data"
    root.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [sys.executable, str(Path(__file__).with_name("make_demo_dataset.py")), "--out", str(data), "--num-frames", str(args.num_frames)],
        check=True,
    )

    rows = []
    for mode in ("visual", "task", "full"):
        out = root / mode
        elapsed, _ = run(
            [
                sys.executable,
                "-m",
                "trc_lcs",
                "--task",
                TASK,
                "--image-dir",
                str(data / "images"),
                "--traj",
                str(data / "trajectory_tum.txt"),
                "--semantics",
                str(data / "semantics.jsonl"),
                "--camera",
                "520",
                "520",
                "320",
                "240",
                "--out",
                str(out),
                "--mode",
                mode,
            ]
        )
        summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        rows.append(
            {
                "mode": mode,
                "num_frames": summary["num_frames"],
                "candidates_logged": summary["num_candidates_logged"],
                "verified_loops": summary["num_verified_loops"],
                "task_memory_frames": summary["num_task_memory_frames"],
                "wall_time_s": round(elapsed, 3),
            }
        )

    (root / "benchmark.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    md = [
        "# Synthetic smoke benchmark",
        "",
        "> This is a deterministic integration smoke test, not a real-world SLAM accuracy benchmark.",
        "",
        "| mode | frames | candidates | verified loops | task-memory frames | wall time (s) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        md.append(
            f"| {r['mode']} | {r['num_frames']} | {r['candidates_logged']} | {r['verified_loops']} | {r['task_memory_frames']} | {r['wall_time_s']:.3f} |"
        )
    (root / "benchmark.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
