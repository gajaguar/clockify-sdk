# Technical Specification — Clockify Unofficial Python SDK

- **Status:** Draft, pending approval
- **Date:** 2026-08-26
- **Owner:** <dev@gajaguar.com>
- **Repository:** `gajaguar/clockify-sdk`
- **Distribution name:** `clockify-unofficial-sdk`
- **Import name:** `clockify`

---

## 1. Goal

Provide a typed, synchronous Python client covering every action documented for
the Clockify **Working (core) API**, the **Reports API**, and **user
management**, so that a consumer never has to hand-build an HTTP request against
`api.clockify.me`.

### 1.1 In scope (v1)

| Surface            | Base path                            | Notes                                                                                                                      |
| ------------------ | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| Working / core API | `https://api.clockify.me/api/v1`     | Workspaces, projects, tasks, time entries, clients, tags, custom fields, groups, invoices, expenses if documented under v1 |
| Reports API        | `https://reports.api.clockify.me/v1` | Summary, detailed, weekly, shared reports                                                                                  |
| User management    | Working API subset                   | Users, memberships, roles, user groups, workspace settings for users                                                       |

### 1.2 Out of scope (v1)

- PTO / Time-off API (`pto.api.clockify.me`)
- Approvals API
- Webhooks API and webhook receiver helpers
- Async client
- CLI

These are deferred, not rejected. The architecture below reserves room for each
as an additive namespace.

### 1.3 Non-goals

- No local caching layer, no ORM, no persistence.
- No business logic on top of Clockify semantics (e.g. no "sum my week" helper).
  The SDK maps the API; aggregation is the caller's concern.

---

## 2. Decisions

| #   | Decision                 | Choice                                                                 | Rationale                                                                                                                                           |
| --- | ------------------------ | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1  | Concurrency model        | **Sync only** (`httpx.Client`)                                         | Target use is scripts, jobs and back-office integrations. An async client can be added later without breaking the sync surface.                     |
| D2  | Model layer              | **Pydantic v2**                                                        | Runtime validation, camelCase↔snake_case aliasing, good errors, first-class mypy support.                                                           |
| D3  | Source of truth          | **Hand-written from official docs**                                    | Clockify publishes no dependable OpenAPI document. Generation would require more patching than authoring.                                           |
| D4  | Public shape             | **Workspace-bound sub-clients**                                        | Removes the repeated `workspace_id` argument that would otherwise appear on ~90% of methods.                                                        |
| D5  | Python floor             | **`>=3.14`**                                                           | Inherited from the template, unchanged. See §11 Risks.                                                                                              |
| D6  | Build backend / tooling  | **uv + hatchling**, ruff `ALL`, mypy `strict`, pyright, pytest         | Inherited from `python-app-template`, unchanged.                                                                                                    |
| D7  | CI                       | **None for v1**                                                        | Local `pre-commit` hook plus `make check` is the gate. See §11 Risks.                                                                               |
| D8  | Reports typing           | Pydantic models for documented fields, `extra="allow"`                 | Report payload shape varies with the filter set; unknown keys must survive rather than raise.                                                       |
| D9  | Time types               | `datetime` (tz-aware UTC) and `timedelta`                              | Clockify emits ISO-8601 instants and ISO-8601 durations (`PT1H30M`). Conversion happens in validators/serializers.                                  |
| D10 | Retries                  | Built in for `429` and `5xx`                                           | See §7.3.                                                                                                                                           |
| D11 | Architecture style       | **Not DDD.** Generic resource base + Strategy + transport Decorator    | The domain is Clockify's, not ours; there is no local invariant to enforce. See §5.                                                                 |
| D12 | Identifiers              | **Value Object types** (`WorkspaceId`, `ProjectId`, …), not bare `str` | Transposing two `str` arguments is the most likely user-facing bug. See §5.3.                                                                       |
| D13 | Command-Query Separation | **Adopted for side effects; commands still return their result**       | Queries mutate nothing, which is what makes semantic retry classification correct (§7.3). Void commands would cost a round trip and race. See §5.5. |

