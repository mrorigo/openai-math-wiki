# openai-math-wiki

An [Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) (OKF) knowledge base of the **OpenAI Math Release** — the 719 mathematical manuscripts, 372 result families, and 17 disciplines published in [github.com/openai/math](https://github.com/openai/math) on October 6, 2026. Each manuscript is a `Paper` concept with its abstract, BibTeX citation, result-family and discipline links; families are `Result` concepts; subject areas are `Discipline` concepts. The bundle is indexed by [rust-okf](https://github.com/origo/rust-okf) into a hybrid (BM25 + dense vector) search store you can query from a CLI, HTTP API, or MCP.

## What's inside

| Concept type | Count | Example |
| --- | ---: | --- |
| `Discipline` | 17 | `bundle/disciplines/number-theory.md` |
| `Result` (result family) | 372 | `bundle/results/003-the-quasi-riemann-hypothesis.md` |
| `Paper` (manuscript) | 719 | `bundle/papers/The-Quasi-Riemann-Hypothesis-September-30-2026.md` |

Extra metadata derived from the release and queryable via tags:

- **172 papers** have a Lean formalization (`lean-formalized` tag), per `lean/formalization.yaml`.
- **10 result families** ship an abridged reasoning summary (`reasoning-trace` tag), e.g. the irrationality exponent of π and the quasi-Riemann hypothesis.
- Every paper carries a `timestamp` (its preprint date), `resource` (GitHub PDF), and BibTeX citation block.

## Repository layout

```
openai-math-wiki/
├── README.md                 # this file (not part of the bundle)
├── okf.toml                  # rust-okf configuration
├── .gitignore                # ignores .okf-index and .fastembed_cache
├── scripts/
│   └── build_bundle.py       # regenerates bundle/ from a math/ snapshot
├── bundle/                   # the OKF bundle (relative links resolve inside)
│   ├── index.md              # bundle root — reserved, not indexed
│   ├── log.md                # changelog — reserved, not indexed
│   ├── disciplines/          # 17 docs, type: Discipline
│   ├── results/              # 372 docs, type: Result
│   └── papers/               # 719 docs, type: Paper
└── .okf-index/               # generated hybrid search store (git-ignored)
```

## Conventions

Every concept is one Markdown file with YAML frontmatter carrying `type`, `title`, `description`, `resource`, `tags`, and `timestamp`. Per the OKF v0.1 spec, `type` is the only required field and is always set here. Files are `index.md`/`log.md` only at directory roots and are used for human navigation; the rust-okf indexer skips them.

Tags form a controlled vocabulary:

| Tag | Applies to | Meaning |
| --- | --- | --- |
| `openai-math` | all | Part of this collection |
| `discipline-<slug>` | all | Subject area, e.g. `discipline-number-theory` |
| `family-<NNN>` | all | Catalogue result family, e.g. `family-003` |
| `lean-formalized` | Paper | Manuscript has a Lean formalization |
| `lean-doc` | Result | Family has a Lean writeup in `lean/docs/` |
| `reasoning-trace` | Result | Family has an abridged reasoning summary |

## Data provenance

Generated (see `scripts/build_bundle.py`) from a snapshot of `openai/math` cloned on 2026-10-10:

- **Titles, abstracts, and paper PDF paths** — `CONTENTS.md` (719 manuscript entries).
- **Result families and discipline classification** — `overview.tex` (372 `\resultentry` blocks in 17 `\cataloguesection`s).
- **Preprint dates and BibTeX citation keys** — each `preprints/*/README.md`.
- **Lean formalization status** — `lean/formalization.yaml`.
- **Reasoning summaries** — the release `README.md` table.

Two intentional notes: the catalogue numbers its families 001–377 with five gaps (45, 61, 70, 123, 163 are absent), and 30 additional `preprints/` directories that are not referenced by the current catalogue (earlier versions of revised papers) are excluded.

## Getting started

Requires the `okf` CLI (build or install from [rust-okf](https://github.com/origo/rust-okf)). FastEmbed downloads model weights on first run.

```bash
cd openai-math-wiki
okf add bundle        # build the hybrid index (creates .okf-index/)
okf search "quasi-Riemann hypothesis"
okf search "Selmer corank" --filter-type Paper --filter-tag family-002 --json
okf serve --bind 127.0.0.1:8787     # HTTP API (GET /health, POST /search, ...)
```

Search options: `--mode hybrid|lexical|vector`, `--top-k`, `--offset`, `--filter-type`, `--filter-tag`, `--filter-path`, `--json`, `--explain`. `okf mcp` exposes search/index/update/delete/compact tools over stdio for MCP clients.

## Regenerating the bundle

```bash
python3 scripts/build_bundle.py      # rewrites bundle/ from ../math
okf update bundle                    # incrementally refresh the store
okf compact                          # merge segments, clear tombstones
```

`okf add bundle` performs a full rebuild of the store; `okf update bundle` applies only changes.

## Notes and limitations

- Mathematical notation is stored as it appears in the source (`$\pi$`, `<i>…</i>`, HTML entities), so lexical queries tokenize LaTeX literally — drop the backslash math (e.g. search `irrationality exponent of pi`) for the best matches.
- The release itself cautions that not all results are formally verified; the source repository tracks corrections and revisions (`history.md`).
- The OKF spec: [announcement](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) · [spec repo](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf) · [Karpathy's LLM wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## License

Manuscripts and supporting artifacts in `openai/math` are released under Apache-2.0. This bundle is derived from them; the wiki files themselves are licensed Apache-2.0 as well.