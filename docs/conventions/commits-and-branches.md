---
type: convention
title: Commits and branches
description: Conventional Commits for messages, Conventional Branch for branch names, and the append-only rule for shared files.
tags: [git]
status: stable
---

# Commits and branches

* Commit messages follow
  [Conventional Commits](https://www.conventionalcommits.org/); branch names
  follow [Conventional Branch](https://conventional-branch.github.io/) — see
  `AGENTS.md`'s "Commits and branches" section for the normative form of
  both.
* `main` carries anything language-agnostic; a language branch changes its
  own files freely but only *appends* to a file it shares with `main` (never
  edits existing lines), so `git merge main` never conflicts with it — see
  [`append-only-shared-files.md`](../branching/append-only-shared-files.md).
