# TRC-LCS

**Task-Relation Conditioned Loop Closure Scheduling for Task-Aware SLAM**

TRC-LCS is a lightweight, modular toolkit for prioritizing loop-closure candidates according to both **place similarity** and a robot's **current task**. It is designed to sit beside an existing SLAM system rather than replace the SLAM frontend or pose-graph backend.

Given ordered keyframes, an optional trajectory, optional semantic observations, and a natural-language task, TRC-LCS builds task-relevant memory, scores visual and semantic-relation candidates, schedules a small verification budget, and verifies selected candidates geometrically.

> **Project status:** `v0.1.0` is an alpha research release. It includes a reproducible synthetic demo, an installable CLI, tests, CI, dataset-integration utilities, and documented extension points. It does **not** claim production safety or public-dataset state-of-the-art performance.

## Why TRC-LCS?

Conventional loop-closure pipelines primarily ask: **"Which past place looks similar to the current frame?"** In embodied or task-driven robotics, a second question can matter: **"Which past places are most useful to reconsider for the task I am executing now?"**

TRC-LCS provides a reference implementation for studying that scheduling problem under a verification budget.

## Pipeline

```text
natural-language task
        │
        ▼
  lightweight task graph
        │
        ├──────────────┐
        ▼              ▼
 semantic memory    visual retrieval
        │              │
        ▼              │
 task-relation CSR     │
        └──────┬───────┘
               ▼
       candidate scoring
               ▼
   budget-aware scheduling
               ▼
    ORB + RANSAC verification
               ▼
       loop constraints + memory
```

The code is intentionally backend-agnostic: learned retrieval, semantic detectors, task parsers, or geometric verifiers can replace the reference implementations without changing the overall workflow.

## Features in v0.1.0

- Task-conditioned loop-candidate memory.
- Continuous semantic-relation representation (CSR) for task-relevant observations.
- Visual, task-conditioned, and fused candidate channels.
- Budget-aware immediate / deferred / suppressed scheduling.
- ORB + RANSAC reference verifier.
- `full`, `visual`, and `task` ablation modes.
- Synthetic reproducible demo and smoke benchmark.
- TUM-style trajectory input and KITTI pose-conversion helper.
- Installable CLI, unit tests, GitHub Actions CI, issue/PR templates, and release documentation.

## Installation

Python 3.10+ is recommended.

```bash
git clone <YOUR_REPOSITORY_URL>
cd TRC-LCS
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -U pip
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
pytest
```

## Quick start

Generate the bundled synthetic sequence:

```bash
python tools/make_demo_dataset.py --out data/demo --num-frames 80
```

Run the full task-conditioned pipeline:

```bash
trc-lcs \
  --task "找到客厅里红色椅子旁边的包" \
  --image-dir data/demo/images \
  --traj data/demo/trajectory_tum.txt \
  --semantics data/demo/semantics.jsonl \
  --camera 520 520 320 240 \
  --out outputs/demo
```

Equivalent module invocation:

```bash
python -m trc_lcs --help
```

The original prototype entry point remains available for compatibility:

```bash
python run_trc_lcs.py --help
```

## Outputs

Each run writes:

```text
outputs/demo/
├── candidate_scores.csv
├── loop_constraints.jsonl
├── task_memory.json
└── summary.json
```

`summary.json` records the package version, task graph, complete run configuration, frame count, candidate count, accepted loop count, and output paths so experiments can be reproduced.

## Ablation modes

The same CLI supports three reference modes:

```bash
# Visual retrieval + visual score only (task candidates and relation score disabled)
trc-lcs ... --mode visual

# Task-conditioned candidate channel + relation score
trc-lcs ... --mode task

# Both channels (default)
trc-lcs ... --mode full
```

These modes are provided for debugging and ablation; they are not claimed as benchmark baselines by themselves.

## Synthetic smoke benchmark

Run all three modes end to end:

```bash
python tools/benchmark_demo.py --work-dir outputs/benchmark_demo
```

