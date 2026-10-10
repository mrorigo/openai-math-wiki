---
title: "099. The sharp exponential scale of edit-distance distortion"
type: Result
description: |-
    Determines the least distortion of embedding edit distance on words of length at most <i>d</i> into real <i>ℓ</i><sub>1</sub>: it is $`\exp(\Theta(\sqrt{\log d\,\log\log d}))`$. Insertions, deletions and substitutions have unit cost. The constants are uniform over all finite alphabets with at least two symbols, even when the alphabet grows with <i>d</i>; binary words already force the lower bound.
resource: https://github.com/openai/math/blob/main/preprints/Edit-Distance-in-l1-Matching-Bounds-up-to-Constants-in-the-Exponent-September-27-2026/paper.pdf
tags: [openai-math, discipline-convex-and-metric-geometry, family-099, lean-doc]
timestamp: 2026-10-06
---

# 099. The sharp exponential scale of edit-distance distortion

> Discipline: [Convex and metric geometry](../disciplines/convex-and-metric-geometry.md)
> Manuscripts: **3**

[Lean formalization of headline result](https://github.com/openai/math/blob/main/lean/docs/099.md)

## Description

Determines the least distortion of embedding edit distance on words of length at most <i>d</i> into real <i>ℓ</i><sub>1</sub>: it is $`\exp(\Theta(\sqrt{\log d\,\log\log d}))`$. Insertions, deletions and substitutions have unit cost. The constants are uniform over all finite alphabets with at least two symbols, even when the alphabet grows with <i>d</i>; binary words already force the lower bound.

## Manuscripts

- [Edit Distance in l1: Matching Bounds up to Constants in the Exponent](../papers/Edit-Distance-in-l1-Matching-Bounds-up-to-Constants-in-the-Exponent-September-27-2026.md) — *2026-09-27*
- [Finite-Circle Obstructions, Binary Codes, and Histogram Embeddings for Edit Distance](../papers/Finite-Circle-Obstructions-Binary-Codes-and-Histogram-Embeddings-for-Edit-Distance-September-27-2026.md) — *2026-09-27*
- [Tree Constructions for the l1 Distortion of Binary Edit Distance](../papers/Tree-Constructions-for-the-l1-Distortion-of-Binary-Edit-Distance-September-27-2026.md) — *2026-09-27*
