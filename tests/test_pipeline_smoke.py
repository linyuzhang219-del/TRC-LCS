import json
from pathlib import Path

import numpy as np
import pytest

cv2 = pytest.importorskip("cv2")

from trc_lcs.config import TRCLCSConfig
from trc_lcs.io import build_keyframes
from trc_lcs.pipeline import TRCLCSPipeline


def _make_tiny_sequence(root: Path, n: int = 14) -> tuple[Path, Path, Path]:
    image_dir = root / "images"
    image_dir.mkdir(parents=True)
    sem_path = root / "semantics.jsonl"
    traj_path = root / "trajectory_tum.txt"

    rng = np.random.default_rng(7)
    base = (rng.random((120, 160)) * 255).astype(np.uint8)
    with sem_path.open("w", encoding="utf-8") as sf, traj_path.open("w", encoding="utf-8") as tf:
        for i in range(n):
            # Repeat texture every 7 frames so the sequence contains a simple loop-like revisit.
            img = base.copy() if i % 7 == 0 else np.roll(base, i % 7, axis=1)
            cv2.imwrite(str(image_dir / f"{i:06d}.png"), img)
            sf.write(
                json.dumps(
                    {
                        "frame_id": i,
                        "image": f"{i:06d}.png",
                        "region": "living room",
                        "objects": [
                            {"label": "red chair", "attrs": ["red"], "score": 0.95},
                            {"label": "bag", "attrs": ["black"], "score": 0.90},
                        ],
                        "relations": [{"subj": "bag", "rel": "near", "obj": "red chair"}],
                    }
                )
                + "\n"
            )
            tf.write(f"{i}.0 {float(i):.3f} 0 0 0 0 0 1\n")
    return image_dir, traj_path, sem_path


def test_pipeline_writes_expected_outputs(tmp_path: Path):
    image_dir, traj, semantics = _make_tiny_sequence(tmp_path)
    keyframes = build_keyframes(image_dir, traj, semantics)
    cfg = TRCLCSConfig(
        min_temporal_gap=5,
        budget=2,
        high_score_threshold=0.20,
        low_score_threshold=0.10,
        min_good_matches=8,
        min_inliers=6,
        min_inlier_ratio=0.20,
    )
    out = tmp_path / "out"
    summary = TRCLCSPipeline("找到客厅里红色椅子旁边的包", cfg, out).process(keyframes)
    assert summary["trc_lcs_version"] == "0.1.0"
    assert summary["num_frames"] == 14
    assert (out / "candidate_scores.csv").exists()
    assert (out / "loop_constraints.jsonl").exists()
    assert (out / "task_memory.json").exists()
    assert (out / "summary.json").exists()
