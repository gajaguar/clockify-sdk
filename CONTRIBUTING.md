# Contributing

Thanks for considering a contribution to this unofficial Clockify SDK. Bug
reports, feature ideas, documentation fixes, and new endpoint coverage are all
welcome.

## Ways to contribute

- Report a bug or propose a feature by opening a GitHub issue. For a bug,
  include the SDK call, the response or error you got, and what you expected.
  Never paste a Clockify API key; it grants full access to a workspace.
- Report a suspected vulnerability privately, as described under
  [Security](README.md#security), not in a public issue.
- Fix or extend documentation under `docs/`.
- Add coverage for a Clockify endpoint the SDK does not wrap yet; see
  [`docs/sdk/coverage.md`](docs/sdk/coverage.md) for what exists.
- For anything larger than a small fix, open an issue first so the approach
  can be agreed before you invest time in it.

## Set up

Fork the repository, then install the toolchain and dependencies as
described in the README's [Prerequisites](README.md#prerequisites) and
[Installation](README.md#installation) sections:

```bash
mise install
make install
```

Run `make help` for the full list of targets.

## Making a change

- A new endpoint follows the steps in
  [`docs/sdk/adding-an-endpoint.md`](docs/sdk/adding-an-endpoint.md), which
  end with updating the coverage table.
- Resources never touch `httpx` directly; read
  [`docs/sdk/layering.md`](docs/sdk/layering.md) before adding a request
  path.
- Code-style rules, including the ban on docstrings, are in
  [`AGENTS.md`](AGENTS.md).

## Before opening a pull request

Both commands MUST exit 0:

```bash
make check
make test
```

`make fix` applies the safe automatic fixes for what `make check` reports.
CI runs the Makefile, Markdown, and spelling linters, `make commits-check`,
and the pre-commit hooks. It does not run the test suite, so `make test`
before you push is on you.

Describe the change and the endpoint(s) it covers in the pull request.

## Commits and branches

- Commit messages follow
  [Conventional Commits](https://www.conventionalcommits.org/).
- Branch names follow
  [Conventional Branch](https://conventionalbranch.org/):
  `<type>/<description>`, for example `feat/add-tags-resource` or
  `fix/retry-after-parsing`. The branch type is one of `feat`, `fix`,
  `hotfix`, `release`, or `chore`; documentation work uses `chore/`.

A pre-commit hook and `make commits-check` enforce both; see
[`docs/conventions/commits-check.md`](docs/conventions/commits-check.md).

## Documentation

`docs/` is a bundle of atomic notes: one concept per file. A new note is
added to its directory's `index.md` and to [`docs/log.md`](docs/log.md) in
the same pull request.

## License

By contributing, you agree that your contribution is licensed under the
project's MIT License; see [LICENSE](LICENSE).
