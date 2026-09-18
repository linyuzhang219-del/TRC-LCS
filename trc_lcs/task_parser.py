from __future__ import annotations

import re
from typing import List, Tuple
from .types import TaskGraph

CN_TO_EN = {
    "包": "bag",
    "书包": "bag",
    "背包": "bag",
    "椅子": "chair",
    "红色椅子": "red chair",
    "红椅子": "red chair",
    "沙发": "sofa",
    "桌子": "table",
    "茶几": "coffee table",
    "电视": "tv",
    "门": "door",
    "床": "bed",
    "客厅": "living room",
    "厨房": "kitchen",
    "卧室": "bedroom",
    "走廊": "corridor",
    "卫生间": "bathroom",
    "办公室": "office",
    "红色": "red",
    "蓝色": "blue",
    "黑色": "black",
    "白色": "white",
}

REGIONS = ["living room", "kitchen", "bedroom", "corridor", "bathroom", "office", "客厅", "厨房", "卧室", "走廊", "卫生间", "办公室"]
OBJECTS = ["red chair", "chair", "bag", "sofa", "table", "coffee table", "tv", "door", "bed", "红色椅子", "红椅子", "椅子", "包", "书包", "背包", "沙发", "桌子", "茶几", "电视", "门", "床"]
REL_WORDS = {
    "旁边": "near",
    "附近": "near",
    "靠近": "near",
    "near": "near",
    "beside": "beside",
    "左边": "left_of",
    "右边": "right_of",
    "前面": "in_front_of",
    "后面": "behind",
    "里面": "in_room",
    "在": "in_room",
}


def normalize_term(term: str) -> str:
    term = term.strip().lower()
    return CN_TO_EN.get(term, term)


def _find_terms(task: str, vocab: List[str]) -> List[str]:
    hits = []
    lower = task.lower()
    for v in sorted(vocab, key=len, reverse=True):
        if v.lower() in lower:
            nv = normalize_term(v)
            if nv not in hits:
                hits.append(nv)
    return hits


def parse_task(task: str) -> TaskGraph:
    """A lightweight rule parser.

    For paper experiments, replace or complement this with an LLM/VLM parser and keep the same TaskGraph structure.
    """
    regions = _find_terms(task, REGIONS)
    objects = _find_terms(task, OBJECTS)

    # Remove coarse object if a more specific one exists.
    if "red chair" in objects and "chair" in objects:
        objects.remove("chair")

    target_objects: List[str] = []
    reference_objects: List[str] = []

    # In Chinese goal sentences such as "找到客厅里红色椅子旁边的包", the final object after 的 is often target.
    if "包" in task or "bag" in task.lower() or "书包" in task or "背包" in task:
        target_objects.append("bag")
    elif objects:
        target_objects.append(objects[-1])

    for obj in objects:
        if obj not in target_objects and obj not in reference_objects:
            reference_objects.append(obj)

    if not regions:
        regions = []

    rels: List[Tuple[str, str, str]] = []
    relation = None
    for w, r in REL_WORDS.items():
        if w in task.lower():
            relation = r
            break
    if relation and target_objects and reference_objects:
        rels.append((target_objects[0], relation, reference_objects[0]))
    if regions:
        # Attach reference object to region if possible, otherwise target object.
        anchor = reference_objects[0] if reference_objects else (target_objects[0] if target_objects else "agent")
        rels.append((anchor, "in_room", regions[0]))

    stages = ["find_region", "find_reference", "find_target", "confirm"]
    return TaskGraph(
        raw_task=task,
        target_objects=target_objects,
        reference_objects=reference_objects,
        target_regions=regions,
        relations=rels,
        stages=stages,
    )
