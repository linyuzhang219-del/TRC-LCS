from __future__ import annotations

import argparse
import json
from typing import Sequence

from . import __version__
from .config import TRCLCSConfig
from .io import build_keyframes
from .pipeline import TRCLCSPipeline


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="trc-lcs",
        description="Task-Relation Conditioned Loop Closure Scheduling for SLAM.",
    )
    p.add_argument("--version", action="version", version=f"TRC-LCS {__version__}")
    p.add_argument("--task", required=True, help="Natural-language task")
    p.add_argument("--image-dir", required=True, help="Directory containing ordered keyframe images")
    p.add_argument("--traj", default=None, help="Optional TUM trajectory: timestamp tx ty tz qx qy qz qw")
    p.add_argument("--semantics", default=None, help="Optional JSONL semantic observations")
    p.add_argument("--out", required=True, help="Output directory")

    p.add_argument("--camera", nargs=4, type=float, default=None, metavar=("fx", "fy", "cx", "cy"))
    p.add_argument("--budget", type=int, default=3)
    p.add_argument("--visual-topk", type=int, default=20)
    p.add_argument("--task-topk", type=int, default=20)
    p.add_argument("--min-temporal-gap", type=int, default=30)
    p.add_argument("--task-memory-threshold", type=float, default=0.20)
    p.add_argument("--high-score-threshold", type=float, default=0.55)
    p.add_argument("--low-score-threshold", type=float, default=0.25)
    p.add_argument("--min-good-matches", type=int, default=18)
    p.add_argument("--min-inliers", type=int, default=15)
    p.add_argument("--min-inlier-ratio", type=float, default=0.25)
    p.add_argument(
        "--mode",
        choices=("full", "visual", "task"),
        default="full",
        help="Ablation mode: full, visual-only retrieval/scoring, or task-conditioned retrieval/scoring.",
    )
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    mode_flags = {
        "full": (True, True, True),
        "visual": (True, False, False),
        "task": (False, True, True),
    }
    enable_visual, enable_task, enable_rel = mode_flags[args.mode]

    cfg = TRCLCSConfig(
        camera=tuple(args.camera) if args.camera is not None else None,
        budget=args.budget,
        visual_topk=args.visual_topk,
        task_topk=args.task_topk,
        min_temporal_gap=args.min_temporal_gap,
        task_memory_threshold=args.task_memory_threshold,
        high_score_threshold=args.high_score_threshold,
        low_score_threshold=args.low_score_threshold,
        min_good_matches=args.min_good_matches,
        min_inliers=args.min_inliers,
        min_inlier_ratio=args.min_inlier_ratio,
        enable_visual_candidates=enable_visual,
        enable_task_candidates=enable_task,
        enable_relation_score=enable_rel,
    )
    keyframes = build_keyframes(args.image_dir, args.traj, args.semantics)
    runner = TRCLCSPipeline(task_text=args.task, cfg=cfg, out_dir=args.out)
    summary = runner.process(keyframes)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0
