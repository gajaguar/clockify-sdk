# Toolchain

Which layer — mise or an ecosystem package manager — installs which tool,
and why.

* [Toolchain layering rule](layering-rule.md) - mise bootstraps, the
  ecosystem's own package manager installs everything else.
* [Rejected install backends](rejected-install-backends.md) - the mise
  `npm:`/`pipx:` backends and pre-commit-managed environments this rules out.
* [mise](mise.md) - pins the high-level toolchain.
* [markdownlint-cli2 and cspell](markdown-tooling.md) - Markdown lint and
  spell check.
* [checkmake](checkmake.md) - lints the Makefile.
* [pre-commit](pre-commit.md) - the git hook running the shared checks.
