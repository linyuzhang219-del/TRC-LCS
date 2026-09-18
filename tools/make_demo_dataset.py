from __future__ import annotations

import argparse
import json
from pathlib import Path
import math
import random

import cv2
import numpy as np


def write_tum(path: Path, num_frames: int):
    with path.open("w", encoding="utf-8") as f:
        for i in range(num_frames):
            # A simple loop trajectory in x-z plane.
            theta = 2 * math.pi * i / max(1, num_frames)
            x = 8 * math.cos(theta)
            y = 0.0
            z = 8 * math.sin(theta)
            # Identity quaternion for demo.
            f.write(f"{i:.6f} {x:.6f} {y:.6f} {z:.6f} 0 0 0 1\n")


def draw_scene(i: int, num_frames: int, w: int = 640, h: int = 480):
    img = np.full((h, w, 3), 245, dtype=np.uint8)
    theta = 2 * math.pi * i / max(1, num_frames)

    # Static visual texture repeated after a loop.
    rng = random.Random(i % 40)
    for _ in range(120):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        cv2.circle(img, (x, y), rng.randint(1, 3), (rng.randint(0, 120), rng.randint(0, 120), rng.randint(0, 120)), -1)

    region = "living room" if (10 <= i <= 35 or 55 <= i <= 75) else "corridor"
    objects = []
    relations = []

    # Draw a red chair in task region.
    if region == "living room":
        chair_x = int(310 + 40 * math.sin(theta))
        chair_y = 245
        cv2.rectangle(img, (chair_x - 40, chair_y - 70), (chair_x + 40, chair_y + 50), (30, 30, 220), 3)
        cv2.line(img, (chair_x - 35, chair_y + 50), (chair_x - 55, chair_y + 100), (30, 30, 220), 3)
        cv2.line(img, (chair_x + 35, chair_y + 50), (chair_x + 55, chair_y + 100), (30, 30, 220), 3)
        objects.append({
            "label": "red chair",
            "attrs": ["red"],
            "bbox": [chair_x - 40, chair_y - 70, 80, 120],
            "xyz": [2.0 + 0.2 * math.sin(theta), 0.0, 4.0],
            "score": 0.95,
        })

        # Bag appears near chair in two parts of loop.
        if 18 <= i <= 35 or 62 <= i <= 75:
            bag_x = chair_x - 85
            bag_y = chair_y + 45
            cv2.rectangle(img, (bag_x - 25, bag_y - 25), (bag_x + 25, bag_y + 25), (20, 20, 20), -1)
            cv2.rectangle(img, (bag_x - 22, bag_y - 22), (bag_x + 22, bag_y + 22), (80, 80, 80), 2)
            objects.append({
                "label": "bag",
                "attrs": ["black"],
                "bbox": [bag_x - 25, bag_y - 25, 50, 50],
                "xyz": [1.35 + 0.2 * math.sin(theta), 0.0, 4.05],
                "score": 0.93,
            })
            relations.append({"subj": "bag", "rel": "near", "obj": "red chair"})
        relations.append({"subj": "red chair", "rel": "in_room", "obj": "living room"})

    # Add generic distractor objects.
    cv2.rectangle(img, (60, 350), (160, 390), (120, 80, 40), 2)
    cv2.putText(img, f"frame {i:03d} {region}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    return img, region, objects, relations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--num-frames", type=int, default=80)
    args = ap.parse_args()

    out = Path(args.out)
    img_dir = out / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    sem_path = out / "semantics.jsonl"
    with sem_path.open("w", encoding="utf-8") as sf:
        for i in range(args.num_frames):
            img, region, objects, relations = draw_scene(i, args.num_frames)
            name = f"{i:06d}.png"
            cv2.imwrite(str(img_dir / name), img)
            sf.write(json.dumps({
                "frame_id": i,
                "image": name,
                "region": region,
                "objects": objects,
                "relations": relations,
            }, ensure_ascii=False) + "\n")

    write_tum(out / "trajectory_tum.txt", args.num_frames)
    print(f"Demo dataset written to {out}")


if __name__ == "__main__":
    main()
