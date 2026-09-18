from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

try:
    import cv2
except Exception as e:  # pragma: no cover
    cv2 = None

from .types import Keyframe
from .config import TRCLCSConfig


class ORBVisualIndex:
    def __init__(self, cfg: TRCLCSConfig):
        if cv2 is None:
            raise ImportError("opencv-python is required. Please run: pip install opencv-python")
        self.cfg = cfg
        self.orb = cv2.ORB_create(nfeatures=cfg.orb_nfeatures)
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        self.desc: Dict[int, np.ndarray] = {}
        self.kp_count: Dict[int, int] = {}

    def compute(self, kf: Keyframe) -> None:
        img = cv2.imread(str(kf.image_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise RuntimeError(f"Failed to read image: {kf.image_path}")
        kps, des = self.orb.detectAndCompute(img, None)
        if des is None:
            des = np.zeros((0, 32), dtype=np.uint8)
        self.desc[kf.frame_id] = des
        self.kp_count[kf.frame_id] = len(kps)
        kf.visual_kp_count = len(kps)

    def add(self, kf: Keyframe) -> None:
        if kf.frame_id not in self.desc:
            self.compute(kf)

    def _score_desc(self, des_q: np.ndarray, des_h: np.ndarray) -> tuple[float, int]:
        if des_q is None or des_h is None or len(des_q) < 8 or len(des_h) < 8:
            return 0.0, 0
        matches = self.matcher.knnMatch(des_q, des_h, k=2)
        good = []
        for pair in matches:
            if len(pair) < 2:
                continue
            m, n = pair
            if m.distance < self.cfg.orb_ratio * n.distance:
                good.append(m)
        denom = max(20, min(len(des_q), len(des_h)))
        return float(min(1.0, len(good) / denom)), len(good)

    def retrieve(self, cur: Keyframe, history: List[Keyframe], topk: int, min_temporal_gap: int) -> List[tuple[int, float, int]]:
        if cur.frame_id not in self.desc:
            self.compute(cur)
        des_q = self.desc[cur.frame_id]
        scored = []
        for h in history:
            if cur.frame_id - h.frame_id < min_temporal_gap:
                continue
            if h.frame_id not in self.desc:
                continue
            s, m = self._score_desc(des_q, self.desc[h.frame_id])
            if m > 0:
                scored.append((h.frame_id, s, m))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:topk]

    def get_desc(self, frame_id: int) -> np.ndarray | None:
        return self.desc.get(frame_id)
