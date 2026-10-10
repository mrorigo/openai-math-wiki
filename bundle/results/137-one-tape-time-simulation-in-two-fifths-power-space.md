---
title: "137. One-tape time simulation in two-fifths-power space"
type: Result
description: |-
    Determines the halting and finite-control outcome of a fixed deterministic one-writable-tape machine up to time <i>T</i> using $`O(T^{2/5}\log^C(T+2))`$ space, improving the square-root exponent. Heads move at most one cell per step; finitely many read-only input heads are allowed. Initial contents are independent of <i>T</i>, and contents and input symbols have polylogarithmic-space access. Simulation time is unrestricted.
resource: https://github.com/openai/math/blob/main/preprints/Simulating-One-Tape-Time-in-Two-Fifths-Power-Space-September-25-2026/article.pdf
tags: [openai-math, discipline-theoretical-computer-science, family-137, lean-doc]
timestamp: 2026-10-06
---

# 137. One-tape time simulation in two-fifths-power space

> Discipline: [Theoretical computer science](../disciplines/theoretical-computer-science.md)
> Manuscripts: **1**

[Lean formalization of headline result](https://github.com/openai/math/blob/main/lean/docs/137.md)

## Description

Determines the halting and finite-control outcome of a fixed deterministic one-writable-tape machine up to time <i>T</i> using $`O(T^{2/5}\log^C(T+2))`$ space, improving the square-root exponent. Heads move at most one cell per step; finitely many read-only input heads are allowed. Initial contents are independent of <i>T</i>, and contents and input symbols have polylogarithmic-space access. Simulation time is unrestricted.

## Manuscripts

- [Simulating One-Tape Time in Two-Fifths-Power Space](../papers/Simulating-One-Tape-Time-in-Two-Fifths-Power-Space-September-25-2026.md) (`lean-formalized`) — *2026-09-25*