---

## 3. Public API

### 3.1 Construction

```python
from clockify import ClientOptions, ClockifyClient, Region

client = ClockifyClient()  # reads CLOCKIFY_API_KEY
client = ClockifyClient(api_key="...")  # explicit wins over env
client = ClockifyClient(options=ClientOptions(region=Region.EU_CENTRAL_1))
client = ClockifyClient(
    options=ClientOptions(
        base_url="https://euc1.clockify.me/api/v1", reports_base_url="https://euc1.clockify.me/report/v1"
    )
)
```

`api_key` stays a direct keyword because it is the one argument nearly every
call site sets. Everything else that shapes a client (`region`, `base_url`,
`reports_base_url`, `timeout`, `retry`, `event_hooks`) is a Parameter Object
(`ClientOptions`, a frozen dataclass in `config.py`) rather than seven
individual keywords on `__init__` — see §5.2's row on it and the coding-style
skill's "long-parameter-list" rule.

Resolution order for the key: `api_key` argument → `CLOCKIFY_API_KEY` →
`MissingCredentialsError` at construction time, not at first request.

`Region` is an enum covering the documented hosts (global, `euc1`, `use2`,
`euw2`, `apse2`, `developer`). An explicit `base_url` (on `ClientOptions`)
overrides the region and is the seam used to point tests at a fake server.

The client is a context manager and owns one `httpx.Client`:

```python
with ClockifyClient() as client:
    ...
```

### 3.2 Root namespace

Endpoints that are not workspace-scoped live on the root client.

```python
client.user.me()                     -> User
client.workspaces.list()             -> list[Workspace]
client.workspaces.get(workspace_id)  -> Workspace
```

### 3.3 Workspace-bound sub-client

```python
ws = client.workspace("64a1f...")    # cheap, no I/O
ws = client.default_workspace()      # one call to /user, then binds

ws.projects.list(archived=False)     -> Iterator[Project]
ws.projects.get(project_id)          -> Project
ws.projects.create(ProjectCreate(name="Apollo", client_id=...)) -> Project
ws.projects.update(project_id, ProjectUpdate(...))              -> Project
ws.projects.delete(project_id)                                  -> None

ws.time_entries.create(...)
ws.time_entries.stop(user_id)
ws.tasks.list(project_id)
ws.clients.list()
ws.tags.list()
ws.users.list()
ws.user_groups.list()
ws.custom_fields.list()
ws.reports.summary(SummaryReportRequest(...))  -> SummaryReport
ws.reports.detailed(DetailedReportRequest(...)) -> Iterator[DetailedReportEntry]
```

`Workspace` sub-clients share the parent's transport; they hold no independent
connection or lifecycle.

### 3.4 Method naming contract

| Clockify verb              | SDK method                                    | CQS kind                 |
| -------------------------- | --------------------------------------------- | ------------------------ |
| `GET` collection           | `list(...)` → auto-paginating `Iterator[T]`   | query                    |
| `GET` collection, one page | `list_page(page=1, page_size=50)` → `Page[T]` | query                    |
| `GET` single               | `get(id)`                                     | query                    |
| `POST`                     | `create(payload)` → created model             | command (non-idempotent) |
| `PUT` / `PATCH`            | `update(id, payload)` → updated model         | command (idempotent)     |
| `DELETE`                   | `delete(id)` → `None`                         | command (idempotent)     |

Every method declares a CQS kind (§5.5). The declaration is not decoration —
the retry transport reads it to decide `5xx` eligibility (§7.3).

Deviations from this table are permitted only where Clockify's endpoint has no
CRUD analogue (e.g. `time_entries.stop`, `reports.detailed`), and each must
carry a `# METHOD /path` comment naming the underlying HTTP method and path
(this repo bans docstrings — see §9). Report methods are queries despite being
`POST` on the wire.

---

## 4. Models

### 4.1 Conventions

- Every model derives from a shared `ClockifyModel(BaseModel)` base with
  `alias_generator=to_camel`, `populate_by_name=True`, `extra="allow"`.
