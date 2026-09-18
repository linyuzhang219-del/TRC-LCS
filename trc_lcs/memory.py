from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .types import Keyframe, TaskGraph
from .csr import cosine, relation_similarity_components


class TaskMemory:
    def __init__(self):
        self.frames: Dict[int, Keyframe] = {}
        self.positive_pairs: List[dict] = []
        self.negative_counts: Dict[str, int] = {}

    def add_frame(self, kf: Keyframe) -> None:
        self.frames[kf.frame_id] = kf

    def record_positive(self, cur_id: int, hist_id: int, inliers: int, score: float) -> None:
        self.positive_pairs.append({
            "cur_id": cur_id,
            "hist_id": hist_id,
            "inliers": int(inliers),
            "score": float(score),
        })

    def record_negative(self, cur_id: int, hist_id: int) -> None:
        key = self._pair_key(cur_id, hist_id)
        self.negative_counts[key] = self.negative_counts.get(key, 0) + 1

    def fail_count(self, cur_id: int, hist_id: int) -> int:
        return self.negative_counts.get(self._pair_key(cur_id, hist_id), 0)

    @staticmethod
    def _pair_key(a: int, b: int) -> str:
        x, y = sorted([int(a), int(b)])
        return f"{x}:{y}"

    def retrieve_task_candidates(self, cur: Keyframe, task: TaskGraph, topk: int, min_temporal_gap: int) -> List[tuple[int, float]]:
        scored = []
        for fid, hist in self.frames.items():
            if cur.frame_id <= fid or cur.frame_id - fid < min_temporal_gap:
                continue
            comps = relation_similarity_components(cur, hist, task)
            s = 0.5 * comps["csr"] + 0.2 * comps["entity"] + 0.15 * comps["spatial"] + 0.15 * comps["region"]
            if s > 0:
                scored.append((fid, float(s)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:topk]

    def save(self, path: str | Path) -> None:
        path = Path(path)
        data = {
            "frames": [
                {
                    "frame_id": k.frame_id,
                    "image_path": str(k.image_path),
                    "task_relevance": k.task_relevance,
                    "timestamp": k.timestamp,
                }
                for k in self.frames.values()
            ],
            "positive_pairs": self.positive_pairs,
            "negative_counts": self.negative_counts,
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
