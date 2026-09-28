---
type: tool
title: markdownlint-cli2 and cspell
description: Markdown lint and spell check, installed via pnpm and configured canonically on main.
tags: [toolchain]
status: stable
---

# markdownlint-cli2 and cspell

Markdown lint and spell check (pnpm, dev-only). Configuration
(`.markdownlint.yaml`, `.markdownlint-cli2.jsonc`, `cspell.config.yaml`) is
canonical on `main`; a language branch only appends its own dictionary words
and ignore paths — see
[`append-only-shared-files.md`](../branching/append-only-shared-files.md).