- Public attribute names are `snake_case`; wire names are camelCase via alias.
- Read models (`Project`) and write models (`ProjectCreate`, `ProjectUpdate`)
  are separate types. Write models must not carry server-assigned fields.
- Read models are frozen; the server owns the truth and local objects are
  snapshots. Mutation is expressed only by sending a write model (§5.3).
- Identifier fields are Value Object types from `ids.py`, not bare `str`
  (§5.3).
- Optional-on-write fields use a sentinel so that "omit" and "set to null" are
  distinguishable; serialization uses `exclude_unset=True`.
- Enumerated Clockify values (`ProjectStatus`, `TimeEntryType`, `Role`,
  `EstimateType`, …) are `StrEnum`, tolerant of unknown values via a fallback
  member or `str` union — Clockify adds values without notice.

### 4.2 Time handling

| Wire                     | Python                     |
| ------------------------ | -------------------------- |
| `"2026-08-26T10:00:00Z"` | `datetime` (tz-aware, UTC) |
| `"PT1H30M"`              | `timedelta`                |
| `"2026-08-26"`           | `date`                     |

Two reusable annotated types, `ClockifyInstant` and `ClockifyDuration`, carry the
validator/serializer pair. ISO-8601 duration parsing and formatting is
implemented in-repo (`clockify._time`) rather than pulled from a dependency;
Clockify only emits the `PnDTnHnMnS` subset.

---

## 5. Design patterns

The SDK is a faithful mapping of an API it does not own. That constraint
decides which patterns apply and which are actively harmful.

### 5.1 Why not Domain-Driven Design

DDD was evaluated and rejected as an architecture. Three reasons, in order of
weight:

1. **The domain is not ours.** DDD's center of gravity is aggregates enforcing
   invariants. Clockify's server is the sole authority on every invariant that
   matters (overlapping time entries, name uniqueness, billable-rate rules).
   Any invariant encoded in a local aggregate is a guess about someone else's
   business rules and drifts silently when they change.
2. **There is no domain logic to model.** §1.3 already commits to this as a
   non-goal. The dominant risks here are surface area, transport correctness,
   and drift from the docs; DDD addresses none of them.
3. **A translated vocabulary harms an SDK.** Users arrive holding the Clockify
   docs. Renaming their concepts forces every user to translate back, and turns
   `coverage.md` from a mapping into a translation table. Clockify's vocabulary
   is the ubiquitous language and it is already fixed.

Related trap: `ws.projects` resembles a Repository. It is not one. Collection
semantics — identity map, unit of work, in-memory illusion — are wrong over
HTTP, where every access costs latency, paginates, and can rate-limit
mid-iteration. It is the Resource pattern; the shared shape is coincidence.

DDD belongs in applications *built on* this SDK, where the consumer owns the
domain and this package is the infrastructure their anti-corruption layer
wraps. That arrangement works better the thinner and more literal this SDK
stays.

### 5.2 Patterns adopted

| Pattern                       | Applied to                                      | Why                                                                                                 |
| ----------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Generic resource base class   | `resources/base.py`                             | Dominant risk is surface area; writes the CRUD five once instead of 40+ times                       |
| Strategy                      | `RetryPolicy`, auth scheme                      | Plan-dependent rate limits need a different policy, not a tuned number                              |
| Decorator (transport wrapper) | retry/backoff as an `httpx.BaseTransport`       | Composes, tests standalone, keeps `request()` linear, doubles as the user injection point           |
| Facade                        | `ClockifyClient`                                | One entry point over httpx, auth, retries, pagination                                               |
| Iterator                      | `list()` → `Iterator[T]`                        | Lazy pagination without materializing whole workspaces                                              |
| Value Object                  | ID types, `ClockifyInstant`, `ClockifyDuration` | Prevents `str`/`str` transposition; see §5.3                                                        |
| Parameter Object              | `ClientOptions` (§3.1), `ErrorBody` (§7.4)      | Collapses a long, related keyword list into one typed object instead of a many-argument constructor |

#### Generic resource base class

