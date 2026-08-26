# Clockify Unofficial SDK

> **Unofficial.** This project is not affiliated with, endorsed by, or
> supported by CAKE.com d.o.o. "Clockify" is a trademark of CAKE.com d.o.o.
> Use at your own risk against the [Clockify API](https://docs.clockify.me/).

A typed, synchronous Python client for the Clockify Working API, Reports API,
and user management. Package manager: [uv](https://docs.astral.sh/uv/).
Requires **Python >= 3.14**.

See [`docs/TECH_SPEC.md`](docs/TECH_SPEC.md) for the full technical
specification, [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for how the
client is layered, and [`docs/coverage.md`](docs/coverage.md) for the endpoint
coverage matrix.

## Status

Pre-alpha scaffold. No Clockify endpoint is implemented yet — see
`docs/coverage.md`.

## Quickstart

```bash
make install   # sync Python deps, install node tooling, install pre-commit hook
make check     # read-only gate: lint, format-check, mypy, pyright,
               # md-lint, spell, pylint
make fix       # apply safe auto-fixes (format, ruff --fix, markdownlint --fix)
make test      # run the test suite
```

Run `make help` for the full target list.

## Authentication

```python
import os
from clockify import ClockifyClient

os.environ["CLOCKIFY_API_KEY"] = "..."
client = ClockifyClient()  # reads CLOCKIFY_API_KEY
client = ClockifyClient(api_key="...")  # explicit argument takes precedence
```

## Command convention: `check` vs `fix`

Targets are split by whether they mutate files:

| Prefix / umbrella   | Behavior                                                             | Example targets                                                                               |
| ------------------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `check` (read-only) | Reports problems, exits non-zero, never writes. This is the CI gate. | `lint`, `format-check`, `mypy`, `pyright`, `typecheck`, `md-lint`, `spell`, `pylint`, `check` |
| `fix` (writable)    | Mutates files in place.                                              | `format`, `lint-fix`, `lint-fix-unsafe`, `md-fix`, `fix`, `fix-unsafe`                        |

All targets accept `FILES="..."` to scope to specific paths/globs, e.g.
`make lint FILES="src/clockify/client.py"`.

There is no CI pipeline for this repository (accepted trade-off — see
`docs/TECH_SPEC.md` §11, risk R2). `make check && make test` is the gate;
run it before every commit and always before tagging a release.

## Toolchain

- **uv** — dependency management and virtualenvs (`hatchling` build backend)
- **httpx** — HTTP transport
- **pydantic** — request/response models and validation
- **ruff** — linting and formatting (`lint.select = ["ALL"]`, curated ignores)
- **mypy** + **pyright** — static type checking
- **pytest** + **pytest-cov** + **respx** — testing, coverage, HTTP mocking
- **markdownlint-cli2** + **cspell** (pnpm, dev-only) — Markdown lint & spell check
- **pylint** + [`custom-pylint-rules`](https://github.com/gajaguar/custom-pylint-rules)
  (uv git dependency) — custom checkers for personal-preference rules ruff
  doesn't cover (e.g. no docstrings — see below)
- **pre-commit** — git hook running ruff, ruff-format, mypy, and pylint before
  each commit

### Docstring policy

This project does not use docstrings — use comments only where the *why*
isn't obvious from the code. `custom-pylint-rules`'s `app-no-docstrings`
(W9001) checker fails `make check`/`make pylint` if any function, method, or
class has one. Because the SDK can't rely on docstrings for endpoint
reference, each resource method carries a one-line `# METHOD /path` comment
above its definition, and the authoritative endpoint-to-method mapping lives
in [`docs/coverage.md`](docs/coverage.md).

### Custom pylint checkers (`custom-pylint-rules`)

A standalone pylint plugin encoding personal code-review preferences beyond
ruff's rule set, installed as a `uv` git dependency pinned in
`pyproject.toml`'s `[tool.uv.sources]` — see
[the plugin's README](https://github.com/gajaguar/pylint-plugin) for the full
checker list.

## Project layout

```text
.
├── pyproject.toml       # deps, ruff/mypy/pyright/pytest/coverage config
├── Makefile             # check/fix command surface
├── docs/                # tech spec, architecture, endpoint coverage matrix
├── src/clockify/        # SDK package
└── tests/
    ├── unit/            # respx-backed, offline, deterministic
    └── live/            # marker-gated (`-m live`), hits a real workspace
```
