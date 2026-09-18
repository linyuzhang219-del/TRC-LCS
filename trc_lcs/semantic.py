from __future__ import annotations

from typing import Iterable, Set
import math

from .types import Keyframe, SemanticObs, TaskGraph


def _norm(s: str | None) -> str:
    return (s or "").strip().lower()


def label_match(label: str, query: str) -> bool:
    label = _norm(label)
    query = _norm(query)
    if not label or not query:
        return False
    return label == query or query in label or label in query


def attr_match(attrs: Iterable[str], query: str) -> bool:
    q_tokens = set(_norm(query).split())
    attrs_set = {_norm(a) for a in attrs}
    return bool(q_tokens & attrs_set)


def task_relevance(kf: Keyframe, task: TaskGraph) -> float:
    sem = kf.semantic
    if sem is None:
        return 0.0

    score = 0.0
    max_score = 0.0

    task_entities = task.target_objects + task.reference_objects
    if task_entities:
        max_score += 0.45
        hit = 0
        for q in task_entities:
            if any(label_match(o.label, q) or attr_match(o.attrs, q) for o in sem.objects):
                hit += 1
        score += 0.45 * (hit / max(1, len(task_entities)))

    if task.target_regions:
        max_score += 0.20
        region_hit = any(label_match(sem.region or "", r) for r in task.target_regions)
        score += 0.20 if region_hit else 0.0

    if task.relations:
        max_score += 0.25
        rel_hit = 0
        for subj, rel, obj in task.relations:
            for rr in sem.relations:
                if label_match(rr.subj, subj) and label_match(rr.obj, obj) and rr.rel == rel:
                    rel_hit += 1
                    break
        score += 0.25 * (rel_hit / max(1, len(task.relations)))

    # At least containing any object in task is useful in early stages.
    max_score += 0.10
    if any(any(label_match(o.label, q) for q in task_entities) for o in sem.objects):
        score += 0.10

    return float(score / max(max_score, 1e-8))


def infer_simple_relations(sem: SemanticObs) -> None:
    """Fill near relations from 3D positions when not provided.

    This keeps the demo and real JSON inputs usable even when detector only outputs objects.
    """
    if sem.relations:
        return
    objs = [o for o in sem.objects if o.xyz is not None]
    for i, a in enumerate(objs):
        for b in objs[i + 1:]:
            try:
                d = math.sqrt(sum((float(a.xyz[k]) - float(b.xyz[k])) ** 2 for k in range(3)))
            except Exception:
                continue
            if d < 1.2:
                from .types import RelationObs
                sem.relations.append(RelationObs(subj=a.label, rel="near", obj=b.label))
                sem.relations.append(RelationObs(subj=b.label, rel="near", obj=a.label))
