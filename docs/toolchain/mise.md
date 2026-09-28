---
type: tool
title: mise
description: Pins the high-level toolchain — Node, pnpm, pre-commit, and the language runtime on a language branch.
tags: [toolchain]
status: stable
---

# mise

Pins the high-level toolchain (`mise.toml`): Node, pnpm, pre-commit, and — on
language branches — the language runtime itself (e.g. Python, uv).
Per-language package managers keep doing their own job (uv for Python, pnpm
for Node). See [`layering-rule.md`](layering-rule.md) for the boundary this
enforces.
