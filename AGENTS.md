# AGENTS.md

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## Command surface

The agent MUST use the `Makefile` targets (`make check`, `make fix`,
`make test`, ...) instead of invoking the underlying tools directly, and
MUST NOT add a target without its `##` help line.

## Documentation

Documentation MUST be an OKF bundle of atomic notes under `docs/`: one
Markdown concept per file, with YAML frontmatter (`type`, `title`,
`description`). A new note MUST be added to its directory's `index.md`
and to [`docs/log.md`](docs/log.md). A note MUST cover exactly one
concept.

## Commits and branches

Commit messages MUST follow
[Conventional Commits](https://www.conventionalcommits.org/); branch names
MUST follow [Conventional Branch](https://conventional-branch.github.io/)
(`<type>/<description>`, e.g. `feat/add-python-branch`,
`fix/makefile-phony-scoping`). Both share the same `type` vocabulary
(`feat`, `fix`, `docs`, `build`, `ci`, `refactor`, `test`, `chore`, ...). A
pre-commit hook and `make commits-check` enforce both, in this template and
in every generated project — see
[`docs/conventions/commits-check.md`](docs/conventions/commits-check.md).

## Gate

`make check` MUST pass before any commit. Findings SHOULD be fixed with
`make fix` before editing by hand.

## Repository metadata

The agent MUST populate the GitHub repository metadata before the first
release, and SHOULD do so in the first commit that follows instantiation of
this template:

- The repository description MUST be set to a single sentence, in English,
  without a trailing period.
- Repository topics MUST include the primary language and the project kind,
  and SHOULD include the main framework or runtime.
- The homepage URL MUST be set when the project is deployed or published,
  and MAY be left empty otherwise.
- `README.md` MUST NOT be the only place where the purpose of the project is
  stated; the description and the README first paragraph MUST agree.

The agent SHOULD apply these with `gh`:

```bash
gh repo edit --description "..." --add-topic <topic> --homepage "..."
```

The agent MUST NOT leave the description empty, and MUST NOT copy the
description of this template verbatim.

## Python

The `feat/python` branch adds Python-specific tooling through `mk/python.mk` while
keeping the shared `install`/`check`/`fix`/`test` command surface.

### Python commands

The Python targets are:

```bash
make lint FILES="..."
make format-check FILES="..."
make mypy FILES="..."
make pyright FILES="..."
make typecheck
make pylint FILES="..."
make pytest FILES="..."
make coverage
make build
make commits-check
```

`make build` builds the sdist and wheel into `dist/`. `make commits-check`
re-validates the commit range and branch name against Conventional
Commits/Conventional Branch with `conventional-git`, since a local hook can
be bypassed with `--no-verify`; CI runs it as a separate step (`BASE`
defaults to `origin/main`). `make new-project ... PUBLISH=pypi` additionally
wires up PyPI Trusted Publishing — see
[`docs/release/pypi-trusted-publishing.md`](docs/release/pypi-trusted-publishing.md)
in a project generated with that flag.

### Toolchain layering

**mise installs what bootstraps an ecosystem or belongs to none; the
ecosystem's own package manager installs everything else.** A tool declared
in two layers can drift, so `make check` and the pre-commit hook would then
disagree.

| Tool                                          | Declared in                                |
| :-------------------------------------------- | :----------------------------------------- |
| node, pnpm, python, uv, checkmake, pre-commit | `mise.toml`                                |
| cspell, markdownlint-cli2                     | `package.json`                             |
| ruff, mypy, pyright, pytest, pylint           | `pyproject.toml` `[dependency-groups].dev` |

`mise.toml` is the single source for the pinned Python version, and its
`[env]` forces uv to use that interpreter instead of downloading its own.

### Python conventions

- **No docstrings.** `pylint-plugin`'s `app-no-docstrings` (W9001) fails
  `make check` if any function, method, or class has one; use a comment only
  where the why is not obvious from the code.
- Custom pylint checks come from `gajaguar/pylint-plugin`, a git dependency
  configured through `pyproject.toml`'s `[tool.pylint.main]` and
  `[tool.pylint."messages control"]` settings. pylint runs only the plugin's
  `app-*` checkers; ruff covers everything else.
- Ruff runs with `lint.select = ["ALL"]` and `--preview`; mypy runs in
  `strict` mode and excludes `tests/`.
- Imports follow ruff's default isort order, one import per line
  (`lint.isort.force-single-line`).
- `pyproject.toml` MUST NOT hold a setting equal to the tool's default, and
  every `lint.per-file-ignores` entry MUST match a current violation — see
  [`docs/python/pyproject-defaults.md`](docs/python/pyproject-defaults.md).

## Long parameter lists

- MUST NOT silence `too-many-arguments` (pylint `R0913` / ruff `PLR0913`)
  with a disable comment. Fix the design instead: apply the **Parameter
  Object** refactoring — group the related arguments into a small, frozen,
  `slots=True` dataclass and accept that object as a single parameter.
- Keep the one or two arguments nearly every caller sets (e.g. `api_key`) as
  direct parameters. Only the secondary, related-by-purpose arguments move
  into the parameter object.
- Reference implementations: `src/clockify/errors.py`'s `ErrorBody` (groups
  `code`/`message`/`raw` across the exception hierarchy) and
  `src/clockify/config.py`'s `ClientOptions` (groups `region`, `base_url`,
  `reports_base_url`, `timeout`, `retry`, `event_hooks` for
  `ClockifyClient.__init__`).
- If the long parameter list is on a *documented* public API, update the
  README's usage examples in the same change — don't let the docs drift from
  the actual constructor shape.
