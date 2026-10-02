---
type: guide
title: Invoices
description: How the three invoice resources split Clockify's routes, how amounts are expressed, why deleting an item is not retried, and which shapes the spec leaves doubtful.
tags: [sdk, invoices]
status: stable
---

# Invoices

Invoices is a Standard-plan feature. The account the SDK was built on is on the
Free plan, so Clockify answers `403` (`ForbiddenError`) and **the Invoices models
and requests are not verified against a real response**; they follow the OpenAPI
spec, with every doubtful field optional.

## Three resources

The routes would make one class with twenty methods, so the SDK splits them by
the thing each acts on:

* `ws.invoices` — the invoice itself: `list`, `search`, `get`, `create`,
  `update`, `delete`, `duplicate`, `export`, `update_status`, and the workspace
  `get_settings` and `update_settings`.
* `ws.invoice_items` — `add`, `import_entries` (time entries and expenses) and
  `delete`.
* `ws.invoice_payments` — `list`, `add` and `delete`.

`list()` (`GET .../invoices`) filters by status and sorts. `search()`
(`POST .../invoices/info`) filters by client, company, amounts, number and issue
date; it is a `POST` that only reads, so it is a query and a `5xx` is retried.
Its page travels in the body, which is why `InvoiceSearch` has no page fields.

## Amounts are minor units

Every amount (`amount`, `balance`, `paid`, `subtotal`, `unit_price`) is an
integer in the currency's minor unit, as the spec's `int64`: `12000` is `120.00`.
Discount and tax percentages are floats.

## Deleting an item is not retried

`DELETE .../invoices/{id}/items/{order}` takes the item's position, and the items
after it are renumbered. Repeating the call after a `5xx` could delete the item
that moved into that position, so `delete` is a non-idempotent command. Adding an
item, importing entries, duplicating and adding a payment are non-idempotent as
well; deleting a payment by its id is idempotent.

## The export is a file

`ws.invoices.export(id, user_locale=)` returns the exported invoice as bytes,
through `request_bytes` — see [`binary-downloads.md`](binary-downloads.md).

## Doubtful shapes

* The spec renders `taxType`, `applyTaxes` and `calculationType` as objects of
  enum members, while every request and the settings use a plain string. The SDK
  types them as string enums with an `UNKNOWN` fallback; a response that sends an
  object would fail to validate.
* `visibleZeroFields` is one value in the update request and an object in the
  responses. The request takes one `InvoiceVisibleZeroField`; the responses keep
  it as an extra field, not a typed one.
* The first page of `payments` and `list` is assumed to be `1`, as in the rest of
  the API.
