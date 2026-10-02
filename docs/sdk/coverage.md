---
type: reference
title: Endpoint coverage
description: Authoritative mapping of every documented Clockify endpoint in scope to its SDK method and implementation status.
tags: [sdk]
status: stable
---

# Endpoint coverage

Authoritative mapping of every documented Clockify endpoint in scope to its
SDK method and implementation status. This table is the verifiable definition
of "covers all actions" — an endpoint with no row, or a row not marked
`done`, is not yet supported.

Status values: `planned`, `in-progress`, `done`.

A section whose heading names a plan is available only from that plan up. On a
lower plan Clockify answers `403`, which the SDK raises as `ForbiddenError`.

## Core API — Workspaces

| Endpoint                        | SDK method                  | Status |
| ------------------------------- | --------------------------- | ------ |
| `GET /workspaces`               | `client.workspaces.list()`  | done   |
| `GET /workspaces/{workspaceId}` | `client.workspaces.get(id)` | done   |

## Core API — Projects

| Endpoint                                         | SDK method                        | Status  |
| ------------------------------------------------ | --------------------------------- | ------- |
| `GET /workspaces/{workspaceId}/projects`         | `ws.projects.list()`              | done    |
| `GET /workspaces/{workspaceId}/projects/{id}`    | `ws.projects.get(id)`             | done    |
| `POST /workspaces/{workspaceId}/projects`        | `ws.projects.create(payload)`     | done    |
| `PUT /workspaces/{workspaceId}/projects/{id}`    | `ws.projects.update(id, payload)` | done    |
| `DELETE /workspaces/{workspaceId}/projects/{id}` | `ws.projects.delete(id)`          | done    |

## Core API — Tasks

| Endpoint                                     | SDK method                                 | Status  |
| -------------------------------------------- | ------------------------------------------ | ------- |
| `GET .../projects/{projectId}/tasks`         | `ws.tasks.list(project_id)`                | done    |
| `GET .../projects/{projectId}/tasks/{id}`    | `ws.tasks.get(project_id, id)`             | done    |
| `POST .../projects/{projectId}/tasks`        | `ws.tasks.create(project_id, payload)`     | done    |
| `PUT .../projects/{projectId}/tasks/{id}`    | `ws.tasks.update(project_id, id, payload)` | done    |
| `DELETE .../projects/{projectId}/tasks/{id}` | `ws.tasks.delete(project_id, id)`          | done    |

## Core API — Time entries

| Endpoint                               | SDK method                                        | Status |
| -------------------------------------- | ------------------------------------------------- | ------ |
| `GET .../user/{userId}/time-entries`   | `ws.time_entries.list(user_id, entry_filter=...)` | done   |
| `GET .../time-entries/{id}`            | `ws.time_entries.get(id)`                         | done   |
| `POST .../time-entries`                | `ws.time_entries.create(payload)`                 | done   |
| `POST .../user/{userId}/time-entries`  | `ws.time_entries.start(user_id, payload)`         | done   |
| `PUT .../time-entries/{id}`            | `ws.time_entries.update(id, payload)`             | done   |
| `PATCH .../user/{userId}/time-entries` | `ws.time_entries.stop(user_id, end=None)`         | done   |
| `DELETE .../time-entries/{id}`         | `ws.time_entries.delete(id)`                      | done   |

## Core API — Clients, tags, custom fields

| Endpoint                        | SDK method                             | Status |
| ------------------------------- | -------------------------------------- | ------ |
| `GET .../clients`               | `ws.clients.list()`                    | done   |
| `GET .../clients/{id}`          | `ws.clients.get(id)`                   | done   |
| `POST .../clients`              | `ws.clients.create(payload)`           | done   |
| `PUT .../clients/{id}`          | `ws.clients.update(id, payload)`       | done   |
| `DELETE .../clients/{id}`       | `ws.clients.delete(id)`                | done   |
| `GET .../tags`                  | `ws.tags.list()`                       | done   |
| `GET .../tags/{id}`             | `ws.tags.get(id)`                      | done   |
| `POST .../tags`                 | `ws.tags.create(payload)`              | done   |
| `PUT .../tags/{id}`             | `ws.tags.update(id, payload)`          | done   |
| `DELETE .../tags/{id}`          | `ws.tags.delete(id)`                   | done   |
| `GET .../custom-fields`         | `ws.custom_fields.list()`              | done   |
| `POST .../custom-fields`        | `ws.custom_fields.create(payload)`     | done   |
| `PUT .../custom-fields/{id}`    | `ws.custom_fields.update(id, payload)` | done   |
| `DELETE .../custom-fields/{id}` | `ws.custom_fields.delete(id)`          | done   |

