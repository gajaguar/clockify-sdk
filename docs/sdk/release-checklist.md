---
type: playbook
title: Release checklist
description: Steps to take before tagging a release; the GitHub Release itself triggers publish.yml, which builds and uploads to PyPI.
tags: [sdk, release, git]
status: stable
---

# Release checklist

`.github/workflows/ci.yml` and `python.yml` gate every push and pull request
against `main` with `make check && make test`. Before tagging a release:

1. Confirm CI is green on the commit being released.
2. `make check` and `make test` — must exit 0 locally too; the coverage gate
   (90%) is part of `make test`.
3. `make build` — must produce a valid sdist and wheel in `dist/`.
4. Confirm [`coverage.md`](coverage.md) reflects the endpoints actually
   shipped in this version.
5. Bump `version` in `pyproject.toml` and commit.
6. Tag and publish a GitHub Release. That `published` event triggers
   `.github/workflows/publish.yml`, which builds and uploads to PyPI via
   Trusted Publishing — see
   [`../release/pypi-trusted-publishing.md`](../release/pypi-trusted-publishing.md).
