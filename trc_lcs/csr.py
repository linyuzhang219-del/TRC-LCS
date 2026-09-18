from __future__ import annotations

import hashlib
from typing import Iterable, List, Tuple
import numpy as np

from .types import Keyframe, TaskGraph, SemanticObs
from .semantic import label_match


def _hash_index(token: str, dim: int) -> int:
    h = hashlib.md5(token.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % dim


def _add_token(vec: np.ndarray, token: str, weight: float = 1.0, prefix: str = "") -> None:
    token = (prefix + str(token).strip().lower())
    if not token:
        return
    vec[_hash_index(token, len(vec))] += weight


def _normalize(vec: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(vec)
    if n < 1e-9:
        return vec
    return vec / n


def extract_task_relevant_semantic(sem: SemanticObs | None, task: TaskGraph) -> SemanticObs | None:
    if sem is None:
        return None
    task_entities = task.target_objects + task.reference_objects
    keep_objects = []
    for o in sem.objects:
        if any(label_match(o.label, q) or any(label_match(a, q) for a in o.attrs) for q in task_entities):
            keep_objects.append(o)
    keep_relations = []
    keep_labels = {o.label for o in keep_objects}
    for r in sem.relations:
        if r.subj in keep_labels or r.obj in keep_labels:
            keep_relations.append(r)
        else:
            for qs, qr, qo in task.relations:
                if label_match(r.subj, qs) and label_match(r.obj, qo):
                    keep_relations.append(r)
                    break
    from .types import SemanticObs
    return SemanticObs(
        frame_id=sem.frame_id,
        image=sem.image,
        region=sem.region,
        objects=keep_objects,
        relations=keep_relations,
    )


class CSREncoder:
    def __init__(self, dim: int = 128):
        self.dim = dim

    def encode(self, kf: Keyframe, task: TaskGraph) -> np.ndarray:
        vec = np.zeros(self.dim, dtype=np.float32)
        sem = extract_task_relevant_semantic(kf.semantic, task)
        if sem is None:
            return vec

        # Region component.
        if sem.region:
            _add_token(vec, sem.region, 0.8, "region:")

        # Node embeddings: label + attrs + coarse 3D bins.
        for o in sem.objects:
            _add_token(vec, o.label, 1.0 * o.score, "obj:")
            for a in o.attrs:
                _add_token(vec, a, 0.45 * o.score, "attr:")
            if o.xyz is not None and len(o.xyz) >= 3:
                try:
                    x, y, z = [float(v) for v in o.xyz[:3]]
                    bins = (round(x / 0.5), round(y / 0.5), round(z / 0.5))
                    _add_token(vec, f"{o.label}:xyz:{bins}", 0.35, "pos:")
                except Exception:
                    pass

        # Edge embeddings.
        for r in sem.relations:
            _add_token(vec, f"{r.subj}-{r.rel}-{r.obj}", 1.15, "rel:")
            _add_token(vec, r.rel, 0.55, "reltype:")

        # Task condition tokens ensure the representation is task-aligned.
        for o in task.target_objects:
            _add_token(vec, o, 0.25, "task_target:")
        for o in task.reference_objects:
            _add_token(vec, o, 0.20, "task_ref:")
        for r in task.target_regions:
            _add_token(vec, r, 0.20, "task_region:")
        for s, rel, o in task.relations:
            _add_token(vec, f"{s}-{rel}-{o}", 0.25, "task_rel:")

        return _normalize(vec)


def cosine(a: np.ndarray | None, b: np.ndarray | None) -> float:
    if a is None or b is None:
        return 0.0
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def jaccard(xs: Iterable[str], ys: Iterable[str]) -> float:
    a = {str(x).lower() for x in xs if str(x).strip()}
    b = {str(y).lower() for y in ys if str(y).strip()}
    if not a and not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))


def relation_similarity_components(a: Keyframe, b: Keyframe, task: TaskGraph) -> dict:
    sa = extract_task_relevant_semantic(a.semantic, task)
    sb = extract_task_relevant_semantic(b.semantic, task)
    if sa is None or sb is None:
        return {"entity": 0.0, "attr": 0.0, "spatial": 0.0, "region": 0.0, "stage": 0.0, "csr": 0.0}

    ent_a = [o.label for o in sa.objects]
    ent_b = [o.label for o in sb.objects]
    attr_a = [x for o in sa.objects for x in o.attrs]
    attr_b = [x for o in sb.objects for x in o.attrs]
    rel_a = [f"{r.subj}-{r.rel}-{r.obj}" for r in sa.relations]
    rel_b = [f"{r.subj}-{r.rel}-{r.obj}" for r in sb.relations]

    region = 1.0 if sa.region and sb.region and label_match(sa.region, sb.region) else 0.0
    stage = 1.0 if (a.task_relevance > 0 and b.task_relevance > 0) else 0.0
    return {
        "entity": jaccard(ent_a, ent_b),
        "attr": jaccard(attr_a, attr_b),
        "spatial": jaccard(rel_a, rel_b),
        "region": region,
        "stage": stage,
        "csr": cosine(a.csr, b.csr),
    }