## Users and user groups

| Endpoint                                              | SDK method                           | Status  |
| ----------------------------------------------------- | ------------------------------------ | ------- |
| `GET /user`                                           | `client.user.me()`                   | done    |
| `GET .../users`                                       | `ws.users.list()`                    | done    |
| `GET .../user-groups`                                 | `ws.user_groups.list()`              | done    |
| `POST .../user-groups`                                | `ws.user_groups.create(payload)`     | done    |
| `PUT .../user-groups/{id}`                            | `ws.user_groups.update(id, payload)` | done    |
| `DELETE .../user-groups/{id}`                         | `ws.user_groups.delete(id)`          | done    |
| `POST .../user-groups/{userGroupId}/users`            | `ws.user_groups.add_user(...)`       | done    |
| `DELETE .../user-groups/{userGroupId}/users/{userId}` | `ws.user_groups.remove_user(...)`    | done    |

## Core API — Webhooks

| Endpoint                                    | SDK method                          | Status  |
| ------------------------------------------- | ----------------------------------- | ------- |
| `GET .../webhooks`                          | `ws.webhooks.list(webhook_type=)`   | done    |
| `GET .../webhooks/{id}`                     | `ws.webhooks.get(id)`               | done    |
| `POST .../webhooks`                         | `ws.webhooks.create(payload)`       | done    |
| `PUT .../webhooks/{id}`                     | `ws.webhooks.update(id, payload)`   | done    |
| `DELETE .../webhooks/{id}`                  | `ws.webhooks.delete(id)`            | done    |
| `PATCH .../webhooks/{id}/token`             | `ws.webhooks.regenerate_token(id)`  | done    |
| `POST .../webhooks/{id}/logs`               | `ws.webhooks.logs(id, search=)`     | done    |
| `GET .../webhooks/{id}/statuses`            | `ws.webhooks.statuses(id, status=)` | done    |
| `GET .../addons/{addonId}/webhooks`         | `ws.webhooks.list_for_addon(id)`    | done    |

## Core API — Time off (Standard plan)

The models follow the OpenAPI spec and are not verified against a real response;
see [`time-off.md`](time-off.md). The routes are the spec's, not the ones this
table listed before: a request hangs off its policy, and the balance has no
`GET .../balance`.

| Endpoint                                                                      | SDK method                                                          | Status |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------- | ------ |
| `GET .../time-off/policies`                                                   | `ws.time_off_policies.list(policy_filter=)`                         | done   |
| `POST .../time-off/policies`                                                  | `ws.time_off_policies.create(payload)`                              | done   |
| `GET .../time-off/policies/{id}`                                              | `ws.time_off_policies.get(id)`                                      | done   |
| `PUT .../time-off/policies/{id}`                                              | `ws.time_off_policies.update(id, payload)`                          | done   |
| `PATCH .../time-off/policies/{id}`                                            | `ws.time_off_policies.update_status(id, payload)`                   | done   |
| `DELETE .../time-off/policies/{id}`                                           | `ws.time_off_policies.delete(id)`                                   | done   |
| `POST .../time-off/requests`                                                  | `ws.time_off_requests.list(request_filter=)`                        | done   |
| `POST .../time-off/policies/{policyId}/requests`                              | `ws.time_off_requests.create(policy_id, payload)`                   | done   |
| `POST .../time-off/policies/{policyId}/users/{userId}/requests`               | `ws.time_off_requests.create_for_user(policy_id, user_id, payload)` | done   |
| `PATCH .../time-off/policies/{policyId}/requests/{requestId}`                 | `ws.time_off_requests.update_status(policy_id, request_id, body)`   | done   |
| `DELETE .../time-off/policies/{policyId}/requests/{requestId}`                | `ws.time_off_requests.delete(policy_id, request_id)`                | done   |
| `GET .../time-off/balance/policy/{policyId}`                                  | `ws.time_off_balances.list_for_policy(policy_id, balance_filter=)`  | done   |
| `GET .../time-off/balance/user/{userId}`                                      | `ws.time_off_balances.list_for_user(user_id, balance_filter=)`      | done   |
| `PATCH .../time-off/balance/policy/{policyId}`                                | `ws.time_off_balances.update(policy_id, payload)`                   | done   |
| `POST .../time-off/balance/assignment`                                        | `ws.time_off_balances.create_assignment(payload)`                   | done   |
| `GET .../time-off/balance/assignment/user/{userId}/policy/{policyId}`         | `ws.time_off_balances.list_assignments(user_id, policy_id)`         | done   |
| `PUT .../time-off/balance/assignment/{id}/user/{userId}/policy/{policyId}`    | `ws.time_off_balances.update_assignment(id, user_id, policy_id, p)` | done   |
| `DELETE .../time-off/balance/assignment/{id}/user/{userId}/policy/{policyId}` | `ws.time_off_balances.delete_assignment(id, user_id, policy_id, p)` | done   |

