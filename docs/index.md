---
okf_version: "0.2"
---

# Documentation

This is an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
(OKF) bundle: one Markdown concept per file, each with YAML frontmatter, laid
out under this directory.

## Reference

* [Conventions](conventions/index.md) - the `check`/`fix` split, `FILES=`
  scoping, and commit/branch naming.
* [Toolchain](toolchain/index.md) - which layer (mise or an ecosystem package
  manager) installs which tool, and why.

See [`log.md`](log.md) for the bundle's change history.

## Release

* [Release](release/index.md) - how this project ships new versions to
  PyPI.

## Python

* [Python](python/index.md) - the docstring policy, `pylint-plugin`, and the interpreter
  source decision.

## SDK

* [SDK](sdk/index.md) - layering, request lifecycle, pagination, and the
  endpoint coverage table.