```python
class WorkspaceResource[TRead, TCreate, TUpdate]:
    _path: ClassVar[str]
    _read_model: type[TRead]
```

Subclasses declare path and model types; `list`, `list_page`, `get`, `create`,
`update`, `delete` are defined once on the base. PEP 695 syntax, available on
the 3.14 floor.

**Guard against over-abstraction.** Endpoints with no CRUD analogue —
`time_entries.stop`, the reports endpoints, bulk operations — are written as
plain methods on the subclass and must not be contorted into the generic
shape. The base covers the roughly 80% that is genuinely uniform; the rest
being hand-written is correct, not a defect.

#### Strategy: retry policy and auth

Retry configuration is an object, not a spread of constructor keywords:

```python
options = ClientOptions(retry=RetryPolicy(max_attempts=3, backoff=...))
client = ClockifyClient(options=options)
client = ClockifyClient(options=ClientOptions(retry=NO_RETRY))
```

Free-plan workspaces face limits differing by orders of magnitude from paid
ones (§7.3), so they need a genuinely different policy rather than a tuned
number. Auth follows the same shape — a small strategy object rather than a
conditional — which is the seam `X-Addon-Token` support arrives through
(§7.1).

### 5.3 Value Objects for identifiers

`WorkspaceId`, `ProjectId`, `TaskId`, `UserId` are distinct types, not bare
`str`. With workspace-bound sub-clients (D4) the remaining identifiers are
still threaded through many signatures, and transposing two `str` arguments is
the most likely user-facing bug in the SDK.

Accepted costs: wrapping and unwrapping at boundaries, and pydantic
serialization hooked up once on the shared base. This interacts with the
generic resource base — typed IDs let the base express `get(id: TId)` — so
both are settled together in Phase 1 rather than retrofitted.

Read models are frozen. Mutation is expressed only by sending a write model to
the server, which prevents the "I changed `project.name` locally, why didn't
it save" class of bug. The server owns the truth; local objects are snapshots.

### 5.4 Patterns explicitly rejected

| Pattern                                | Verdict                                                                                                                                                                  |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Domain-Driven Design (as architecture) | See §5.1                                                                                                                                                                 |
| Repository, Unit of Work, identity map | Wrong over HTTP; collection semantics the transport cannot honor                                                                                                         |
| Fluent builder for report requests     | Duplicates what a pydantic model with keyword arguments already does, and gives up validation-at-construction. Revisit only if reports filters prove painful in practice |
| Circuit breaker                        | Right pattern, wrong scale. For a client used from scripts and jobs, a `RateLimitError` after bounded retries is more debuggable                                         |
| `Result`/`Either` return types         | Non-idiomatic in Python, fights mypy ergonomics, and §7.4 already specifies a typed exception hierarchy consumers can `except`                                           |
| Plugin/registry for resources          | Nothing needs runtime discovery; static attributes are more discoverable and typecheck                                                                                   |

### 5.5 Command-Query Separation

CQS is adopted as a discipline on **side effects**, not as a rule about return
types. Every method is classified as a command or a query, and that
classification is load-bearing (see the retry rule in §7.3).

#### The rule

- A **query** (`get`, `list`, `list_page`, all report methods) mutates nothing —
  not server state, not client state.
- A **command** (`create`, `update`, `delete`, `time_entries.stop`) may mutate
  server state.
- The classification is semantic, **not** derived from the HTTP verb. Clockify
  serves several pure reads over `POST`; those are queries.

#### Deliberate exception: commands return their result

Strict CQS requires a command to return nothing. That is rejected here.
`POST /workspaces/{id}/projects` returns the created resource with its
server-assigned id; discarding it would force the caller into a second request
to find what they just created — an extra round trip against a tight rate
budget (§7.3), and unreliable besides, since the only available filter is a
non-unique name and the lookup races other writers.

So `create`, `update`, and `stop` return the server's representation.
`delete` returns `None`. This is the same pragmatic exception that permits
`stack.pop()`, and it is recorded here so it is not later "corrected" into
conformance.

#### Consequence: resources are stateless

