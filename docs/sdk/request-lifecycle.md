---
type: guide
title: Request lifecycle
description: Every request passes through the same auth, retry, error-mapping, and validation pipeline inside _transport, regardless of which resource issued it.
tags: [sdk, architecture]
status: stable
---

# Request lifecycle

Every request passes through the same auth → retry → error-mapping →
validation pipeline, regardless of which resource issued it. The retry loop
on `429`/`5xx` and the status-to-exception mapping are the two behaviors
worth tracing explicitly — everything else in this flow is a straight
pass-through.

```mermaid
sequenceDiagram
    participant Caller
    participant Resource
    participant Transport as _transport
    participant API as Clockify API

    Caller->>Resource: ws.projects.list(archived=False)
    Resource->>Transport: request(method, path, params)
    Transport->>Transport: call api_key() if provider, else use as-is
    Transport->>Transport: inject X-Api-Key
    Transport->>API: HTTP request
    API-->>Transport: 429 + Retry-After
    Transport->>Transport: wait, retry (bounded by max_attempts)
    Transport->>API: HTTP request (retry)
    API-->>Transport: 200 + JSON body
    Transport->>Transport: map status to exception (2xx: none)
    Transport-->>Resource: raw JSON
    Resource->>Resource: validate into pydantic model(s)
    Resource-->>Caller: Project | list[Project]
```

Declaring a resource method's CQS kind (query, idempotent command,
non-idempotent command) is part of adding an endpoint — see
[`adding-an-endpoint.md`](adding-an-endpoint.md) — because the retry
transport reads it to decide `5xx` eligibility.

The async client runs the same pipeline: `AsyncTransport` awaits the request,
`AsyncRetryTransport` retries with `asyncio.sleep`, and response handling is the
same function — see [`async-client.md`](async-client.md).
