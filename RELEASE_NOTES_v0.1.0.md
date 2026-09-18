# TRC-LCS v0.1.0 — Initial alpha release

TRC-LCS is a modular reference toolkit for task-relation conditioned loop-closure scheduling in task-aware and embodied SLAM.

## Highlights

- Combines visual loop candidates with task-conditioned semantic-relation candidates.
- Maintains task-relevant keyframe memory and a lightweight continuous semantic-relation representation (CSR).
- Uses a configurable verification budget with immediate, deferred, suppressed, and safety-reactivated candidates.
- Ships an ORB + RANSAC reference verifier that can be replaced by learned backends.
- Provides `full`, `visual`, and `task` modes for reproducible ablations.
- Adds an installable `trc-lcs` CLI, tests, CI, data-format docs, KITTI pose conversion, and a synthetic smoke benchmark.

## Quick start

```bash
pip install -e .
python tools/make_demo_dataset.py --out data/demo --num-frames 80
trc-lcs \
  --task "找到客厅里红色椅子旁边的包" \
  --image-dir data/demo/images \
  --traj data/demo/trajectory_tum.txt \
  --semantics data/demo/semantics.jsonl \
  --camera 520 520 320 240 \
  --out outputs/demo
```

## Scope of this release

v0.1.0 is an alpha research release. The included synthetic sequence is for end-to-end reproducibility testing and is not a real-world accuracy benchmark. Public-dataset performance claims are intentionally deferred until a documented and independently reproducible protocol is added.

## Known limitations

- Rule-based reference task parser.
- User-supplied semantic observations.
- ORB reference retrieval/verification backend.
- Row-aligned image/trajectory assumption.

See `ROADMAP.md` for planned public-dataset adapters, learned backend interfaces, and ROS 2 integration.