No response caching, page cursors, or ETags stored on a resource object. All
per-call state lives in the iterator returned by `list()`. Without this,
"queries do not mutate" quietly becomes false on the client side, and two
interleaved iterations over the same resource corrupt each other. Frozen read
models (§5.3) close the related gap on the model side.

#### Known fuzzy cases

Bulk endpoints returning per-item results, and any upsert-shaped endpoint, are
genuinely both. Rule: name them as commands and document what they return.
Do not invent a third category.

---

## 6. Package layout

```
src/clockify/
    __init__.py            # public re-exports: ClockifyClient, Region,
                            # errors, models
    _version.py
    client.py              # ClockifyClient, WorkspaceClient
    config.py              # Region enum, ClientConfig, env resolution
    errors.py              # exception hierarchy
    ids.py                 # WorkspaceId, ProjectId, TaskId, UserId, ...
    retry.py               # RetryPolicy, NO_RETRY (public: users supply one)
    _auth.py               # auth strategy (ApiKeyAuth; AddonTokenAuth later)
    _transport.py          # httpx wiring, hooks, logging
    _retry_transport.py    # httpx.BaseTransport decorator applying RetryPolicy
    _pagination.py         # Page[T], paginate()
    _time.py               # ISO-8601 duration codec
    models/
        __init__.py
        base.py            # ClockifyModel
        common.py          # HourlyRate, Membership, ...
        workspace.py
        project.py
        task.py
        time_entry.py
        client.py
        tag.py
        user.py
        user_group.py
        custom_field.py
        reports.py
    resources/
        __init__.py
        base.py            # Resource[...], WorkspaceResource[...] generics
        workspaces.py
        projects.py
        tasks.py
        time_entries.py
        clients.py
        tags.py
        users.py
        user_groups.py
        custom_fields.py
        reports.py
tests/
    unit/                  # respx-backed, offline, deterministic
    live/                  # marker-gated, real workspace
    conftest.py
docs/
    TECH_SPEC.md
    ARCHITECTURE.md
    coverage.md            # endpoint → SDK method matrix
```

Everything prefixed with `_` is private and may change without a major version
bump. `resources/` is private in practice — instances are reached only through
`ClockifyClient`/`WorkspaceClient` attributes.

---

## 7. Transport

### 7.1 Authentication

`X-Api-Key: <key>` on every request, applied by an auth strategy object in
`_auth.py` (§5.2) rather than by a conditional in the transport.
`X-Addon-Token` is not supported in v1; adding it later means adding one
strategy implementation, with no change to `_transport.py`.

### 7.2 Pagination

Clockify collection endpoints are offset-paginated with `page` (1-indexed) and
`page-size` (default 50). `list()` returns a lazy iterator that requests pages
until a short or empty page is returned; `list_page()` exposes a single page for
callers that manage their own cursors.

- Default `page_size` used by `list()`: **200**, tunable per call and per client.
- Maximum accepted `page_size` is endpoint-dependent; the SDK does not clamp, it
  forwards the value and surfaces any server rejection as `ValidationError`.
- Iteration is lazy: no request is issued until the iterator is advanced.

### 7.3 Retries and rate limits

Documented limits (verify per plan at implementation time):

- ~10 requests/second per API key on the core API.
- 50 requests/second for addon tokens on one workspace.
- Free-plan workspaces are substantially lower (~30 requests/hour reported).
- Reports endpoints are more tightly limited than core endpoints.

Policy is carried by a `RetryPolicy` strategy object (§5.2), applied by an
`httpx.BaseTransport` decorator in `_retry_transport.py` rather than a loop
inside `request()`. Users may supply their own policy or `NO_RETRY`; the
default is:

- Retry on `429` and on `500`, `502`, `503`, `504`.
- Honor `Retry-After` when present; otherwise exponential backoff with full
  jitter, base 0.5 s.
- `max_attempts` default **3**, set on the policy; `NO_RETRY` disables.
- After exhausting retries, raise `RateLimitError` or `ServerError` carrying the
  final response.

