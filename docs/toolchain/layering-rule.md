---
type: decision
title: Toolchain layering rule
description: mise installs what bootstraps an ecosystem or belongs to none; the ecosystem's own package manager installs everything else.
tags: [toolchain]
status: stable
---

# Toolchain layering rule

> **mise installs what bootstraps an ecosystem or belongs to none. The
> ecosystem's package manager installs everything else.**

A tool declared in two layers can drift between them — `make check` and the
git hook can then reach different verdicts on the same file, the exact
class of drift this rule exists to prevent. `mise.toml`'s `[env]` sets
`UV_PYTHON_PREFERENCE = "only-system"` and `UV_PYTHON_DOWNLOADS = "never"`,
forcing uv to use the mise-provided interpreter instead of shadowing it
with its own — see [`../python/interpreter-source.md`](../python/interpreter-source.md).

| Tool                                | Where                                      | Why                                      |
| :---------------------------------- | :----------------------------------------- | :--------------------------------------- |
| node, pnpm, python, uv              | `mise.toml`                                | bootstrap: nothing else can install them |
| checkmake                           | `mise.toml`                                | Go binary, no ecosystem in this repo     |
| pre-commit                          | `mise.toml`                                | meta-tool that runs everything else      |
| cspell, markdownlint-cli2           | `package.json`                             | Node dev deps, lockfile-managed          |
| ruff, mypy, pyright, pytest, pylint | `pyproject.toml` `[dependency-groups].dev` | Python dev deps, `uv.lock`-managed       |

See [`rejected-install-backends.md`](rejected-install-backends.md) for the
alternatives this decision ruled out.
