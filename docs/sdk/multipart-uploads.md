---
type: decision
title: Multipart uploads
description: Why creating and updating an expense sends multipart/form-data from bytes, how a retry replays it, and why the file download is not covered yet.
tags: [sdk, expenses, transport]
status: stable
---

# Multipart uploads

`POST` and `PUT .../expenses` take `multipart/form-data`, not JSON. Expenses is
a Pro-plan feature and the account the SDK was built on is on the Free plan, so
Clockify answers `403` (`ForbiddenError`) and **the Expenses models and requests
are not verified against a real response**; they follow the OpenAPI spec, with
every doubtful field optional.

## How the body is sent

`Transport.request` and `AsyncTransport.request` accept a `Multipart` object in
the `json` argument. It carries the parts as httpx's `files=` takes them, and
the transport passes it on instead of a JSON body. Every field, text included, is
a part, so an update without a file is still `multipart/form-data`. A list field
(`changeFields`) is repeated, one part per value. The authentication and the
logging do not change: only the method, the path, the status and the elapsed time
are logged.

## Bytes, not streams

`ExpenseFile` holds `content: bytes`. The retry transport resends the same
request after a `429` or, for an idempotent command, a `5xx`; a stream that a
first attempt consumed cannot be replayed, while httpx renders `bytes` again on
every attempt. The price is that a file is held in memory, which a receipt can
afford. A creation is a non-idempotent command, so it retries only on `429`.

## The file download is not covered

`GET .../expenses/{id}/files/{fileId}` answers with raw bytes, and the transport
decodes every success as JSON. Supporting it needs a second response path in
both transports and cannot be checked without a Pro workspace, so it stays
`planned` in [`coverage.md`](coverage.md).