**Retry eligibility is keyed off the CQS classification (§5.5), not off the
HTTP verb:**

| Call kind                                 | Retry on `429` | Retry on `5xx` |
| ----------------------------------------- | -------------- | -------------- |
| Query (`get`, `list`, all reports)        | yes            | yes            |
| Idempotent command (`update`, `delete`)   | yes            | yes            |
| Non-idempotent command (`create`, `stop`) | yes            | **no**         |

Rationale: the Reports API serves pure reads over `POST` (§5.5). Keying off the
verb would strip `5xx` retry protection from exactly the endpoints that are
slowest, heaviest, and most tightly rate-limited — a real defect, and the
reason CQS is specified rather than left implicit. `429` is always retryable
because the request provably did not execute; `5xx` is withheld only where a
retry could duplicate a write.

Each resource method therefore declares its kind, and the retry transport reads
that declaration rather than inspecting `request.method`.

### 7.4 Errors

```
ClockifyError                       # base; carries request + response context
├── ConfigurationError
│   └── MissingCredentialsError
├── ClockifyAPIError                # any non-2xx; .status_code, .code, .raw
│   ├── AuthenticationError         # 401
│   ├── ForbiddenError              # 403
│   ├── NotFoundError               # 404
│   ├── ValidationError             # 400, 422
│   ├── ConflictError               # 409
│   ├── RateLimitError              # 429; .retry_after
│   └── ServerError                 # 5xx
└── TransportError                  # connect/read timeouts, DNS, TLS
```

Clockify's error body (`{"code": ..., "message": ...}`) is parsed when present
and preserved verbatim in `.raw` when it is not. `code`/`message`/`raw` travel
into the exception constructors as one `ErrorBody` (§5.2's Parameter Object
row) rather than three separate keywords, but remain flat attributes
(`.code`, `.message`, `.raw`) on the raised exception itself — the grouping is
a constructor-ergonomics detail, not a change to the caught-exception shape.

### 7.5 Logging and hooks

- Logger name `clockify`, `NullHandler` attached at import. The library never
  configures the root logger.
- `DEBUG`: method, URL, status, elapsed ms, request id if returned.
- The API key is **never** logged; a redacting filter covers the `X-Api-Key`
  header and any `api_key` value in structured extras.
- `ClientOptions(event_hooks=...)` forwards to httpx event hooks for
  caller-supplied instrumentation.

---

## 8. Testing

| Layer      | Tooling            | Runs                                               |
| ---------- | ------------------ | -------------------------------------------------- |
| Unit       | `pytest` + `respx` | Always. Offline, deterministic.                    |
| Live smoke | `pytest -m live`   | Manual / on demand, against a throwaway workspace. |

Requirements:

- Every resource method has at least one unit test asserting the exact HTTP
  method, path, query parameters, and request body it produces.
- Pagination, retry/backoff, and error mapping each have dedicated unit tests
  independent of any resource.
- Time codec has round-trip property tests over the `PnDTnHnMnS` subset.
- Live tests are skipped unless `CLOCKIFY_TEST_API_KEY` and
  `CLOCKIFY_TEST_WORKSPACE_ID` are set; they must clean up everything they
  create.
- Coverage gate: **90%** on `src/clockify`, enforced by `make test`.

---

## 9. Documentation deliverables

