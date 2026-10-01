# Clockify Unofficial SDK

[![CI](https://github.com/gajaguar/clockify-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/gajaguar/clockify-sdk/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/clockify-unofficial-sdk.svg)](https://pypi.org/project/clockify-unofficial-sdk/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue.svg)](pyproject.toml)
[![Topics](https://img.shields.io/badge/topics-python%20%7C%20sdk%20%7C%20api--client%20%7C%20clockify%20%7C%20httpx%20%7C%20pydantic-informational)](https://github.com/gajaguar/clockify-sdk)

> **Unofficial.** This project is not affiliated with, endorsed by, or
> supported by CAKE.com d.o.o. "Clockify" is a trademark of CAKE.com d.o.o.
> Use at your own risk against the [Clockify API](https://docs.clockify.me/).

Typed Python SDK, sync and async, for the Clockify Working API and Reports API.
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
[`docs/sdk/coverage.md`](https://github.com/gajaguar/clockify-sdk/blob/main/docs/sdk/coverage.md).

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
- **Sync and async.** `ClockifyClient` uses `httpx.Client`;
  `AsyncClockifyClient` exposes the same resources on `httpx.AsyncClient`.
- **Typed exception hierarchy.** HTTP failures map to specific
  `clockify.errors` exceptions (`AuthenticationError`, `NotFoundError`,
  `RateLimitError`, and others) instead of a generic HTTP exception.
- **Webhooks.** `workspace.webhooks` creates, lists, updates and deletes
  webhooks and rotates their token; `verify_signature` checks that a delivery
  came from Clockify.
- **Approvals.** `workspace.approvals` lists approval requests, submits and
  resubmits timesheets and expenses, and approves, rejects or withdraws them.
- **Expenses.** `workspace.expenses` and `workspace.expense_categories` manage
  expenses (with their receipt file) and their categories. Pro plan only, and
  not verified against a real response.
- **Multi-region support.** `Region.GLOBAL` and the regional Clockify hosts
  are built in; an explicit `base_url` overrides either.

## Architecture

`ClockifyClient` owns one `httpx.Client` and exposes root-level namespaces
plus `workspace(id)` / `default_workspace()`, which return a `WorkspaceClient`
bound to a workspace. See [`docs/sdk/index.md`][sdk-index] for
the full layering (with diagrams) and how to add a new endpoint.
[`docs/sdk/coverage.md`][sdk-coverage] is the authoritative
endpoint-to-method coverage matrix.

## Getting started

### Prerequisites

- Python 3.14 or later
- A Clockify API key (`CLOCKIFY_API_KEY`) — see [Authentication](#authentication)

Contributing to the SDK itself additionally requires
[mise](https://mise.jdx.dev) — see [Development](#development).

### Installation

```bash
uv add clockify-unofficial-sdk
# or
pip install clockify-unofficial-sdk
```

To track an unreleased commit instead, use a `uv` git dependency:

```bash
uv add "clockify-unofficial-sdk @ git+https://github.com/gajaguar/clockify-sdk"
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

An add-on authenticates with the token Clockify issues to it instead of an
API key. The SDK then sends `X-Addon-Token` in place of `X-Api-Key`:

```python
client = ClockifyClient(addon_token="...")
client = ClockifyClient()  # reads CLOCKIFY_ADDON_TOKEN if no API key is set
client = ClockifyClient(addon_token=lambda: store.current_token())
```

An API key and an add-on token are mutually exclusive: passing both
arguments, or setting both environment variables with no argument, raises a
`ConfigurationError`. An explicit argument beats the other credential's
environment variable. Add-on tokens are rate limited to 50 requests per
second per workspace, and an add-on usually sets
`options=ClientOptions(base_url=...)` to the backend URL Clockify gives it.

The SDK's only credential sources are the `api_key` and `addon_token`
arguments (string or provider) and, as their sole fallbacks, the
`CLOCKIFY_API_KEY` and `CLOCKIFY_ADDON_TOKEN` environment variables. It has
no OS keyring/keychain integration, no 1Password or other password-manager
support, no OAuth/SSO flow, and no interactive prompts — that is an
application-level concern for whatever consumes this SDK (see
[`clockify-cli`](https://github.com/gajaguar/clockify-cli) for an example
that layers all of that on top).

#### Getting a credential

1. Open your profile menu and choose **Profile settings**.
2. Open the **Advanced** tab and choose **Manage API keys**.
3. Choose **Generate new** and give the key a name.
4. Copy the key. Clockify does not show it again once you leave the page.

Any user can generate keys for their own account, and a key can be renamed
or deleted from the same page. Clockify has no OAuth flow. An add-on token
comes from Clockify when the add-on is installed in a workspace.

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

Run a summary report for a date range, grouped by project (Reports API,
always requested as JSON):

```python
import datetime

from clockify import ClockifyClient, ReportGroup, SummaryFilter, SummaryReportRequest

with ClockifyClient() as client:
    workspace = client.default_workspace()
    request = SummaryReportRequest(
        date_range_start=datetime.datetime(2026, 8, 1, tzinfo=datetime.UTC),
        date_range_end=datetime.datetime(2026, 8, 31, 23, 59, 59, tzinfo=datetime.UTC),
        summary_filter=SummaryFilter(groups=[ReportGroup.PROJECT]),
    )
    report = workspace.reports.summary(request)
    for row in report.group_one or []:
        print(row.name, row.duration)
```

A weekly report takes a `group` and a `subgroup`, which is `WeeklySubgroup.TIME`
or `WeeklySubgroup.EARNINGS` rather than a `ReportGroup`. The API rejects any
range that is not exactly 7 days long ("Please select date range of exactly 7
days for weekly report"):

```python
import datetime

from clockify import ReportGroup, WeeklyFilter, WeeklyReportRequest, WeeklySubgroup

start = datetime.datetime(2026, 8, 3, tzinfo=datetime.UTC)
request = WeeklyReportRequest(
    date_range_start=start,
    date_range_end=start + datetime.timedelta(days=7),
    weekly_filter=WeeklyFilter(group=ReportGroup.PROJECT, subgroup=WeeklySubgroup.TIME),
)
```

Clockify answers a report request with a 403 (`ForbiddenError`) when the
workspace's plan or the user's role does not allow reports; a FREE workspace
did. The report models are covered by unit tests with mocked responses, but they
have not been checked against a live response yet.

Use the async client with `async with` and `await`:

```python
import asyncio

from clockify import AsyncClockifyClient


async def main() -> None:
    async with AsyncClockifyClient() as client:
        workspace = await client.default_workspace()
        async for project in workspace.projects.list():
            print(project.name)


asyncio.run(main())
```

A credential provider runs inside the event loop, so it must not block, and
`event_hooks` passed to the async client must be coroutine functions. See
[`docs/sdk/async-client.md`](docs/sdk/async-client.md).

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

Register a webhook, then check each delivery in your receiver:

```python
from clockify import (
    SIGNATURE_HEADER,
    WebhookCreate,
    WebhookEvent,
    WebhookTriggerSourceType,
    verify_signature,
)

webhook = workspace.webhooks.create(
    WebhookCreate(
        url="https://example.com/clockify",
        webhook_event=WebhookEvent.NEW_TIMER_STARTED,
        trigger_source=[workspace.id],
        trigger_source_type=WebhookTriggerSourceType.WORKSPACE_ID,
    )
)
stored_token = webhook.auth_token  # keep it in your own secret store

# In the receiver, with `headers` from the incoming request:
if not verify_signature(headers.get(SIGNATURE_HEADER), stored_token):
    raise PermissionError("not sent by Clockify")
```

`workspace.webhooks.list()` makes one request and returns every webhook; the
endpoint has no pages, so `list_page()` raises `NotImplementedError`.
`regenerate_token(id)` issues a new token and invalidates the old one. See
[`docs/sdk/webhooks.md`](docs/sdk/webhooks.md).

Submit a timesheet for approval and decide on it (Standard plan or above; a
lower plan answers `403`, raised as `ForbiddenError`):

```python
import datetime

from clockify import (
    ApprovalPeriod,
    ApprovalRequestCreate,
    ApprovalRequestFilter,
    ApprovalRequestType,
    ApprovalRequestUpdate,
    ApprovalState,
)

request = workspace.approvals.submit(
    ApprovalRequestType.TIMESHEET,
    ApprovalRequestCreate(
        period_start=datetime.datetime(2026, 9, 28, tzinfo=datetime.UTC),
        period=ApprovalPeriod.WEEKLY,
    ),
)
workspace.approvals.update(request.id, ApprovalRequestUpdate(state=ApprovalState.APPROVED))

for details in workspace.approvals.list(request_filter=ApprovalRequestFilter(status=ApprovalState.PENDING)):
    print(details.approval_request.id, details.tracked_time)
```

`submit_for_user(user_id, type, payload)` submits on behalf of another user and
`resubmit(payload)` resubmits rejected or withdrawn entries.

Create an expense category and an expense with its receipt (Pro plan; a lower
plan answers `403`, raised as `ForbiddenError`). These models follow the OpenAPI
spec and have **not been verified against a real response**, because the account
used to build the SDK is on the Free plan:

```python
import datetime

from clockify import ExpenseCategoryCreate, ExpenseCreate, ExpenseFile

category = workspace.expense_categories.create(ExpenseCategoryCreate(name="Travel"))
expense = workspace.expenses.create(
    ExpenseCreate(
        user_id=user.id,
        category_id=category.id,
        project_id=project.id,
        date=datetime.datetime(2026, 9, 30, tzinfo=datetime.UTC),
        amount=12.5,
        file=ExpenseFile("receipt.pdf", receipt_bytes, "application/pdf"),
    )
)
```

The file is sent as bytes, not a stream, so a retry can resend it. Clockify has
no endpoint to read one category, so `expense_categories.get()` raises
`NotImplementedError`; downloading the receipt is not covered yet. See
[`docs/sdk/multipart-uploads.md`](docs/sdk/multipart-uploads.md).

Manage pagination directly instead of iterating the full collection:

```python
page = workspace.projects.list_page(page=1, page_size=50)
print(len(page.items), page.items)
```

## Configuration

| Variable                     | Where it's read                | Default        | Description                                            |
| ---------------------------- | ------------------------------ | -------------- | ------------------------------------------------------ |
| `CLOCKIFY_API_KEY`           | `ClockifyClient()`             | none, required | API key used when `api_key` is not passed explicitly.  |
| `CLOCKIFY_ADDON_TOKEN`       | `ClockifyClient()`             | none           | Add-on token used when neither credential is passed.   |
| `CLOCKIFY_TEST_API_KEY`      | `tests/live` suite (`-m live`) | none           | Enables the live smoke tests against a real workspace. |
| `CLOCKIFY_TEST_WORKSPACE_ID` | `tests/live` suite (`-m live`) | none           | Workspace the live smoke tests run against.            |
| `CLOCKIFY_TEST_REGION`       | `tests/live` suite (`-m live`) | `GLOBAL`       | `Region` the reports smoke test runs against.          |

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
`AP_SOUTHEAST_2`, `DEVELOPER`. The hosts follow Clockify's docs and every one
answers, but only the regions with a test account are verified end to end with
an authenticated call; pass an explicit `base_url`/`reports_base_url` if one
turns out to be wrong.

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

Docstrings are forbidden (see [`AGENTS.md`][agents]), so each resource
method carries a one-line `# METHOD /path` comment above its definition, and
the authoritative endpoint-to-method mapping lives in
[`docs/sdk/coverage.md`](https://github.com/gajaguar/clockify-sdk/blob/main/docs/sdk/coverage.md).

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
  [`src/clockify/retry.py`](https://github.com/gajaguar/clockify-sdk/blob/main/src/clockify/retry.py).

## Contributing

See [`CONTRIBUTING.md`](https://github.com/gajaguar/clockify-sdk/blob/main/CONTRIBUTING.md).

## Security

Report suspected vulnerabilities through GitHub's
[private vulnerability reporting](https://github.com/gajaguar/clockify-sdk/security/advisories/new),
or email <dev@gajaguar.com>, instead of opening a public issue. A Clockify
API key grants full access to a workspace — never commit one, and rotate
immediately if one is exposed.

## License

Distributed under the MIT License. See [LICENSE][license] for details.

[sdk-index]: https://github.com/gajaguar/clockify-sdk/blob/main/docs/sdk/index.md
[sdk-coverage]: https://github.com/gajaguar/clockify-sdk/blob/main/docs/sdk/coverage.md
[agents]: https://github.com/gajaguar/clockify-sdk/blob/main/AGENTS.md
[license]: https://github.com/gajaguar/clockify-sdk/blob/main/LICENSE
