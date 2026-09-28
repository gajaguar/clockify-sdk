# Conventions

The `check`/`fix` command split, `FILES=` scoping, and commit/branch naming.

* [check vs fix](check-vs-fix.md) - the read-only CI gate versus the
  writable auto-fix umbrella.
* [FILES= scoping](files-scoping.md) - limiting a target to specific paths
  or globs.
* [Commits and branches](commits-and-branches.md) - Conventional Commits,
  Conventional Branch, and the append-only rule for files shared with `main`.
* [Enforcing commits and branches](commits-check.md) - the pre-commit hook
  and `make commits-check` that enforce them.

README section order and writing style moved to
[`../documentation/index.md`](../documentation/index.md).
