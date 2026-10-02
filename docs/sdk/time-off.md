---
type: guide
title: Time off
description: How the three time-off resources map onto Clockify's routes, which of their calls read despite the verb, and why a balance change is not retried.
tags: [sdk, time-off]
status: stable
---

# Time off

Time off is a Standard-plan feature. The account the SDK was built on is on the
Free plan, so Clockify answers `403` (`ForbiddenError`) and **the Time off models
and requests are not verified against a real response**; they follow the OpenAPI
spec, with every doubtful field optional.

## Three resources, not one

The API has no single `time-off` collection, so the SDK splits it by the thing
each route acts on:

* `ws.time_off_policies` — `.../time-off/policies`, with the usual
  `list`/`get`/`create`/`update`/`delete` and `update_status` (`PATCH`, which only
  archives or restores).
* `ws.time_off_requests` — a request hangs off its policy
  (`.../policies/{policyId}/requests`), so `create`, `create_for_user`,
  `update_status` (approve or reject) and `delete` take the policy id first. There
  is no endpoint to read one request.
* `ws.time_off_balances` — read per policy or per user, changed by `update`, and
  managed through balance assignments.

## `time_off_requests.list()` is a `POST` that reads

`POST .../time-off/requests` lists the requests of the workspace and takes its
filter and its `page`/`pageSize` in the body. The SDK declares it a query, so a
`5xx` is retried, and `TimeOffRequestFilter.as_body()` renders the filter as JSON
instead of query parameters.

## A balance change is not retried on `5xx`

`PATCH .../balance/policy/{policyId}` sends `value`, and
`PUT .../balance/assignment/...` sends `balanceChange`: both are **changes**, not
the new balance. Repeating either after a `5xx` could apply it twice, so both are
declared non-idempotent commands even though their verbs are idempotent by
convention. `delete_assignment` sends a `DELETE` with a JSON body (`note`).

## Dates

The write models take `datetime.date` and send `YYYY-MM-DD`, as the spec's
`DateRangeV1Request` and `PeriodV1Request` ask. The read models return instants.
