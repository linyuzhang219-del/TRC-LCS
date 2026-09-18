from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np


@dataclass
class TaskGraph:
    raw_task: str
    target_objects: List[str]
    reference_objects: List[str]
    target_regions: List[str]
    relations: List[Tuple[str, str, str]]
    stages: List[str]


@dataclass
class ObjectObs:
    label: str
    attrs: List[str] = field(default_factory=list)
    bbox: Optional[List[float]] = None  # x,y,w,h
    xyz: Optional[List[float]] = None
    score: float = 1.0


@dataclass
class RelationObs:
    subj: str
    rel: str
    obj: str


@dataclass
class SemanticObs:
    frame_id: int
    image: Optional[str] = None
    region: Optional[str] = None
    objects: List[ObjectObs] = field(default_factory=list)
    relations: List[RelationObs] = field(default_factory=list)


@dataclass
class Keyframe:
    frame_id: int
    image_path: Path
    timestamp: float
    pose_tum: Optional[np.ndarray] = None  # tx ty tz qx qy qz qw
    semantic: Optional[SemanticObs] = None
    task_relevance: float = 0.0
    csr: Optional[np.ndarray] = None
    visual_kp_count: int = 0


@dataclass
class LoopCandidate:
    cur_id: int
    hist_id: int
    source: str
    visual_score: float = 0.0
    rel_score: float = 0.0
    loc_gain: float = 0.0
    redundancy: float = 0.0
    cost: float = 0.0
    total_score: float = 0.0
    schedule: str = "unknown"
    verified: bool = False
    inliers: int = 0
    matches: int = 0
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
