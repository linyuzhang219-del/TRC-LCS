# Architecture

TRC-LCS keeps the scheduling layer separate from the host SLAM system.

## 1. Task graph

`task_parser.parse_task()` converts a natural-language goal into a small `TaskGraph` containing targets, references, regions, relations, and coarse stages. v0.1.0 ships a deterministic rule parser so the demo has no remote-model dependency.

## 2. Task-relevant semantic memory

Each keyframe may carry a `SemanticObs`. `semantic.task_relevance()` estimates relevance to the current task. Relevant frames enter `TaskMemory`.

## 3. Continuous semantic-relation representation (CSR)

`CSREncoder` hashes task-relevant object, attribute, region, spatial-relation, and coarse 3D tokens into a normalized vector. It is deliberately lightweight and replaceable.

## 4. Candidate channels

`ORBVisualIndex` retrieves visually similar historical frames. `TaskMemory` retrieves task-related frames using CSR and relation components. The two candidate sets are merged without requiring a specific SLAM frontend.

## 5. Scoring

Each candidate combines visual score, relation score, an estimated localization-gain term, redundancy, and estimated verification cost. All weights live in `TRCLCSConfig`.

## 6. Scheduling

`CandidateScheduler` separates candidates into immediate, deferred, or suppressed groups and enforces a per-frame verification budget. Deferred candidates can be reactivated under elevated uncertainty.

## 7. Verification

v0.1.0 uses ORB matching and an essential-matrix or homography RANSAC check. This is a reference backend. Learned feature matchers can replace it behind the same candidate interface.

## 8. Outputs

The pipeline emits candidate-level diagnostics, accepted loop constraints, task memory, and a full run summary. These artifacts are intended to make regressions and benchmark settings auditable.
