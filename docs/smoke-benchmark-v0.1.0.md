# Synthetic smoke benchmark

> This is a deterministic integration smoke test, not a real-world SLAM accuracy benchmark.

| mode | frames | candidates | verified loops | task-memory frames | wall time (s) |
|---|---:|---:|---:|---:|---:|
| visual | 80 | 810 | 1 | 47 | 2.498 |
| task | 80 | 610 | 3 | 47 | 1.988 |
| full | 80 | 953 | 18 | 47 | 5.779 |

## Validation environment

This snapshot was generated while preparing v0.1.0 with Python 3.11, NumPy 2.3.5, and OpenCV 4.13.0. Runtime varies by machine. Re-run the benchmark on your own environment instead of comparing the wall-clock column across hardware.