The script writes `benchmark.json` and `benchmark.md`. This benchmark checks reproducibility and integration only; do not report it as real-world SLAM accuracy.

## Input data

### Images

`--image-dir` should contain keyframe images in sortable order (`png`, `jpg`, `jpeg`, `bmp`, or `webp`).

### Trajectory

Optional `--traj` uses row-aligned TUM format:

```text
timestamp tx ty tz qx qy qz qw
```

For KITTI odometry pose files, convert the 3x4 matrices first:

```bash
python tools/convert_kitti_poses_to_tum.py \
  --poses /path/to/poses/00.txt \
  --times /path/to/sequences/00/times.txt \
  --out data/kitti00_trajectory_tum.txt
```

### Semantic observations

Optional `--semantics` is JSONL with one keyframe observation per line:

```json
{
  "frame_id": 12,
  "image": "000012.png",
  "region": "living room",
  "objects": [
    {"label": "bag", "attrs": ["black"], "bbox": [120, 160, 80, 60], "xyz": [1.2, 0.1, 3.4], "score": 0.91},
    {"label": "red chair", "attrs": ["red"], "bbox": [230, 150, 100, 140], "xyz": [1.6, 0.0, 3.6], "score": 0.88}
  ],
  "relations": [
    {"subj": "bag", "rel": "near", "obj": "red chair"},
    {"subj": "red chair", "rel": "in_room", "obj": "living room"}
  ]
}
```

See [`docs/data-format.md`](docs/data-format.md) for details.

## Using public SLAM datasets

TRC-LCS does not redistribute third-party datasets. The recommended workflow is to export ordered keyframes and a row-aligned trajectory from your SLAM system, then provide semantic observations if available.

Integration notes for KITTI and TUM RGB-D are in [`docs/datasets.md`](docs/datasets.md). A reproducible real-data result should always identify the sequence/split, camera setup, keyframe policy, trajectory source, semantic provider, and exact CLI configuration.

## Architecture and extension points

| Module | Responsibility | Typical replacement |
|---|---|---|
| `task_parser.py` | natural language → task graph | LLM/VLM parser |
| `semantic.py` | semantic observations and relevance | detector / segmenter adapter |
| `csr.py` | task-relevant relation representation | learned relation encoder |
| `features.py` | visual candidate retrieval | NetVLAD / DINOv2 / local features |
| `memory.py` | task-conditioned memory | persistent semantic memory |
| `scoring.py` | utility scoring + scheduler | learned / uncertainty-aware policy |
| `verify.py` | geometric verification | SuperPoint/LightGlue/PnP/backend verifier |
| `pipeline.py` | orchestration + outputs | SLAM-system adapter |

See [`docs/architecture.md`](docs/architecture.md).

## Reproducibility policy

TRC-LCS separates **smoke tests** from **research benchmarks**. Synthetic data is used to verify that all modules work together. Claims about accuracy or efficiency should be made only from documented public or user-provided datasets with an exact configuration. See [`docs/benchmarking.md`](docs/benchmarking.md).

## Limitations

- The v0.1.0 task parser is a small rule-based reference implementation, not a general language understanding model.
- Semantic observations are supplied by the user or another perception stack; TRC-LCS does not bundle a detector/segmenter.
- ORB retrieval and verification are reference backends chosen for low setup cost, not as a claim that they are optimal.
- The localization-gain term uses a lightweight surrogate when SLAM covariance is unavailable.
- A candidate accepted by this research toolkit should still be validated by the host SLAM system before affecting a safety-critical robot.

## Contributing

Contributions are welcome. Start with [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`ROADMAP.md`](ROADMAP.md). Dataset adapters, regression tests, documentation, and backend integrations are especially useful.

## License

MIT. See [`LICENSE`](LICENSE).

## Citation

A software citation template is provided in [`CITATION.cff`](CITATION.cff). Add publication metadata there if a corresponding paper becomes available.
