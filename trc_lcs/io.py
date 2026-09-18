from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np

from .types import Keyframe, SemanticObs, ObjectObs, RelationObs

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}


def list_images(image_dir: str | Path) -> List[Path]:
    p = Path(image_dir)
    if not p.exists():
        raise FileNotFoundError(f"image_dir not found: {p}")
    images = sorted([x for x in p.iterdir() if x.suffix.lower() in IMAGE_EXTS])
    if not images:
        raise RuntimeError(f"No images found under {p}")
    return images


def load_tum_trajectory(path: Optional[str | Path]) -> Dict[int, tuple[float, np.ndarray]]:
    """Return frame index -> (timestamp, pose[7]).

    The code assumes trajectory rows are aligned with sorted images. If your timestamps differ,
    adapt this function to map image timestamp to trajectory timestamp.
    """
    if path is None:
        return {}
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"trajectory not found: {path}")
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 8:
                continue
            vals = [float(x) for x in parts[:8]]
            rows.append(vals)
    traj: Dict[int, tuple[float, np.ndarray]] = {}
    for i, vals in enumerate(rows):
        traj[i] = (vals[0], np.asarray(vals[1:8], dtype=np.float64))
    return traj


def load_semantics_jsonl(path: Optional[str | Path]) -> Dict[int, SemanticObs]:
    if path is None:
        return {}
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"semantics not found: {path}")
    sems: Dict[int, SemanticObs] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            frame_id = int(item.get("frame_id", len(sems)))
            objects = []
            for obj in item.get("objects", []):
                objects.append(ObjectObs(
                    label=str(obj.get("label", "unknown")).lower(),
                    attrs=[str(a).lower() for a in obj.get("attrs", [])],
                    bbox=obj.get("bbox"),
                    xyz=obj.get("xyz"),
                    score=float(obj.get("score", 1.0)),
                ))
            relations = []
            for rel in item.get("relations", []):
                relations.append(RelationObs(
                    subj=str(rel.get("subj", "")).lower(),
                    rel=str(rel.get("rel", "")).lower(),
                    obj=str(rel.get("obj", "")).lower(),
                ))
            sems[frame_id] = SemanticObs(
                frame_id=frame_id,
                image=item.get("image"),
                region=(str(item["region"]).lower() if item.get("region") is not None else None),
                objects=objects,
                relations=relations,
            )
    return sems


def build_keyframes(image_dir: str | Path, traj_path: Optional[str | Path], sem_path: Optional[str | Path]) -> List[Keyframe]:
    images = list_images(image_dir)
    traj = load_tum_trajectory(traj_path)
    sems = load_semantics_jsonl(sem_path)
    keyframes = []
    for idx, img in enumerate(images):
        timestamp, pose = traj.get(idx, (float(idx), None))
        sem = sems.get(idx)
        keyframes.append(Keyframe(
            frame_id=idx,
            image_path=img,
            timestamp=timestamp,
            pose_tum=pose,
            semantic=sem,
        ))
    return keyframes
