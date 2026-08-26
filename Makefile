SHELL := /bin/bash
.SHELLFLAGS := -euo pipefail -c

UV := uv
NPM := pnpm

# Files to scope quality targets to. Accepts paths or globs.
# Usage: make lint FILES="src/foo.py src/bar.py"
FILES ?=

.DEFAULT_GOAL := help

##@ Help

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Setup

install-root: ## Install main + dev/test dependency groups
	$(UV) sync

install-tools: ## Install root package and register console scripts onto PATH (not applicable — this package ships no CLI)
	$(UV) sync

install-node: ## Install Node tooling (markdownlint-cli2, cspell) via pnpm
	$(NPM) install

setup-hooks: ## Install the pre-commit git hook
	$(UV) run pre-commit install

install: install-root install-node setup-hooks ## Install everything (Python, Node, git hooks)

##@ Read-only checks (never mutate — the CI gate)

lint: ## Lint with Ruff — accepts FILES="..." to limit scope
	$(UV) run ruff check --preview $(or $(FILES),.)

format-check: ## Check formatting with Ruff, without writing — accepts FILES="..."
	$(UV) run ruff format --check --preview $(or $(FILES),.)

mypy: ## Type-check with mypy — accepts FILES="..." to limit scope
	$(UV) run mypy $(or $(FILES),.)

pyright: ## Type-check with Pyright — accepts FILES="..." to limit scope
	$(UV) run pyright $(or $(FILES),.)

typecheck: mypy pyright ## Run both type checkers

md-lint: ## Lint Markdown files with markdownlint-cli2 — accepts FILES="..."
	@if ! command -v pnpm &>/dev/null; then \
		echo "pnpm is not available. Run: make install-node"; \
	else \
		pnpm exec markdownlint-cli2 $(or $(FILES),**/*.md); \
	fi

spell: ## Spell-check files with cspell — accepts FILES="..."
	@if ! command -v pnpm &>/dev/null; then \
		echo "pnpm is not available. Run: make install-node"; \
	else \
		pnpm exec cspell --no-progress --no-summary $(or $(FILES),**); \
	fi

pylint: ## Self-lint with this repo's own checkers (see github.com/gajaguar/pylint-plugin) — accepts FILES="..."
	$(UV) run pylint $(or $(FILES),src tests)

check: lint format-check typecheck md-lint spell pylint ## Run the full read-only validation gate

##@ Writable fixes (mutate files in place)

format: ## Format code with Ruff — accepts FILES="..." to limit scope
	$(UV) run ruff format --preview $(or $(FILES),.)

lint-fix: ## Auto-fix lint issues with Ruff (safe fixes only) — accepts FILES="..."
	$(UV) run ruff check --fix --preview $(or $(FILES),.)

lint-fix-unsafe: ## Auto-fix lint issues with Ruff, including unsafe fixes — accepts FILES="..."
	$(UV) run ruff check --fix --preview --unsafe-fixes $(or $(FILES),.)

md-fix: ## Auto-fix Markdown files with markdownlint-cli2 — accepts FILES="..."
	@if ! command -v pnpm &>/dev/null; then \
		echo "pnpm is not available. Run: make install-node"; \
	else \
		pnpm exec markdownlint-cli2 --fix $(or $(FILES),**/*.md); \
	fi

fix: format lint-fix _md-fix-scoped ## Apply all safe auto-fixes

fix-unsafe: format lint-fix-unsafe _md-fix-scoped ## Apply all auto-fixes, including unsafe Ruff fixes

# Only invoke md-fix with Markdown files — prevents `fix`/`fix-unsafe` from
# forwarding a non-Markdown FILES scope (e.g. FILES="src/main.py") into
# markdownlint-cli2. Not a public target; used internally by fix/fix-unsafe.
_md-fix-scoped:
	@MD_FILES=$$(echo "$(or $(FILES),**/*.md)" | tr ' ' '\n' | grep '\.md$$' | tr '\n' ' ' || true); \
	if [ -n "$$MD_FILES" ]; then \
		$(MAKE) md-fix FILES="$$MD_FILES"; \
	fi

##@ Test

test: ## Run the test suite — accepts FILES="..." to limit scope
	$(UV) run pytest $(FILES)

coverage: ## Run tests with an HTML coverage report
	$(UV) run pytest --cov=clockify --cov-report=html

.PHONY: help install-root install-tools install-node setup-hooks install \
	lint format-check mypy pyright typecheck md-lint spell pylint check \
	format lint-fix lint-fix-unsafe md-fix fix fix-unsafe _md-fix-scoped \
	test coverage
