# Roadmap

TRC-LCS is an early-stage research-oriented OSS toolkit. Planned work is deliberately scoped around reusable interfaces and reproducibility.

## v0.2
- Pluggable visual retrieval interface (NetVLAD / DINOv2 / learned local features).
- Explicit semantic-provider interface for detector/segmenter outputs.
- Reproducible KITTI and TUM RGB-D example configurations.
- Candidate-level benchmark metrics: verification calls, accepted loops, runtime, and memory.

## v0.3
- ROS 2 integration example.
- Adapter for pose-graph backends and covariance-aware localization gain.
- Learned or LLM-assisted task parsing behind an optional interface.
- Dataset regression suite and versioned benchmark reports.

## Long term
- Community-maintained adapters for additional SLAM systems.
- Stable plugin API for retrieval, semantics, verification, and scheduling policies.
