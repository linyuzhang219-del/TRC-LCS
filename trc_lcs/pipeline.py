from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List

from tqdm import tqdm

from . import __version__
from .config import TRCLCSConfig
from .types import Keyframe, LoopCandidate
from .task_parser import parse_task
from .semantic import task_relevance, infer_simple_relations
from .csr import CSREncoder
from .features import ORBVisualIndex
from .memory import TaskMemory
from .scoring import CandidateScheduler, compute_candidate_score, merge_candidates
from .verify import GeometricVerifier


class TRCLCSPipeline:
    def __init__(self, task_text: str, cfg: TRCLCSConfig, out_dir: str | Path):
        self.task = parse_task(task_text)
        self.cfg = cfg
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self.csr = CSREncoder(dim=128)
        self.memory = TaskMemory()
        self.visual = ORBVisualIndex(cfg)
        self.verifier = GeometricVerifier(cfg, self.visual)
        self.scheduler = CandidateScheduler(cfg)

        self.history: List[Keyframe] = []
        self.loop_constraints: List[dict] = []
        self.all_candidates: List[LoopCandidate] = []
        self.frames_since_last_loop = 999

    def _uncertainty(self, cur: Keyframe) -> float:
        # Lightweight surrogate when a SLAM covariance is unavailable.
        return min(1.0, self.frames_since_last_loop / 150.0)

    def process(self, keyframes: List[Keyframe]) -> dict:
        for kf in tqdm(keyframes, desc="TRC-LCS"):
            if kf.semantic is not None:
                infer_simple_relations(kf.semantic)
            kf.task_relevance = task_relevance(kf, self.task)
            kf.csr = self.csr.encode(kf, self.task)

            # ORB descriptors are used by v0.1.0 geometric verification even
            # if the visual retrieval channel is disabled for an ablation.
            self.visual.add(kf)

            if kf.task_relevance >= self.cfg.task_memory_threshold:
                self.memory.add_frame(kf)

            if len(self.history) < self.cfg.min_temporal_gap:
                self.history.append(kf)
                self.frames_since_last_loop += 1
                continue

            visual_cands = []
            if self.cfg.enable_visual_candidates:
                visual_cands = self.visual.retrieve(
                    cur=kf,
                    history=self.history,
                    topk=self.cfg.visual_topk,
                    min_temporal_gap=self.cfg.min_temporal_gap,
                )

            task_cands = []
            if self.cfg.enable_task_candidates:
                task_cands = self.memory.retrieve_task_candidates(
                    cur=kf,
                    task=self.task,
                    topk=self.cfg.task_topk,
                    min_temporal_gap=self.cfg.min_temporal_gap,
                )

            candidates = merge_candidates(visual_cands, task_cands, cur_id=kf.frame_id)
            hist_by_id = {h.frame_id: h for h in self.history}
            scored: List[LoopCandidate] = []
            for c in candidates:
                hist = hist_by_id.get(c.hist_id) or self.memory.frames.get(c.hist_id)
                if hist is None:
                    continue
                scored.append(
                    compute_candidate_score(
                        cand=c,
                        cur=kf,
                        hist=hist,
                        task=self.task,
                        cfg=self.cfg,
                        memory=self.memory,
                        frames_since_last_loop=self.frames_since_last_loop,
                    )
                )

            selected = self.scheduler.schedule(scored, uncertainty=self._uncertainty(kf))

            verified_any = False
            for c in selected:
                hist = hist_by_id.get(c.hist_id) or self.memory.frames.get(c.hist_id)
                if hist is None:
                    continue
                c = self.verifier.verify(kf, hist, c)
                if c.verified:
                    verified_any = True
                    self.loop_constraints.append(
                        {
                            "cur_id": c.cur_id,
                            "hist_id": c.hist_id,
                            "score": c.total_score,
                            "source": c.source,
                            "inliers": c.inliers,
                            "matches": c.matches,
                            "timestamp_cur": kf.timestamp,
                            "timestamp_hist": hist.timestamp,
                        }
                    )
                    self.memory.record_positive(c.cur_id, c.hist_id, c.inliers, c.total_score)
                else:
                    self.memory.record_negative(c.cur_id, c.hist_id)
                self.all_candidates.append(c)

            selected_keys = {(c.cur_id, c.hist_id) for c in selected}
            for c in scored:
                if (c.cur_id, c.hist_id) not in selected_keys:
                    self.all_candidates.append(c)

            self.history.append(kf)
            self.frames_since_last_loop = 0 if verified_any else self.frames_since_last_loop + 1

        return self._save_outputs(len(keyframes))

    def _save_outputs(self, num_frames: int) -> dict:
        cand_path = self.out_dir / "candidate_scores.csv"
        with cand_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "cur_id",
                    "hist_id",
                    "source",
                    "visual_score",
                    "rel_score",
                    "loc_gain",
                    "redundancy",
                    "cost",
                    "total_score",
                    "schedule",
                    "verified",
                    "inliers",
                    "matches",
                    "reason",
                ],
            )
            writer.writeheader()
            for c in self.all_candidates:
                writer.writerow(c.to_dict())

        loops_path = self.out_dir / "loop_constraints.jsonl"
        with loops_path.open("w", encoding="utf-8") as f:
            for item in self.loop_constraints:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        memory_path = self.out_dir / "task_memory.json"
        self.memory.save(memory_path)

        summary = {
            "trc_lcs_version": __version__,
            "task": self.task.raw_task,
            "task_graph": {
                "target_objects": self.task.target_objects,
                "reference_objects": self.task.reference_objects,
                "target_regions": self.task.target_regions,
                "relations": self.task.relations,
                "stages": self.task.stages,
            },
            "config": self.cfg.to_dict(),
            "num_frames": num_frames,
            "num_candidates_logged": len(self.all_candidates),
            "num_verified_loops": len(self.loop_constraints),
            "num_task_memory_frames": len(self.memory.frames),
            "outputs": {
                "candidate_scores": str(cand_path),
                "loop_constraints": str(loops_path),
                "task_memory": str(memory_path),
            },
        }
        summary_path = self.out_dir / "summary.json"
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        return summary
