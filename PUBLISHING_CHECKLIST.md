# GitHub publishing checklist for v0.1.0

Use this checklist before submitting TRC-LCS to Codex for Open Source.

## Repository setup

- [ ] Create a **public** GitHub repository named `TRC-LCS` (or another final name).
- [ ] Upload the contents of this package to the repository root.
- [ ] Replace `<YOUR_REPOSITORY_URL>` in `README.md` with the actual repository URL.
- [ ] Confirm the default branch is `main`.
- [ ] Confirm GitHub Actions CI passes on Python 3.10 and 3.11.
- [ ] Confirm the repository shows the MIT license.
- [ ] Enable GitHub Discussions if you want a low-friction support channel.
- [ ] Enable private vulnerability reporting / Security Advisories if available.

## First public maintenance signals

- [ ] Open 3–5 roadmap issues from `ROADMAP.md` rather than committing every future task privately.
- [ ] Label at least one small documentation/test issue as `good first issue`.
- [ ] Close at least one issue through a normal PR so the repository visibly demonstrates the review workflow.
- [ ] Keep CI green and avoid committing generated `data/` or `outputs/` directories.

## Release

- [ ] Tag commit as `v0.1.0`.
- [ ] Create a GitHub Release titled `TRC-LCS v0.1.0 — Initial alpha release`.
- [ ] Paste `RELEASE_NOTES_v0.1.0.md` into the release description.
- [ ] Attach a source archive only if useful; GitHub already generates source ZIP/tarballs.

## Before the Codex for Open Source application

- [ ] GitHub profile is public.
- [ ] Repository is public.
- [ ] You are clearly the primary maintainer in the repository activity/README or project metadata.
- [ ] README Quick Start works from a fresh environment.
- [ ] CI has at least one successful public run.
- [ ] v0.1.0 release is visible.
- [ ] At least a small amount of genuine issue/PR/release activity is visible.
- [ ] Copy the final repository URL and your OpenAI Organization ID into the application packet.

Do not invent stars, downloads, users, contributors, or benchmark results. A new project should explain ecosystem relevance and show credible maintenance infrastructure instead.
