# Python

Decisions specific to this project's Python setup.

* [No docstrings](docstring-policy.md) - the docstring policy and the
  checker that enforces it.
* [pylint-plugin](pylint-plugin.md) - the git-dependency plugin providing
  this project's custom pylint checkers.
* [Interpreter source](interpreter-source.md) - why `mise.toml` is the only
  source of the pinned Python version.
* [pyproject defaults](pyproject-defaults.md) - which settings are left out
  of `pyproject.toml` because they equal the tool's default.
* [Re-checking the commit range in CI](commit-range-in-ci.md) - why
  `make commits-check` runs in CI, not `make check`, and what it validates.
