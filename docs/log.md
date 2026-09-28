# Directory Update Log

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

* **Standardization**: Brought the project up to date with this org's
  internal Python project template via `make audit-project` — Makefile,
  mise.toml, `.pre-commit-config.yaml`, `mk/python.mk`, CI workflows, and
  this OKF `docs/` bundle. Added `.github/workflows/publish.yml` for PyPI
  Trusted Publishing — see
  [`release/pypi-trusted-publishing.md`](release/pypi-trusted-publishing.md).
  `docs/ARCHITECTURE.md` and `docs/coverage.md` moved under
  [`sdk/`](sdk/index.md) as OKF notes; see [`sdk/index.md`](sdk/index.md)
  for what replaced them at their old paths.
