from __future__ import annotations

from typing import Optional, Tuple
import numpy as np

try:
    import cv2
except Exception as e:  # pragma: no cover
    cv2 = None

from .config import TRCLCSConfig
from .types import Keyframe, LoopCandidate
from .features import ORBVisualIndex


class GeometricVerifier:
    def __init__(self, cfg: TRCLCSConfig, visual_index: ORBVisualIndex):
        if cv2 is None:
            raise ImportError("opencv-python is required. Please run: pip install opencv-python")
        self.cfg = cfg
        self.visual_index = visual_index
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        if cfg.camera is not None:
            fx, fy, cx, cy = cfg.camera
            self.K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float64)
        else:
            self.K = None

    def _load_gray(self, kf: Keyframe):
        img = cv2.imread(str(kf.image_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise RuntimeError(f"Failed to read image: {kf.image_path}")
        return img

    def _detect(self, kf: Keyframe):
        img = self._load_gray(kf)
        kps, des = self.visual_index.orb.detectAndCompute(img, None)
        if des is None:
            des = np.zeros((0, 32), dtype=np.uint8)
        return kps, des

    def verify(self, cur: Keyframe, hist: Keyframe, cand: LoopCandidate) -> LoopCandidate:
        kp1, des1 = self._detect(cur)
        kp2, des2 = self._detect(hist)
        if len(des1) < 8 or len(des2) < 8:
            cand.verified = False
            cand.reason = "too_few_features"
            return cand

        matches_knn = self.matcher.knnMatch(des1, des2, k=2)
        good = []
        for pair in matches_knn:
            if len(pair) < 2:
                continue
            m, n = pair
            if m.distance < self.cfg.orb_ratio * n.distance:
                good.append(m)
        cand.matches = len(good)
        if len(good) < self.cfg.min_good_matches:
            cand.verified = False
            cand.reason = "too_few_good_matches"
            return cand

        pts1 = np.float32([kp1[m.queryIdx].pt for m in good])
        pts2 = np.float32([kp2[m.trainIdx].pt for m in good])

        if self.K is not None and self.cfg.use_essential_if_camera:
            E, mask = cv2.findEssentialMat(
                pts1,
                pts2,
                self.K,
                method=cv2.RANSAC,
                prob=0.999,
                threshold=1.5,
            )
        else:
            H, mask = cv2.findHomography(pts1, pts2, cv2.RANSAC, 3.0)

        if mask is None:
            cand.verified = False
            cand.reason = "ransac_failed"
            return cand

        inliers = int(mask.ravel().sum())
        cand.inliers = inliers
        ratio = inliers / max(1, len(good))
        if inliers >= self.cfg.min_inliers and ratio >= self.cfg.min_inlier_ratio:
            cand.verified = True
            cand.reason = "verified"
        else:
            cand.verified = False
            cand.reason = f"low_inliers:{inliers}/{len(good)}"
        return cand