| File                      | Content                                                                                                                               |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `README.md`               | Install, auth, quickstart, 5–8 recipes, link to coverage matrix                                                                       |
| `docs/ARCHITECTURE.md`    | Layering (client → resource → transport → models), extension points, why sync-only, how to add an endpoint                            |
| `docs/coverage.md`        | Table: Clockify documented endpoint → SDK method → status. The verifiable definition of "covers all actions"                          |
| `# METHOD /path` comments | Docstrings are banned (§9's own convention); every resource method carries a one-line comment naming its HTTP method and path instead |

A generated docs site is optional and out of scope for v1.

---

## 10. Delivery plan

| Phase | Content                                                                                                                                              | Exit criterion                                                                                      |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| 0     | Template import, rename `app` → `clockify`, pyproject metadata, deps (`httpx`, `pydantic>=2`), `make check` green                                    | Empty package installs and passes the gate                                                          |
| 1     | `config`, `errors`, `ids`, `retry`, `_auth`, `_transport`, `_retry_transport`, `_pagination`, `_time`, `ClockifyClient` skeleton, `client.user.me()` | Auth, retries, errors, pagination unit-tested end to end against respx                              |
| 2     | Generic `resources/base.py`; workspaces, users, user groups, memberships                                                                             | `WorkspaceClient` binding proven; generic base validated on real endpoints before it is depended on |
| 3     | Projects, tasks, clients, tags, custom fields                                                                                                        | Core CRUD complete                                                                                  |
| 4     | Time entries (incl. start/stop, bulk, filters)                                                                                                       | The highest-traffic surface complete                                                                |
| 5     | Reports API                                                                                                                                          | Summary/detailed/weekly/shared                                                                      |
| 6     | `docs/coverage.md` filled, README, ARCHITECTURE, `0.1.0` published to PyPI                                                                           | Coverage matrix shows no gaps in the §1.1 scope                                                     |

Versioning is SemVer. Everything below `1.0.0` may break; `0.x` minor bumps
signal breaking changes.

---

## 11. Risks and accepted trade-offs

| #   | Risk                                                 | Impact                                                                                                                                | Position                                                                                                                                                                                                         |
| --- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R1  | `requires-python = ">=3.14"`                         | Excludes nearly every current installation (3.11–3.13). Adoption of a public PyPI package will be near zero until 3.14 is widespread. | **Accepted by owner.** Revisit before announcing publicly; lowering the floor later is non-breaking.                                                                                                             |
| R2  | No CI                                                | Nothing enforces `make check` on a PR; a missed local hook ships a broken release.                                                    | **Accepted for v1.** Mitigation: a release checklist in `ARCHITECTURE.md` requiring `make check && make test` before tagging. Add GitHub Actions before `1.0.0`.                                                 |
| R3  | Hand-written endpoints drift from Clockify's docs    | Silent breakage when Clockify changes a payload.                                                                                      | `extra="allow"` on all models absorbs additions; live smoke suite detects removals. Re-audit the coverage matrix each release.                                                                                   |
| R4  | Undocumented / inconsistent Clockify behavior        | Some endpoints return shapes that contradict the docs.                                                                                | Encode observed behavior, cite the doc URL in the docstring, note the discrepancy inline.                                                                                                                        |
| R5  | Rate limits differ by plan and are poorly documented | Retry defaults may be wrong for free-plan users.                                                                                      | Defaults are conservative and fully configurable; document the observed limits in the README.                                                                                                                    |
| R6  | Trademark / naming                                   | "Clockify" is CAKE.com's mark.                                                                                                        | Distribution name is `clockify-unofficial-sdk`; README carries a prominent "unofficial, not affiliated with CAKE.com" notice. Import name `clockify` is a namespace risk only if an official package ever ships. |
| R7  | Generic resource base over-abstracts                 | Endpoints with no CRUD analogue get contorted into the generic shape, making them harder to read than plain methods would be.         | The base is introduced in Phase 2 against real endpoints, not designed up front. Non-CRUD endpoints are written by hand by rule (§5.2).                                                                          |
| R8  | Typed IDs add boundary friction                      | Wrapping/unwrapping at every call site; users passing bare `str` hit type errors the runtime would have tolerated.                    | Accept `str` at public boundaries and coerce, so typing is a static aid rather than a runtime obstacle. Revisit in Phase 2 if it proves noisy.                                                                   |

---

## 12. Open items

1. Confirm whether Expenses and Invoices are exposed under the v1 Working API
   for the target plan; if so they belong in §1.1, otherwise defer.
2. Confirm the real per-endpoint `page-size` maximum (reported values range from
   200 to 5000) before fixing the `list()` default.
3. License: the template ships MIT (© Gerardo Antonio Gerónimo Vasconcelos).
   Confirm MIT is intended for the published SDK.
