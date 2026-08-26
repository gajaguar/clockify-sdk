# Endpoint coverage

Authoritative mapping of every documented Clockify endpoint in scope (see
[`TECH_SPEC.md`](TECH_SPEC.md) §1.1) to its SDK method and implementation
status. Updated as each phase in `TECH_SPEC.md` §10 lands. This table is the
verifiable definition of "covers all actions" — an endpoint with no row, or a
row not marked `done`, is not yet supported.

Status values: `planned`, `in-progress`, `done`.

## Core API — Workspaces

| Endpoint                        | SDK method                  | Status  |
| ------------------------------- | --------------------------- | ------- |
| `GET /workspaces`               | `client.workspaces.list()`  | planned |
| `GET /workspaces/{workspaceId}` | `client.workspaces.get(id)` | planned |

## Core API — Projects

| Endpoint                                         | SDK method                        | Status  |
| ------------------------------------------------ | --------------------------------- | ------- |
| `GET /workspaces/{workspaceId}/projects`         | `ws.projects.list()`              | planned |
| `GET /workspaces/{workspaceId}/projects/{id}`    | `ws.projects.get(id)`             | planned |
| `POST /workspaces/{workspaceId}/projects`        | `ws.projects.create(payload)`     | planned |
| `PUT /workspaces/{workspaceId}/projects/{id}`    | `ws.projects.update(id, payload)` | planned |
| `DELETE /workspaces/{workspaceId}/projects/{id}` | `ws.projects.delete(id)`          | planned |

## Core API — Tasks

| Endpoint                                     | SDK method                                 | Status  |
| -------------------------------------------- | ------------------------------------------ | ------- |
| `GET .../projects/{projectId}/tasks`         | `ws.tasks.list(project_id)`                | planned |
| `GET .../projects/{projectId}/tasks/{id}`    | `ws.tasks.get(project_id, id)`             | planned |
| `POST .../projects/{projectId}/tasks`        | `ws.tasks.create(project_id, payload)`     | planned |
| `PUT .../projects/{projectId}/tasks/{id}`    | `ws.tasks.update(project_id, id, payload)` | planned |
| `DELETE .../projects/{projectId}/tasks/{id}` | `ws.tasks.delete(project_id, id)`          | planned |

## Core API — Time entries

| Endpoint                               | SDK method                            | Status  |
| -------------------------------------- | ------------------------------------- | ------- |
| `GET .../user/{userId}/time-entries`   | `ws.time_entries.list(user_id)`       | planned |
| `GET .../time-entries/{id}`            | `ws.time_entries.get(id)`             | planned |
| `POST .../time-entries`                | `ws.time_entries.create(payload)`     | planned |
| `PUT .../time-entries/{id}`            | `ws.time_entries.update(id, payload)` | planned |
| `PATCH .../user/{userId}/time-entries` | `ws.time_entries.stop(user_id)`       | planned |
| `DELETE .../time-entries/{id}`         | `ws.time_entries.delete(id)`          | planned |

## Core API — Clients, tags, custom fields

| Endpoint                | SDK method                   | Status  |
| ----------------------- | ---------------------------- | ------- |
| `GET .../clients`       | `ws.clients.list()`          | planned |
| `POST .../clients`      | `ws.clients.create(payload)` | planned |
| `GET .../tags`          | `ws.tags.list()`             | planned |
| `POST .../tags`         | `ws.tags.create(payload)`    | planned |
| `GET .../custom-fields` | `ws.custom_fields.list()`    | planned |

## Users and user groups

| Endpoint             | SDK method              | Status  |
| -------------------- | ----------------------- | ------- |
| `GET /user`          | `client.user.me()`      | done    |
| `GET .../users`      | `ws.users.list()`       | planned |
| `GET .../userGroups` | `ws.user_groups.list()` | planned |

## Reports API

| Endpoint                                          | SDK method                     | Status  |
| ------------------------------------------------- | ------------------------------ | ------- |
| `POST /workspaces/{workspaceId}/reports/summary`  | `ws.reports.summary(request)`  | planned |
| `POST /workspaces/{workspaceId}/reports/detailed` | `ws.reports.detailed(request)` | planned |
| `POST /workspaces/{workspaceId}/reports/weekly`   | `ws.reports.weekly(request)`   | planned |
| `GET /shared-reports/{id}`                        | `ws.reports.shared(id)`        | planned |

## Out of scope (v1)

PTO/Time-off, Approvals, Webhooks, Expenses/Invoices (pending confirmation —
see `TECH_SPEC.md` §12 open item 1). Not tracked in this table until promoted
into scope.
