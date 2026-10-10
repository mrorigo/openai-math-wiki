# OpenAI Math Wiki

An [Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) bundle describing the **OpenAI Math Release**: 719 mathematical manuscripts covering 372 result families across 17 disciplines, published in [github.com/openai/math](https://github.com/openai/math) on October 6, 2026 under Apache-2.0. The results were produced by an unreleased internal OpenAI frontier model for model-development evaluation on open research problems.

## Navigation

- [Disciplines](disciplines/index.md) — 17 subject areas
- [Result families](results/index.md) — 372 numbered results
- [Papers](papers/index.md) — 719 manuscripts with abstracts

## Conventions

Every concept document carries `type`, `title`, `description`, `resource`, `tags`, and `timestamp` in its YAML frontmatter:

- `type: Discipline` — a subject area from the collection overview.
- `type: Result` — one numbered result family from the manuscript catalogue.
- `type: Paper` — a single manuscript; the `resource` links to the PDF in the OpenAI repository.

Papers link to their result family and discipline; result families link to their papers. Tags use a controlled vocabulary: `discipline-<slug>`, `family-<NNN>`, `lean-formalized`, `reasoning-trace`.

## Statistics

- 719 papers, 372 result families, 17 disciplines.
- 172 papers with a Lean formalization (tagged `lean-formalized`).
- 10 result families with an abridged reasoning summary (tagged `reasoning-trace`).
- Repository snapshot date: 2026-10-10.

## Managing the store

This directory is both the OKF bundle and the [rust-okf](https://github.com/mrorigo/rust-okf) store root (`okf.toml` + `.okf-index/`). The indexer skips `index.md`, `log.md`, and dot-directories, so the store can live inside the bundle.

```bash
cd openai-math-wiki
okf init-config        # (re)create okf.toml
okf add .              # full (re)build of the hybrid index
okf update .           # incremental update after editing documents
okf compact            # merge segments and clear tombstones
okf search "quasi-Riemann hypothesis"
okf search "Selmer corank" --filter-type Paper --filter-tag family-002 --json
okf serve --bind 127.0.0.1:8787
```
