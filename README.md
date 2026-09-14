# Clockify Unofficial SDK

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Topics](https://img.shields.io/badge/topics-python%20%7C%20sdk%20%7C%20api--client%20%7C%20clockify%20%7C%20httpx%20%7C%20pydantic-informational)](https://github.com/gajaguar/clockify-sdk)

> **Unofficial.** This project is not affiliated with, endorsed by, or
> supported by CAKE.com d.o.o. "Clockify" is a trademark of CAKE.com d.o.o.
> Use at your own risk against the [Clockify API](https://docs.clockify.me/).

Typed, synchronous Python SDK for the Clockify Working API and Reports API.

See [`docs/TECH_SPEC.md`](docs/TECH_SPEC.md) for the full technical
specification, [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for how the
client is layered, and [`docs/coverage.md`](docs/coverage.md) for the endpoint
coverage matrix.

## Requirements

- [mise](https://mise.jdx.dev) — pins the toolchain (`mise.toml`: Python 3.14,
  uv, node, pnpm, pre-commit, checkmake); run `mise install`, then
  `make install`
- A Clockify API key (`CLOCKIFY_API_KEY`) — see [Authentication](#authentication)

## Usage

```bash
make install   # sync Python deps, install node tooling, install pre-commit hook
make check     # read-only gate: lint, format-check, mypy, pyright,
               # md-lint, spell, pylint
make fix       # apply safe auto-fixes (format, ruff --fix, markdownlint --fix)
make test      # run the test suite
```

Run `make help` for the full target list.

### Authentication

```python
import os
from clockify import ClockifyClient

os.environ["CLOCKIFY_API_KEY"] = "..."
client = ClockifyClient()  # reads CLOCKIFY_API_KEY
client = ClockifyClient(api_key="...")  # explicit argument takes precedence
```

### Recipes

Start a timer, list today's running/finished entries, then stop it:

```python
import datetime

from clockify import ClockifyClient, TimeEntryCreate, TimeEntryFilter

with ClockifyClient() as client:
    workspace = client.default_workspace()
    user = client.user.me()

    payload = TimeEntryCreate(description="Writing docs")
    started = workspace.time_entries.start(user.id, payload)
    print(f"started {started.id}")

    today = datetime.datetime.now(datetime.UTC)
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    entry_filter = TimeEntryFilter(start=today)
    for entry in workspace.time_entries.list(user.id, entry_filter=entry_filter):
        print(entry.description, entry.time_interval.duration)

    stopped = workspace.time_entries.stop(user.id)
    print(stopped.time_interval.duration)
```

### Command convention: `check` vs `fix`

Targets are split by whether they mutate files:

| Prefix / umbrella   | Behavior                                                             | Example targets                                                                               |
| ------------------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `check` (read-only) | Reports problems, exits non-zero, never writes. This is the CI gate. | `lint`, `format-check`, `mypy`, `pyright`, `typecheck`, `md-lint`, `spell`, `pylint`, `check` |
| `fix` (writable)    | Mutates files in place.                                              | `format`, `lint-fix`, `lint-fix-unsafe`, `md-fix`, `fix`, `fix-unsafe`                        |

All targets accept `FILES="..."` to scope to specific paths/globs, e.g.
`make lint FILES="src/clockify/client.py"`.

### Toolchain

- **uv** — dependency management and virtualenvs (`hatchling` build backend)
- **httpx** — HTTP transport
- **pydantic** — request/response models and validation
- **ruff** — linting and formatting (`lint.select = ["ALL"]`, curated ignores)
- **mypy** + **pyright** — static type checking
- **pytest** + **pytest-cov** + **respx** — testing, coverage, HTTP mocking
- **markdownlint-cli2** + **cspell** (pnpm, dev-only) — Markdown lint & spell check
- **checkmake** — lints the `Makefile` itself (`make makefile-lint`)
- **pylint** + [`pylint-plugin`](https://github.com/gajaguar/pylint-plugin)
  (uv git dependency) — custom checkers for personal-preference rules ruff
  doesn't cover (e.g. no docstrings — see below)
- **pre-commit** — git hook running the generic hygiene hooks
  (trailing-whitespace, end-of-file-fixer, check-yaml, check-toml,
  check-merge-conflict, check-added-large-files, mixed-line-ending),
  markdownlint-cli2, cspell, checkmake, ruff, ruff-format, mypy, and pylint
  before each commit
- **mise** — pins the whole toolchain version (Python, uv, node, pnpm,
  pre-commit, checkmake) in `mise.toml`

#### Docstring policy

This project does not use docstrings — use comments only where the *why*
isn't obvious from the code. `pylint-plugin`'s `app-no-docstrings`
(W9001) checker fails `make check`/`make pylint` if any function, method, or
class has one. Because the SDK can't rely on docstrings for endpoint
reference, each resource method carries a one-line `# METHOD /path` comment
above its definition, and the authoritative endpoint-to-method mapping lives
in [`docs/coverage.md`](docs/coverage.md).

#### Custom pylint checkers (`pylint-plugin`)

A standalone pylint plugin encoding personal code-review preferences beyond
ruff's rule set, installed as a `uv` git dependency pinned in
`pyproject.toml`'s `[tool.uv.sources]` — see
[the plugin's README](https://github.com/gajaguar/pylint-plugin) for the full
checker list.

### Project layout

```text
.
├── pyproject.toml       # deps, ruff/mypy/pyright/pytest/coverage config
├── Makefile             # check/fix command surface (root: shared targets)
├── mk/python.mk         # Python-specific targets, wired into the Makefile
├── mise.toml            # pinned toolchain versions
├── docs/                # tech spec, architecture, endpoint coverage matrix
├── src/clockify/        # SDK package
└── tests/
    ├── unit/            # respx-backed, offline, deterministic
    └── live/            # marker-gated (`-m live`), hits a real workspace
```

## Platform notes

- **No CI pipeline.** `make check && make test` is the gate; run it before
  every commit and always before tagging a release (accepted trade-off — see
  `docs/TECH_SPEC.md` §11, risk R2). GitHub Actions is planned before `1.0.0`.
- **`requires-python = ">=3.14"`** excludes most current Python installations
  (3.11–3.13); this is a deliberate, revisitable floor — see `docs/TECH_SPEC.md`
  §11, risk R1.
- `mise.toml` forces `uv` onto the mise-provided interpreter
  (`python-preference = "only-system"`, `python-downloads = "never"` in
  `pyproject.toml`'s `[tool.uv]`), so `.python-version` is intentionally
  absent — mise is the single source of truth for the pinned Python version.
- Clockify rate limits differ by plan and are not fully documented upstream;
  retry defaults are conservative and configurable — see
  [`src/clockify/retry.py`](src/clockify/retry.py).

## Open items

- Reports API (`summary`, `detailed`, `weekly`, shared reports) and user-group
  membership management (`add_user` / `remove_user`) are not yet implemented
  — see the `planned` rows in [`docs/coverage.md`](docs/coverage.md).
- Whether Expenses and Invoices are exposed under the v1 Working API for the
  target plan is unconfirmed; see `docs/TECH_SPEC.md` §12.
- The real per-endpoint `page-size` maximum is unconfirmed (reported values
  range from 200 to 5000); see `docs/TECH_SPEC.md` §12.
