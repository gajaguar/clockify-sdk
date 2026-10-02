---
type: convention
title: Endpoint comment convention
description: Every resource method carries a `# METHOD /path` comment above its def, since the no-docstrings rule in AGENTS.md leaves IDE hover text without endpoint information.
tags: [sdk, documentation]
status: stable
---

# Endpoint comment convention

This repository forbids docstrings — see the Python section of
[`AGENTS.md`](../../AGENTS.md) — so IDE
hover text does not carry endpoint information. Instead:

- every resource method has a `# METHOD /path` comment directly above its
  `def`, naming the exact Clockify endpoint it calls;
- [`coverage.md`](coverage.md) is the authoritative table of every
  documented Clockify endpoint, the SDK method that covers it, and its
  implementation status.
