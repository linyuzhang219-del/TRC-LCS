from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional, Tuple


@dataclass
class TRCLCSConfig:
    """Configuration for the TRC-LCS pipeline.

    The defaults are intentionally conservative and are suitable for the
    bundled synthetic demo. Real SLAM systems should tune thresholds against
    their own keyframe rate, camera, and verification backend.
    """

    visual_topk: int = 20
    task_topk: int = 20
    budget: int = 3
    min_temporal_gap: int = 30
    task_memory_threshold: float = 0.20
    high_score_threshold: float = 0.55
    low_score_threshold: float = 0.25
    redundancy_threshold: float = 0.85
    uncertainty_threshold: float = 0.65
    max_deferred: int = 200

    lambda_v: float = 0.35
    lambda_rel: float = 0.35
    lambda_u: float = 0.18
    lambda_r: float = 0.08
    lambda_c: float = 0.04

    alpha_entity: float = 0.30
    beta_attr: float = 0.15
    gamma_spatial: float = 0.25
    delta_region: float = 0.15
    eta_stage: float = 0.15

    orb_nfeatures: int = 1800
    orb_ratio: float = 0.75
    min_good_matches: int = 18
    min_inliers: int = 15
    min_inlier_ratio: float = 0.25
    use_essential_if_camera: bool = True

    # Ablation / integration switches. Geometry verification still uses ORB in
    # v0.1.0 even when the visual retrieval channel is disabled.
    enable_visual_candidates: bool = True
    enable_task_candidates: bool = True
    enable_relation_score: bool = True

    camera: Optional[Tuple[float, float, float, float]] = None  # fx fy cx cy

    def __post_init__(self) -> None:
        if self.visual_topk < 0 or self.task_topk < 0:
            raise ValueError("top-k values must be non-negative")
        if self.budget <= 0:
            raise ValueError("budget must be positive")
        if self.min_temporal_gap < 0:
            raise ValueError("min_temporal_gap must be non-negative")
        if not 0.0 < self.orb_ratio <= 1.0:
            raise ValueError("orb_ratio must be in (0, 1]")
        if not 0.0 <= self.min_inlier_ratio <= 1.0:
            raise ValueError("min_inlier_ratio must be in [0, 1]")

    def to_dict(self) -> dict:
        return asdict(self)
