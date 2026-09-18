# Changelog

All notable changes to TRC-LCS are documented here.

## [0.1.0] - 2026-09-17

### Added
- Installable Python package with the `trc-lcs` CLI.
- Task-conditioned semantic memory and continuous semantic-relation encoding.
- Visual and task-conditioned loop-candidate channels.
- Budget-aware immediate/deferred/suppressed scheduling.
- ORB + RANSAC geometric verification.
- `full`, `visual`, and `task` ablation modes.
- Synthetic reproducible demo and smoke benchmark tooling.
- KITTI pose conversion helper and public-dataset integration guidance.
- Unit tests, GitHub Actions CI, contribution guidelines, issue templates, and release documentation.

### Known limitations
- The bundled natural-language parser is intentionally lightweight and rule based.
- v0.1.0 uses ORB for retrieval and geometric verification; learned feature backends are extension points rather than bundled dependencies.
- Public-dataset benchmark numbers are not shipped as claims until independently reproduced with a documented configuration.
