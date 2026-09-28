---
type: tool
title: pre-commit
description: Git hook running the universal hooks from main plus whatever a language branch appends.
tags: [toolchain]
status: stable
---

# pre-commit

Git hook running the universal hooks from `main` (whitespace/EOF/YAML/TOML
checks, markdownlint, cspell) plus whatever a language branch appends to
`.pre-commit-config.yaml`.

`default_install_hook_types: [pre-commit, commit-msg, pre-push]` makes
`pre-commit install` (run by `make setup-hooks`) install all three hook
types by default. Without it, `pre-commit install` only wires the
`pre-commit` stage, so a language branch's `commit-msg`/`pre-push` hooks
(for example a commit-message linter) would never run locally.
