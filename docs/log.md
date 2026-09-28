# Directory Update Log

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
