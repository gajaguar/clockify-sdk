---
type: convention
title: Endpoint comment convention
description: Every resource method carries a `# METHOD /path` comment above its def, since app-no-docstrings (see docs/python/docstring-policy.md) leaves IDE hover text without endpoint information.
tags: [sdk]
status: stable
---

# Endpoint comment convention

This repository enforces `app-no-docstrings` — see
[`docs/python/docstring-policy.md`](../python/docstring-policy.md) — so IDE
hover text does not carry endpoint information. Instead:

- every resource method has a `# METHOD /path` comment directly above its
  `def`, naming the exact Clockify endpoint it calls;
- [`coverage.md`](coverage.md) is the authoritative table of every
  documented Clockify endpoint, the SDK method that covers it, and its
  implementation status.
