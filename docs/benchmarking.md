# Benchmarking and reporting

## Synthetic smoke benchmark

`tools/benchmark_demo.py` is a software integration test. Its outputs demonstrate that the candidate channels, scheduler, verifier, and serialization run end to end. They are not evidence of real-world accuracy.

## Recommended real-data report

For every result, record:

- TRC-LCS version or Git commit.
- Dataset and exact sequence/split.
- Image/keyframe policy.
- Trajectory source and whether it is online estimate or ground truth.
- Camera intrinsics used by verification.
- Semantic provider and label mapping.
- CLI/configuration values.
- Hardware and software environment for runtime results.

At minimum, consider reporting:

- candidate pairs generated,
- geometric verification calls,
- accepted loop closures,
- true/false loop closures if ground truth permits,
- verification recall/precision under a stated loop definition,
- mean/percentile runtime per keyframe,
- memory footprint or stored keyframe count.

## Fair ablations

Use the same keyframes, geometry verifier, temporal exclusion window, and verification budget when comparing `visual`, `task`, and `full` modes. Otherwise changes in compute may be caused by different candidate opportunities rather than the scheduling signal itself.
