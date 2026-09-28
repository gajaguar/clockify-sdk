# Clockify Unofficial SDK

[![CI](https://github.com/gajaguar/clockify-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/gajaguar/clockify-sdk/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue.svg)](pyproject.toml)
[![Topics](https://img.shields.io/badge/topics-python%20%7C%20sdk%20%7C%20api--client%20%7C%20clockify%20%7C%20httpx%20%7C%20pydantic-informational)](https://github.com/gajaguar/clockify-sdk)

> **Unofficial.** This project is not affiliated with, endorsed by, or
> supported by CAKE.com d.o.o. "Clockify" is a trademark of CAKE.com d.o.o.
> Use at your own risk against the [Clockify API](https://docs.clockify.me/).

Typed, synchronous Python SDK for the Clockify Working API and Reports API.
Every response is a validated, frozen [pydantic](https://docs.pydantic.dev/)
model with attribute access and real Python types — not a raw `dict`.

## Table of contents

- [About](#about)
- [Key features](#key-features)
- [Architecture](#architecture)
- [Getting started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Authentication](#authentication)
  - [Recipes](#recipes)
- [Configuration](#configuration)
- [Development](#development)
- [Platform notes](#platform-notes)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)

## About

The Clockify REST API returns plain JSON, which leaves every caller to
hand-roll response parsing, pagination, retries, and error mapping. This SDK
does that once for the Working API: validated models, a lazy pagination
iterator, retry with backoff, and a typed exception hierarchy. Reports API
support is not implemented yet — see
[`docs/sdk/coverage.md`](docs/sdk/coverage.md).

## Key features

- **Typed models everywhere.** Requests and responses are pydantic models
  with camelCase↔snake_case aliasing, not raw dicts.
- **Workspace-bound sub-clients.** `client.workspace(id)` returns a
  `WorkspaceClient` that carries the workspace ID, removing it from every
  method call.
- **Lazy pagination.** `list()` returns an iterator that follows Clockify's
  offset pagination; `list_page()` exposes one page at a time for manual
  cursor control.
- **Built-in retry.** `429` and `5xx` responses retry with jittered backoff,
  honoring `Retry-After` and skipping retries on non-idempotent commands.
- **Typed exception hierarchy.** HTTP failures map to specific
  `clockify.errors` exceptions (`AuthenticationError`, `NotFoundError`,
  `RateLimitError`, and others) instead of a generic HTTP exception.
- **Multi-region support.** `Region.GLOBAL` and the regional Clockify hosts
  are built in; an explicit `base_url` overrides either.

## Architecture

`ClockifyClient` owns one `httpx.Client` and exposes root-level namespaces
plus `workspace(id)` / `default_workspace()`, which return a `WorkspaceClient`
bound to a workspace. See [`docs/sdk/index.md`](docs/sdk/index.md) for
the full layering (with diagrams) and how to add a new endpoint.
[`docs/sdk/coverage.md`](docs/sdk/coverage.md) is the authoritative
endpoint-to-method coverage matrix.

## Getting started

### Prerequisites

- Python 3.14 or later
- A Clockify API key (`CLOCKIFY_API_KEY`) — see [Authentication](#authentication)

Contributing to the SDK itself additionally requires
[mise](https://mise.jdx.dev) — see [Development](#development).

### Installation

Not published to PyPI. Add it as a `uv` git dependency pinned to a tag:

```bash
uv add "clockify-unofficial-sdk @ git+https://github.com/gajaguar/clockify-sdk@v0.1.0"
```

or add the source directly in `pyproject.toml`:

```toml
[project]
dependencies = ["clockify-unofficial-sdk"]

[tool.uv.sources.clockify-unofficial-sdk]
git = "https://github.com/gajaguar/clockify-sdk"
tag = "v0.1.0"
```

## Usage

### Authentication

```python
import os
from clockify import ClockifyClient

os.environ["CLOCKIFY_API_KEY"] = "..."
client = ClockifyClient()  # reads CLOCKIFY_API_KEY
client = ClockifyClient(api_key="...")  # explicit argument takes precedence

# api_key also accepts a zero-argument callable, invoked lazily on every request
# instead of once at construction time — useful for a rotating or externally-managed
# key (e.g. one read from an OS keyring by the calling application).
client = ClockifyClient(api_key=lambda: keychain.current_clockify_key())
```

The SDK's only credential sources are the `api_key` argument (string or
provider) and the `CLOCKIFY_API_KEY` environment variable as its sole
fallback. It has no OS keyring/keychain integration, no 1Password or other
password-manager support, no OAuth/SSO flow, and no interactive prompts —
that is an application-level concern for whatever consumes this SDK (see
[`clockify-cli`](https://github.com/gajaguar/clockify-cli) for an example
that layers all of that on top).

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

Handle API errors with the typed exception hierarchy:

```python
from clockify.errors import NotFoundError, RateLimitError

try:
    project = workspace.projects.get("does-not-exist")
except NotFoundError:
    print("project not found")
except RateLimitError:
    print("rate limited even after built-in retries")
```

Manage pagination directly instead of iterating the full collection:

```python
page = workspace.projects.list_page(page=1, page_size=50)
print(len(page.items), page.items)
```

## Configuration

| Variable                     | Where it's read                | Default        | Description                                            |
| ---------------------------- | ------------------------------ | -------------- | ------------------------------------------------------ |
| `CLOCKIFY_API_KEY`           | `ClockifyClient()`             | none, required | API key used when `api_key` is not passed explicitly.  |
| `CLOCKIFY_TEST_API_KEY`      | `tests/live` suite (`-m live`) | none           | Enables the live smoke tests against a real workspace. |
| `CLOCKIFY_TEST_WORKSPACE_ID` | `tests/live` suite (`-m live`) | none           | Workspace the live smoke tests run against.            |

`ClockifyClient(options=ClientOptions(...))` accepts:

| Parameter          | Type                                | Default         | Description                                                |
| ------------------ | ----------------------------------- | --------------- | ---------------------------------------------------------- |
| `region`           | `Region`                            | `Region.GLOBAL` | Selects the Working/Reports API hosts. See `Region` below. |
| `base_url`         | `str \| None`                       | region default  | Overrides the Working API host.                            |
| `reports_base_url` | `str \| None`                       | region default  | Overrides the Reports API host.                            |
| `timeout`          | `float`                             | `30.0`          | `httpx` request timeout in seconds.                        |
| `retry`            | `RetryPolicy \| None`               | see below       | Retry behavior for `429`/`5xx` responses.                  |
| `event_hooks`      | `dict[str, list[Callable]] \| None` | `None`          | Passed through to `httpx.Client`.                          |

`RetryPolicy` defaults: `max_attempts=3`, `backoff_base=0.5`,
`max_backoff=30.0`, `retry_statuses={429, 500, 502, 503, 504}`,
`respect_retry_after=True`.

`Region` members: `GLOBAL`, `EU_CENTRAL_1`, `US_EAST_2`, `EU_WEST_2`,
`AP_SOUTHEAST_2`, `DEVELOPER`. Only the `GLOBAL` hosts are verified against a
live account — the others are transcribed from Clockify's docs; pass an
explicit `base_url`/`reports_base_url` if one turns out to be wrong.

## Development

```bash
make install   # sync Python deps, install node tooling, install pre-commit hook
make check     # read-only gate: lint, format-check, mypy, pyright,
               # md-lint, spell, pylint, commits-check
make fix       # apply safe auto-fixes (format, ruff --fix, markdownlint --fix)
make test      # run the test suite
make build     # build the sdist and wheel into dist/
```

Run `make help` for the full target list; every target accepts
`FILES="..."` to scope to specific paths/globs.

### Toolchain

- **uv** — dependency management and virtualenvs (`hatchling` build backend)
- **httpx** — HTTP transport
- **pydantic** — request/response models and validation
- **ruff** — linting and formatting (`lint.select = ["ALL"]`, curated ignores)
- **mypy** + **pyright** — static type checking
- **pytest** + **pytest-cov** + **respx** — testing, coverage, HTTP mocking
- **markdownlint-cli2** + **cspell** (pnpm, dev-only) — Markdown lint & spell check
- **checkmake** — lints the `Makefile` itself (`make makefile-lint`)
- **pylint** + a custom checker plugin (a `uv` git dependency pinned in
  `pyproject.toml`) — custom checkers for personal-preference rules ruff
  doesn't cover (e.g. no docstrings — see below)
- **pre-commit** — git hook running the generic hygiene hooks
  (trailing-whitespace, end-of-file-fixer, check-yaml, check-toml,
  check-merge-conflict, check-added-large-files, mixed-line-ending),
  markdownlint-cli2, cspell, checkmake, ruff, ruff-format, mypy, and pylint
  before each commit
- **mise** — pins the whole toolchain version (Python, uv, node, pnpm,
  pre-commit, checkmake) in `mise.toml`
- **conventional-git** — validates commit messages and branch names against
  Conventional Commits/Conventional Branch (`make commits-check`)

#### Endpoint comments

Docstrings are forbidden (see [`AGENTS.md`](AGENTS.md)), so each resource
method carries a one-line `# METHOD /path` comment above its definition, and
the authoritative endpoint-to-method mapping lives in
[`docs/sdk/coverage.md`](docs/sdk/coverage.md).

### Project layout

```text
.
├── pyproject.toml       # deps, ruff/mypy/pyright/pytest/coverage config
├── Makefile             # check/fix command surface (root: shared targets)
├── mk/python.mk         # Python-specific targets, wired into the Makefile
├── mise.toml            # pinned toolchain versions
├── docs/                # OKF bundle: SDK architecture, endpoint coverage, conventions
├── src/clockify/        # SDK package
└── tests/
    ├── unit/            # respx-backed, offline, deterministic
    └── live/            # marker-gated (`-m live`), hits a real workspace
```

## Platform notes

- **CI** (`.github/workflows/ci.yml`, `python.yml`) runs `make check && make
  test` on every push and pull request against `main`. `make check && make
  test` is still the gate to run locally before every commit — a local
  `--no-verify` bypass of the pre-commit hook is the case CI exists to catch.
- **`requires-python = ">=3.14"`** excludes most current Python installations
  (3.11–3.13); this is a deliberate, revisitable floor, accepted to keep
  modern-syntax features (PEP 695 generics, `StrEnum`, `datetime.UTC`)
  available now and lowered later without a breaking change.
- `mise.toml`'s `[env]` forces `uv` onto the mise-provided interpreter
  (`UV_PYTHON_PREFERENCE = "only-system"`, `UV_PYTHON_DOWNLOADS = "never"`),
  so `.python-version` is intentionally absent — mise is the single source
  of truth for the pinned Python version.
- Clockify rate limits differ by plan and are not fully documented upstream;
  retry defaults are conservative and configurable — see
  [`src/clockify/retry.py`](src/clockify/retry.py).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Security

Report suspected vulnerabilities to <dev@gajaguar.com> instead of opening a
public issue. A Clockify API key grants full access to a workspace — never
commit one, and rotate immediately if one is exposed.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
