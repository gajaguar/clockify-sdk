---
type: guide
title: Webhooks
description: How the webhook resource differs from the other resources, and how a receiver verifies that a delivery came from Clockify.
tags: [sdk, webhooks]
status: stable
---

# Webhooks

`ws.webhooks` follows the CRUD contract of the other workspace resources, with
three differences that come from the Clockify API, not from the SDK.

## `list()` makes one request

`GET .../webhooks` returns every webhook of the workspace in one envelope
(`webhooks` plus a `workspaceWebhookCount`) and takes no `page` parameter.
`list()` therefore sends one request, unwraps the envelope and yields the
webhooks; `list_page()` raises `NotImplementedError`, as `get()` does on
resources whose API has no single-item endpoint — see
[`pagination.md`](pagination.md). `list(webhook_type=WebhookType.ADDON)` sends
the endpoint's `type` filter.

## `regenerate_token()` is not retried on `5xx`

`PATCH .../webhooks/{id}/token` issues a new token on every call, so repeating
it after a `5xx` could rotate the token twice and leave the caller holding the
first one. It is declared a non-idempotent command, which the retry transport
reads — see [`adding-an-endpoint.md`](adding-an-endpoint.md).

## An empty `200` is not an error

Clockify answers a webhook delete with `200` and no body, not `204`. The
transport maps any successful response with an empty body to `None`, so
`delete()` returns normally.

## Verifying a delivery

Every delivery carries the `Clockify-Signature` header, whose value is the
`auth_token` Clockify returned when the webhook was created. The receiver
stores that token and compares:

```python
from clockify import SIGNATURE_HEADER, verify_signature

verify_signature(headers.get(SIGNATURE_HEADER), stored_token)
```

`verify_signature` compares in constant time and returns `False` for a missing
or empty value. The event name arrives in `Clockify-Webhook-Event-Type`
(`EVENT_TYPE_HEADER`). Regenerating the token invalidates the old one, so the
receiver must store the new value before the next delivery.

`Webhook.auth_token` is excluded from the model's `repr`, so a traceback or a
log line does not print it — the same rule as the API key in
[`credential-contract.md`](credential-contract.md).

The SDK does not parse delivery payloads: the body differs for each of the 51
events and is left to the receiver.
