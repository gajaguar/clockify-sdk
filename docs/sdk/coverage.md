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
| `POST .../webhooks/{id}/logs`               | -                                   | planned |
| `GET .../webhooks/{id}/statuses`            | -                                   | planned |
| `GET .../addons/{addonId}/webhooks`         | -                                   | planned |

## Core API — Time off (Standard plan)

| Endpoint                                    | SDK method | Status  |
| ------------------------------------------- | ---------- | ------- |
| `GET .../policies`                          | -          | planned |
| `POST .../policies`                         | -          | planned |
| `GET .../policies/{id}`                     | -          | planned |
| `PUT .../policies/{id}`                     | -          | planned |
| `PATCH .../policies/{id}`                   | -          | planned |
| `DELETE .../policies/{id}`                  | -          | planned |
| `POST .../time-off-requests`                | -          | planned |
| `POST .../time-off-requests/users/{userId}` | -          | planned |
| `POST .../time-off-requests/all`            | -          | planned |
| `PATCH .../time-off-requests/{id}`          | -          | planned |
| `DELETE .../time-off-requests/{id}`         | -          | planned |
| `GET .../balance`                           | -          | planned |
| `GET .../balance/{userId}`                  | -          | planned |
| `PATCH .../balance/{balanceId}`             | -          | planned |

## Core API — Approvals (Standard plan)

| Endpoint                                                   | SDK method | Status  |
| ---------------------------------------------------------- | ---------- | ------- |
| `GET .../approval-requests`                                | -          | planned |
| `POST .../approval-requests/{type}`                        | -          | planned |
| `POST .../approval-requests/users/{userId}/{type}`         | -          | planned |
| `PATCH .../approval-requests/{id}`                         | -          | planned |
| `POST .../approval-requests/resubmit-entries-for-approval` | -          | planned |

## Core API — Expenses (Pro plan)

| Endpoint                             | SDK method | Status  |
| ------------------------------------ | ---------- | ------- |
| `GET .../expenses`                   | -          | planned |
| `POST .../expenses`                  | -          | planned |
| `GET .../expenses/{id}`              | -          | planned |
| `PUT .../expenses/{id}`              | -          | planned |
| `DELETE .../expenses/{id}`           | -          | planned |
| `GET .../expense-categories`         | -          | planned |
| `POST .../expense-categories`        | -          | planned |
| `PUT .../expense-categories/{id}`    | -          | planned |
| `PATCH .../expense-categories/{id}`  | -          | planned |
| `DELETE .../expense-categories/{id}` | -          | planned |

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
