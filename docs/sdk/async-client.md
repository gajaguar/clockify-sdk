---
type: decision
title: Async client
description: The SDK ships AsyncClockifyClient next to the sync client, sharing models, auth, retry rules and error mapping, and differing only in how it is awaited and closed.
tags: [sdk, architecture, async]
status: stable
---

# Async client

The SDK ships `AsyncClockifyClient`, built on `httpx.AsyncClient`, next to
`ClockifyClient`. Both expose the same resources and methods, so moving from
one to the other means adding `await` and `async with`.

## Why it is implemented

The issue that evaluated it (#19) allowed staying sync-only "unless a real
need appears". The need is concurrent use from async applications, where a
blocking client stalls the event loop. `ApiKeyAuth` and `AddonTokenAuth` are
`httpx.Auth` subclasses, which httpx runs in async mode as well, so the
authentication code is shared and did not change.

## What is shared

* Models, CQS kinds, `RetryPolicy` and its `should_retry` / `compute_delay`
  rules, error mapping, and the debug log (`_handle_response` in
  `_transport.py`).
* Credential resolution and URL resolution (`_build_config_and_auth` in
  `client.py`), so both clients accept the same arguments and environment
  variables.
* Path building, in the `_WorkspacePaths`, `_TaskPaths` and `_TimeEntryPaths`
  bases.

## What differs

* Context manager: `with ClockifyClient()` becomes `async with AsyncClockifyClient()`.
* Closing: `close()` becomes `await aclose()`.
* Iteration: `for x in ws.tags.list()` becomes `async for x in ws.tags.list()`.
* Requests: `ws.tags.list_page()` and `c.default_workspace()` are awaited.
* `c.workspace(id)` is not awaited, because it makes no request.
* Retry: `RetryTransport` with `time.sleep` becomes `AsyncRetryTransport` with
  `asyncio.sleep`.

## Rules for callers

* A credential provider runs inside the event loop on every request, so it
  must not block. Read a file or a keyring before the loop starts, or cache
  the value in the provider.
* `ClientOptions.event_hooks` passed to the async client must be coroutine
  functions; httpx awaits them.
* The `Region` and `RetryPolicy` options behave as in the sync client.

## Keeping the two in step

A new endpoint is added to the sync and the async resource together — see
[`adding-an-endpoint.md`](adding-an-endpoint.md). `bitbucket-sdk` stays
sync-only until it gets its own async client.
