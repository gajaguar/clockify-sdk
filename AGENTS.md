# Agent Instructions

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
