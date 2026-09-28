# Directory Update Log

## 2026-09-28 (3)

* **Sync**: Realigned `AGENTS.md` and the seeded notes with the project
  standard. `AGENTS.md` gained the "Agent instructions" section and lost its
  config-restating Python bullets; `docs/index.md` blurbs no longer describe
  pruned notes; `sdk/endpoint-comments.md` points at `AGENTS.md` instead of the
  deleted `python/docstring-policy.md`; `python/pyproject-defaults.md` drops
  the hatch row (this project sets `packages` explicitly) and cites
  `--cov=clockify`; `toolchain/layering-rule.md` no longer repeats the
  interpreter-source paragraph.

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
