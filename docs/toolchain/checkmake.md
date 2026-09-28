---
type: tool
title: checkmake
description: Lints the Makefile itself; checkmake.ini disables the minphony rule's all/clean expectations.
tags: [toolchain]
status: stable
---

# checkmake

Lints the `Makefile` itself (`make makefile-lint`); `checkmake.ini` disables
the `minphony` rule's `all`/`clean` expectations, which don't apply to this
Makefile's install/check/fix/test shape.
