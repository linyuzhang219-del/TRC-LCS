from __future__ import annotations

from typing import Dict, List
import numpy as np

from .config import TRCLCSConfig
from .types import Keyframe, LoopCandidate, TaskGraph
from .csr import relation_similarity_components
from .memory import TaskMemory


def pose_distance(a: Keyframe, b: Keyframe) -> float:
    if a.pose_tum is None or b.pose_tum is None:
        return 0.0
    pa = a.pose_tum[:3]
    pb = b.pose_tum[:3]
    return float(np.linalg.norm(pa - pb))


def estimate_localization_gain(cur: Keyframe, hist: Keyframe, frames_since_last_loop: int) -> float:
    """Estimate potential loop-closure utility when covariance is unavailable."""
    drift_term = min(1.0, frames_since_last_loop / 120.0)
    dist = pose_distance(cur, hist)
    dist_term = min(1.0, dist / 30.0) if dist > 0 else 0.25 * drift_term
    rel_term = 0.5 * (cur.task_relevance + hist.task_relevance)
    return float(0.45 * drift_term + 0.35 * dist_term + 0.20 * rel_term)


def estimate_redundancy(cur: Keyframe, hist: Keyframe, cfg: TRCLCSConfig, memory: TaskMemory) -> float:
    gap = max(1, cur.frame_id - hist.frame_id)
    temporal = max(0.0, 1.0 - gap / max(1, cfg.min_temporal_gap))
    fail = min(1.0, memory.fail_count(cur.frame_id, hist.frame_id) / 3.0)
    return float(0.70 * temporal + 0.30 * fail)


def estimate_cost(cur: Keyframe, hist: Keyframe) -> float:
    """Lightweight proxy for geometric verification cost."""
    kp = max(cur.visual_kp_count, hist.visual_kp_count, 1)
    return float(min(1.0, kp / 2500.0))


def relation_similarity(cur: Keyframe, hist: Keyframe, task: TaskGraph, cfg: TRCLCSConfig) -> float:
    comps = relation_similarity_components(cur, hist, task)
    weighted = (
        cfg.alpha_entity * comps["entity"]
        + cfg.beta_attr * comps["attr"]
        + cfg.gamma_spatial * comps["spatial"]
        + cfg.delta_region * comps["region"]
        + cfg.eta_stage * comps["stage"]
    )
    return float(0.75 * weighted + 0.25 * comps["csr"])


def compute_candidate_score(
    cand: LoopCandidate,
    cur: Keyframe,
    hist: Keyframe,
    task: TaskGraph,
    cfg: TRCLCSConfig,
    memory: TaskMemory,
    frames_since_last_loop: int,
) -> LoopCandidate:
    cand.rel_score = relation_similarity(cur, hist, task, cfg) if cfg.enable_relation_score else 0.0
    cand.loc_gain = estimate_localization_gain(cur, hist, frames_since_last_loop)
    cand.redundancy = estimate_redundancy(cur, hist, cfg, memory)
    cand.cost = estimate_cost(cur, hist)
    cand.total_score = float(
        cfg.lambda_v * cand.visual_score
        + cfg.lambda_rel * cand.rel_score
        + cfg.lambda_u * cand.loc_gain
        - cfg.lambda_r * cand.redundancy
        - cfg.lambda_c * cand.cost
    )
    return cand


class CandidateScheduler:
    def __init__(self, cfg: TRCLCSConfig):
        self.cfg = cfg
        self.deferred: List[LoopCandidate] = []

    def schedule(self, candidates: List[LoopCandidate], uncertainty: float) -> List[LoopCandidate]:
        immediate: List[LoopCandidate] = []
        deferred_new: List[LoopCandidate] = []

        for c in candidates:
            if c.redundancy >= self.cfg.redundancy_threshold:
                c.schedule = "suppressed"
                c.reason = "high_redundancy"
            elif c.total_score >= self.cfg.high_score_threshold:
                c.schedule = "immediate"
                immediate.append(c)
            elif c.total_score >= self.cfg.low_score_threshold:
                c.schedule = "deferred"
                deferred_new.append(c)
            else:
                c.schedule = "suppressed"
                c.reason = "low_score"

        self.deferred.extend(deferred_new)
        self.deferred = sorted(self.deferred, key=lambda x: x.total_score, reverse=True)[: self.cfg.max_deferred]

        reactivated: List[LoopCandidate] = []
        if uncertainty >= self.cfg.uncertainty_threshold and self.deferred:
            n = min(self.cfg.budget, len(self.deferred))
            reactivated = self.deferred[:n]
            for c in reactivated:
                c.schedule = "safety_reactivated"
                c.reason = "high_uncertainty"
            self.deferred = self.deferred[n:]

        selected = immediate + reactivated
        selected = sorted(selected, key=lambda x: x.total_score, reverse=True)[: self.cfg.budget]
        for c in selected:
            if c.schedule not in {"safety_reactivated", "immediate"}:
                c.schedule = "immediate"
        return selected


def merge_candidates(
    visual: List[tuple[int, float, int]],
    task: List[tuple[int, float]],
    cur_id: int,
) -> List[LoopCandidate]:
    merged: Dict[int, LoopCandidate] = {}
    for fid, score, matches in visual:
        merged[fid] = LoopCandidate(
            cur_id=cur_id,
            hist_id=fid,
            source="visual",
            visual_score=float(score),
            matches=int(matches),
        )
    for fid, score in task:
        if fid in merged:
            merged[fid].source = "visual+task"
            merged[fid].visual_score = max(merged[fid].visual_score, 0.25 * score)
        else:
            # A small proxy score keeps task-only candidates comparable while
            # relation similarity remains the main task-conditioned signal.
            merged[fid] = LoopCandidate(
                cur_id=cur_id,
                hist_id=fid,
                source="task",
                visual_score=0.25 * float(score),
            )
    return list(merged.values())