## Core API — Approvals (Standard plan)

| Endpoint                                                   | SDK method                                             | Status |
| ---------------------------------------------------------- | ------------------------------------------------------ | ------ |
| `GET .../approval-requests`                                | `ws.approvals.list(request_filter=)`                   | done   |
| `POST .../approval-requests/{type}`                        | `ws.approvals.submit(type, payload)`                   | done   |
| `POST .../approval-requests/users/{userId}/{type}`         | `ws.approvals.submit_for_user(user_id, type, payload)` | done   |
| `PATCH .../approval-requests/{id}`                         | `ws.approvals.update(id, payload)`                     | done   |
| `POST .../approval-requests/resubmit-entries-for-approval` | `ws.approvals.resubmit(payload)`                       | done   |

## Core API — Expenses (Pro plan)

The models follow the OpenAPI spec and are not verified against a real response;
see [`multipart-uploads.md`](multipart-uploads.md). The file download returns
bytes; see [`binary-downloads.md`](binary-downloads.md).

| Endpoint                                      | SDK method                                      | Status  |
| --------------------------------------------- | ----------------------------------------------- | ------- |
| `GET .../expenses`                            | `ws.expenses.list(user_id=)`                    | done    |
| `POST .../expenses`                           | `ws.expenses.create(payload)`                   | done    |
| `GET .../expenses/{id}`                       | `ws.expenses.get(id)`                           | done    |
| `PUT .../expenses/{id}`                       | `ws.expenses.update(id, payload)`               | done    |
| `DELETE .../expenses/{id}`                    | `ws.expenses.delete(id)`                        | done    |
| `GET .../expenses/{id}/files/{fileId}`        | `ws.expenses.download_file(id, file_id)`        | done    |
| `GET .../expenses/categories`                 | `ws.expense_categories.list(category_filter=)`  | done    |
| `POST .../expenses/categories`                | `ws.expense_categories.create(payload)`         | done    |
| `PUT .../expenses/categories/{id}`            | `ws.expense_categories.update(id, payload)`     | done    |
| `PATCH .../expenses/categories/{id}/status`   | `ws.expense_categories.update_status(id, body)` | done    |
| `DELETE .../expenses/categories/{id}`         | `ws.expense_categories.delete(id)`              | done    |

## Core API — Invoices (Standard plan)

| Endpoint                                        | SDK method | Status  |
| ----------------------------------------------- | ---------- | ------- |
| `GET .../invoices`                              | -          | planned |
| `POST .../invoices`                             | -          | planned |
| `GET .../invoices/{id}`                         | -          | planned |
| `PUT .../invoices/{id}`                         | -          | planned |
| `DELETE .../invoices/{id}`                      | -          | planned |
| `POST .../invoices/{id}/duplicate`              | -          | planned |
| `GET .../invoices/{id}/export`                  | -          | planned |
| `POST .../invoices/{id}/items`                  | -          | planned |
| `DELETE .../invoices/{id}/items/{itemId}`       | -          | planned |
| `POST .../invoices/{id}/payments`               | -          | planned |
| `DELETE .../invoices/{id}/payments/{paymentId}` | -          | planned |

## Reports API

| Endpoint                                          | SDK method                              | Status |
| ------------------------------------------------- | --------------------------------------- | ------ |
| `POST /workspaces/{workspaceId}/reports/summary`  | `ws.reports.summary(request)`           | done   |
| `POST /workspaces/{workspaceId}/reports/detailed` | `ws.reports.detailed(request)`          | done   |
| `POST /workspaces/{workspaceId}/reports/weekly`   | `ws.reports.weekly(request)`            | done   |
| `GET /shared-reports/{id}`                        | `ws.reports.shared(id, query=None)`     | done   |
