# Directory Update Log

## 2026-10-01 (9)

* **Release**: version 1.8.0, a minor. Since 1.7.0 the public API only grew:
  `ws.time_off_policies`, `ws.time_off_requests`, `ws.time_off_balances` and the
  time off models, sync and async; no breaking changes. The new models are not
  verified against a real response.

## 2026-10-01 (8)

* **Feature**: `workspace.time_off_policies`, `time_off_requests` and
  `time_off_balances`, sync and async, so the Time off endpoints are `done` in
  [`sdk/coverage.md`](sdk/coverage.md), whose routes are corrected to the spec's
  (a request hangs off its policy and the balance has no `GET .../balance`). It
  also covers the four balance-assignment endpoints the table did not list. See
  [`sdk/time-off.md`](sdk/time-off.md). **The models are not verified against a
  real response**: Time off needs the Standard plan and the account used answers
  `403`.

## 2026-10-01 (7)

* **Release**: version 1.7.0, a minor. Since 1.6.0 the public API only grew:
  `ws.webhooks.logs`, `logs_page`, `statuses`, `statuses_page` and
  `list_for_addon` with their models, sync and async; no breaking changes. The
  new models are not verified against a real response.

## 2026-10-01 (6)

* **Feature**: `workspace.webhooks.logs`, `logs_page`, `statuses`, `statuses_page`
  and `list_for_addon`, sync and async, so the three remaining Webhooks
  endpoints are `done` in [`sdk/coverage.md`](sdk/coverage.md). The delivery
  endpoints page with `size`; see [`sdk/webhooks.md`](sdk/webhooks.md).
  **Not verified against a real response**: the Free plan answers `403` for every
  webhook endpoint, so the models follow the OpenAPI spec and the first page is
  assumed to be `1`.

## 2026-10-01 (5)

* **Release**: version 1.6.0, a minor. Since 1.5.0 the public API only grew:
  `ws.expenses` (`list`, `list_page`, `get`, `create`, `update`, `delete`),
  `ws.expense_categories` (`list`, `list_page`, `create`, `update`,
  `update_status`, `delete`) and the expense models, sync and async; no breaking
  changes. The Expenses models are not verified against a real response.

## 2026-10-01 (4)

* **Feature**: `workspace.expenses` (`list`, `list_page`, `get`, `create`, `update`,
  `delete`) and `workspace.expense_categories` (`list`, `list_page`, `create`,
  `update`, `update_status`, `delete`), sync and async, so the Expenses endpoints
  are `done` in [`sdk/coverage.md`](sdk/coverage.md), whose category routes are
  corrected to `.../expenses/categories`. Creating and updating an expense send
  `multipart/form-data`; see [`sdk/multipart-uploads.md`](sdk/multipart-uploads.md).
  The file download stays `planned`. **The models are not verified against a real
  response**: Expenses needs the Pro plan and the account used answers `403`.

## 2026-10-01 (3)

* **Release**: version 1.5.0, a minor. Since 1.4.0 the public API only grew:
  `ws.approvals` (`list`, `list_page`, `submit`, `submit_for_user`, `update`,
  `resubmit`) and the approval models, sync and async; no breaking changes.

## 2026-10-01 (2)

* **Feature**: `workspace.approvals` (`list`, `list_page`, `submit`,
  `submit_for_user`, `update`, `resubmit`, sync and async) and the approval
  models, so the five Approvals endpoints are `done` in
  [`sdk/coverage.md`](sdk/coverage.md). Below the Standard plan Clockify answers
  `403`, raised as `ForbiddenError`. The deprecated submit endpoints without a
  `{type}` stay out of scope.

## 2026-10-01 (1)

* **Documentation**: [`sdk/coverage.md`](sdk/coverage.md) tracks Time off,
  Approvals, Expenses and Invoices as `planned` instead of out of scope. Clockify's
  pricing page confirms Time off, Approvals and Invoices from the Standard plan
  and Expenses from the Pro plan; each section names its plan, and a lower plan
  gets a `403`.

## 2026-09-30 (14)

* **Release**: version 1.4.0, a minor. Since 1.3.0 the public API only grew:
  `ws.webhooks` (`list`, `get`, `create`, `update`, `delete`,
  `regenerate_token`), the webhook models, `verify_signature` and the two
  header-name constants are new, sync and async. A successful response with no
  body now returns `None` instead of raising; nothing else changed in
  behavior, so it is not a major.

## 2026-09-30 (13)

* **Feature**: `workspace.webhooks` (`list`, `get`, `create`, `update`,
  `delete`, `regenerate_token`, sync and async), the webhook models, and
  `verify_signature` with the two header-name constants for receivers. The
  transport now maps a successful response with no body to `None`, since
  Clockify answers a webhook delete with `200` and no body. Webhook logs,
  statuses and add-on webhooks stay `planned` in
  [`sdk/coverage.md`](sdk/coverage.md). See [`sdk/webhooks.md`](sdk/webhooks.md).

## 2026-09-30 (12)

* **Documentation**: the README's environment variable table lists
  `CLOCKIFY_TEST_REGION`, the `Region` the live reports smoke test runs against.

