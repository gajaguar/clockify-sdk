---
type: convention
title: check vs fix
description: Targets are split by whether they mutate files — check is the read-only CI gate, fix writes in place.
tags: [makefile]
status: stable
---

# check vs fix

Targets are split by whether they mutate files:

| Umbrella            | Behavior                                                             |
| :------------------ | :------------------------------------------------------------------- |
| `check` (read-only) | Reports problems, exits non-zero, never writes. This is the CI gate. |
| `fix` (writable)    | Mutates files in place.                                              |

Each language branch appends its own targets to `check`/`fix` (and to
`install`/`test`) via `mk/*.mk` — see
[`adding-a-language.md`](../branching/adding-a-language.md).
