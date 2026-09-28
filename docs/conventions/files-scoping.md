---
type: convention
title: FILES= scoping
description: Most make targets accept FILES="..." to limit scope to specific paths or globs.
tags: [makefile]
status: stable
---

# FILES= scoping

Most targets accept `FILES="..."` to limit scope to specific paths or globs,
for example `make md-lint FILES="README.md"`.