## 2026-09-30 (11)

* **Documentation**: the README documents the weekly report's 7-day range and
  `WeeklySubgroup`, and says that a 403 from the Reports API means the plan or
  role does not allow reports and that the report models are not yet checked
  against a live response.

## 2026-09-30 (10)

* **Fix**: a live run against the Reports API showed two request bugs. A
  `DetailedReportRequest` without an explicit filter sent no `detailedFilter`,
  which the API rejects; `_body` now drops `None` values instead of unset ones,
  so the default filter is sent. `WeeklyFilter.subgroup` was typed
  `ReportGroup`, but the API accepts only `TIME` or `EARNINGS`; the new
  `WeeklySubgroup` enum replaces it, so passing a `ReportGroup` now fails
  validation. The live summary smoke test skips on a 403, since the FREE plan
  lacks the Reports API.

## 2026-09-30 (9)

* **Release**: version 1.3.0, a minor. Since 1.2.0 the public API only grew:
  `ws.reports` (`summary`, `detailed`, `weekly`, `shared`), its request and
  response models, and the optional `reports_transport` parameter of
  `WorkspaceClient` and `AsyncWorkspaceClient` are new, sync and async.
  Nothing was removed or changed in behavior, so it is not a major.

## 2026-09-30 (8)

* **Addition**: `ws.reports` with `summary`, `detailed`, `weekly` and `shared`,
  sync and async, completing the "Reports API" section of
  [`sdk/coverage.md`](sdk/coverage.md). The resource uses the reports
  transport, requests every report as JSON and declares each call a query.
  `WorkspaceClient` and `AsyncWorkspaceClient` take an optional
  `reports_transport`. The version stays 1.2.0; the minor bump to 1.3.0 is a
  separate release change.

## 2026-09-30 (7)

* **Release**: version 1.2.0, a minor. Since 1.1.0 the public API only grew:
  `user_groups.add_user` and `user_groups.remove_user` are new, sync and
  async. Nothing was removed or changed in behavior, so it is not a major.

## 2026-09-30 (6)

* **Addition**: `user_groups.add_user` and `user_groups.remove_user`, sync and
  async, completing the "Users and user groups" section of
  [`sdk/coverage.md`](sdk/coverage.md). `add_user` is a non-idempotent command
  (POST); `remove_user` is idempotent (DELETE). Both return the updated
  `UserGroup`. The version stays 1.1.0; the minor bump to 1.2.0 is a separate
  release change.

## 2026-09-30 (5)

* **Release**: version 1.1.0, a minor. Since 1.0.1 the public API only grew:
  `ClockifyClient` accepts an add-on token (`addon_token=` or
  `CLOCKIFY_ADDON_TOKEN`), and `AsyncClockifyClient` and
  `AsyncWorkspaceClient` are new. Nothing was removed or changed in behavior,
  so it is not a major.

## 2026-09-30 (4)

* **Addition**: `AsyncClockifyClient` and `AsyncWorkspaceClient`, built on
  `httpx.AsyncClient`, with async twins of every resource, the retry
  transport and pagination. Decision recorded in
  [`sdk/async-client.md`](sdk/async-client.md); `sdk/layering.md`,
  `sdk/request-lifecycle.md` and `sdk/adding-an-endpoint.md` now cover the
  async path. The version stays 1.0.1; the minor bump to 1.1.0 is a separate
  release change.

## 2026-09-30 (3)

