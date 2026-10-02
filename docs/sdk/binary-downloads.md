---
type: decision
title: Binary downloads
description: Why the transport has a second method for endpoints that answer with a file, and what it leaves untouched.
tags: [sdk, transport, expenses]
status: stable
---

# Binary downloads

`GET .../expenses/{id}/files/{fileId}` answers with the receipt itself, and
`GET .../invoices/{id}/export` answers with the exported invoice. The
[transport](layering.md) decodes every success as JSON, so neither fits
`Transport.request`.

## The decision

`Transport.request_bytes` and `AsyncTransport.request_bytes` send the request
the same way `request` does and return `response.content` raw. They take
no body: a download is a `GET`. `request` is unchanged, so the addition is
backwards compatible.

Both methods go through one private `_send` and one `_check_response`:

* **Authentication.** The httpx client carries the `httpx.Auth` object, so a
  download sends the same `X-Api-Key` or `X-Addon-Token` header as any request.
* **Logging.** `_check_response` logs the method, the path, the status and the
  elapsed time, as before. The body is never logged, which matters more for a
  file than for JSON.
* **Retries.** The retry transport sits below httpx, so a download is retried
  like any other request. A download is a query, so a `5xx` is retried as well
  as a `429`.
* **Errors.** A non-success status raises the same typed exception as `request`.

## What it does not do

* It does not stream. The body is held in memory, as `ExpenseFile` is on upload
  (see [`multipart-uploads.md`](multipart-uploads.md)); a retry replays a request
  whose body is bytes, not a stream, and a receipt or an invoice fits in memory.
* It does not return the content type or the file name. The caller already knows
  which receipt it asked for.

## Not verified live

Expenses and Invoices need a paid plan, and the Free plan answers `403`, so
neither download has been checked against a real response. The OpenAPI spec
types both responses as `*/*` bytes.
