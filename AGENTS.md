# AGENTS.md

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## Agent instructions

`AGENTS.md` is the only agent instructions file. The repository MUST NOT
contain a `CLAUDE.md` or any other tool-specific copy; project rules go here.

## Command surface

The agent MUST use the `Makefile` targets (`make check`, `make fix`,
`make test`, ...) instead of invoking the underlying tools directly, and
MUST NOT add a target without its `##` help line. Run `make help` for the
full list.

## Gate

`make check` MUST pass before any commit. Findings SHOULD be fixed with
`make fix` before editing by hand.

## Commits and branches

Commit messages MUST follow
[Conventional Commits](https://www.conventionalcommits.org/); branch names
MUST follow [Conventional Branch](https://conventionalbranch.org/)
(`<type>/<description>`, e.g. `feat/add-tags-resource`,
`fix/retry-after-parsing`). A commit type may be any Conventional Commits
type, but a branch type MUST be one of `feat` (or `feature`), `fix` (or
`bugfix`), `hotfix`, `release`, `chore`; documentation and dependency work
uses `chore/`, e.g. `chore/update-readme`. A pre-commit hook and
`make commits-check` enforce both — see
[`docs/conventions/commits-check.md`](docs/conventions/commits-check.md).

## Documentation

Documentation MUST be an OKF bundle of atomic notes under `docs/`: one
Markdown concept per file, with YAML frontmatter (`type`, `title`,
`description`). A new note MUST be added to its directory's `index.md` and
to [`docs/log.md`](docs/log.md). A note MUST cover exactly one concept, and
only when it explains something a reader can't already get from `make
help`, a linter's own message, or the configuration it comes from.

## Dependencies

A new tool MUST be added to the ecosystem manager that owns it and MUST
only go in `mise.toml` when it bootstraps an ecosystem or has none in this
repository — see
[`docs/toolchain/layering-rule.md`](docs/toolchain/layering-rule.md).

## Python

- The agent MUST NOT add docstrings to functions, methods, or classes; use a
  comment only where the *why* is not obvious from the code. The
  `pylint-plugin` `app-no-docstrings` checker enforces this and fails
  `make check`/`make pylint` otherwise.
- The agent MUST NOT add a `pyproject.toml` setting that equals the tool's
  default, and every `lint.per-file-ignores` entry MUST match a current
  violation — see
  [`docs/python/pyproject-defaults.md`](docs/python/pyproject-defaults.md).
- The agent MUST run `make check` and `make test` before committing Python
  changes, and SHOULD run `make fix` first for anything auto-fixable.

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