* **Updated**: `sdk/credential-contract.md` (new "Choosing between credential
  kinds" section) and `sdk/credential-tests.md` (new "Selection" group),
  aligned with `bitbucket-sdk`. The behavior already matched.

## 2026-09-30 (2)

* **Addition**: `ClockifyClient` accepts an add-on token (`addon_token=` or
  `CLOCKIFY_ADDON_TOKEN`), sent as `X-Addon-Token`, mutually exclusive with
  the API key. [`sdk/credentials.md`](sdk/credentials.md) now covers both
  credentials. The version stays 1.0.1; the minor bump to 1.1.0 is a separate
  release change.

## 2026-09-30

* **Template sync**: `Makefile` and `mk/python.mk` match the template again
  (`make commits-check` rejects an empty commit message; `install-python`
  registers console scripts only when the project declares them, so the
  hand-made deviation is gone). The credential notes drop their `generated`
  field. `AGENTS.md` follows the current seed, with the Pull requests and SDK
  sections, and keeps "Long parameter lists". `conventions/commits-check.md`
  and `python/pyproject-defaults.md` no longer describe the old branch-skip and
  the `app-*` pylint checkers. No code or public API changed, so the version
  stays 1.0.1.

## 2026-09-29 (4)

* **Release**: version 1.0.1, a patch. Since 1.0.0 the public API is
  unchanged; `Transport` now receives its authentication from the client,
  `MissingCredentialsError` names where to create the key, and the docs gained
  the credential notes.

## 2026-09-29 (3)

* **Addition**: adopted the credential notes `credential-contract.md`,
  `credential-sources.md` and `credential-tests.md` under `docs/sdk/`, the
  same text `bitbucket-sdk` carries. [`sdk/credentials.md`](sdk/credentials.md)
  now holds only what belongs to Clockify and links to the contract.

## 2026-09-29 (2)

* **Auth**: added [`sdk/credentials.md`](sdk/credentials.md), the credential
  contract shared with `bitbucket-sdk`. `Transport` now receives its
  `httpx.Auth` from the client instead of building one, and
  `MissingCredentialsError` names where to create the key. The README gained
  a "Getting a credential" section.

## 2026-09-29

* **Template sync**: `pylint-plugin` (git) replaced by `pylint-gajaguar` from
  PyPI with `enable = ["gajaguar"]`; `conventional-git>=1.1`, the
  `conventional-git-latest` target, Dependabot's `npm` ecosystem, and the
  Dependabot branch skip in `make commits-check` now match the template.
  `AGENTS.md` names the `gajaguar-no-docstrings` checker.

## 2026-09-28 (6)

* **Release readiness**: [`release/pypi-trusted-publishing.md`](release/pypi-trusted-publishing.md)
  now names the PyPI project `clockify-unofficial-sdk` and the `pypi`
  environment protection. [`conventions/commits-check.md`](conventions/commits-check.md)
  documents that Dependabot branches skip the branch-name check. Version
  1.0.0.

## 2026-09-28 (5)

* **Conventions**: `AGENTS.md` and `CONTRIBUTING.md` now say a branch type
  is one the Conventional Branch specification defines (`feat`, `fix`,
  `hotfix`, `release`, `chore`), not any commit type; documentation work uses
  `chore/`. Links point at conventionalbranch.org.

## 2026-09-28 (4)

* **Contributing**: added a root `CONTRIBUTING.md` carrying what the
  README's `## Contributing` section listed — setup, the new-endpoint
  procedure, the gate, commit and branch conventions — plus how to report a
  bug, a vulnerability, and the docs-bundle rule. The README section is now
  one sentence linking to it.

## 2026-09-28 (3)

* **Sync**: Realigned `AGENTS.md` and the seeded notes with the project
  standard. `AGENTS.md` gained the "Agent instructions" section and lost its
  config-restating Python bullets; `docs/index.md` blurbs no longer describe
  pruned notes; `sdk/endpoint-comments.md` points at `AGENTS.md` instead of the
  deleted `python/docstring-policy.md`; `python/pyproject-defaults.md` drops
  the hatch row (this project sets `packages` explicitly) and cites
  `--cov=clockify`; `toolchain/layering-rule.md` no longer repeats the
  interpreter-source paragraph.
  README.md now follows the standard section order (CI badge, About, Open
  items) and its docstring subsection points at `AGENTS.md`. The README's
  "Open items" section was then removed as a duplicate of
  [`sdk/coverage.md`](sdk/coverage.md); its one unique caveat, the unconfirmed
  `page-size` maximum, moved to [`sdk/pagination.md`](sdk/pagination.md).

## 2026-09-28 (2)

* **Pruning**: Removed `docs/toolchain/{checkmake,markdown-tooling,mise,
  pre-commit}.md`, `docs/python/{docstring-policy,pylint-plugin}.md`, and
  `docs/conventions/{check-vs-fix,files-scoping,commits-and-branches}.md` —
  each only restated what `make help` or a linter's own message already
  says, and the last two also linked to a `docs/branching/` this project
  never had. Folded `docs/python/commit-range-in-ci.md` into
  `docs/conventions/commits-check.md`. Removed `AGENTS.md`'s "Repository
  metadata" section (an instantiation-only checklist, stale since this
  project's first release) and trimmed its Python section to what
  `make help` and the toolchain layering note don't already cover.
  README.md's `check`/`fix` table and `FILES=` paragraph moved to one
  sentence pointing at `make help`.

## 2026-09-28

* **Auth: credential provider callback (0.2.0)**: `ClockifyClient(api_key=...)`
  and `resolve_api_key` now accept a zero-argument callable in addition to a
  plain string, invoked lazily on every request by `ApiKeyAuth` instead of
  once at construction. This is the SDK's only new credential-related
  surface — it keeps the environment variable as its sole automatic
  fallback and adds no keyring, filesystem, or interactive dependency.
  `ClientConfig.api_key` is now `repr=False` so the raw key can no longer
  leak into a dataclass repr. See
  [`sdk/request-lifecycle.md`](sdk/request-lifecycle.md).

## 2026-09-27

* **Standardization**: Brought the project's scaffold up to date —
  Makefile, mise.toml, `.pre-commit-config.yaml`, `mk/python.mk`, CI
  workflows, and this OKF `docs/` bundle. Added
  `.github/workflows/publish.yml` for PyPI
  Trusted Publishing — see
  [`release/pypi-trusted-publishing.md`](release/pypi-trusted-publishing.md).
  `docs/ARCHITECTURE.md` and `docs/coverage.md` moved under
  [`sdk/`](sdk/index.md) as OKF notes; see [`sdk/index.md`](sdk/index.md)
  for what replaced them at their old paths.
