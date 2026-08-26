# Endpoint coverage

Authoritative mapping of every documented Clockify endpoint in scope (see
[`TECH_SPEC.md`](TECH_SPEC.md) §1.1) to its SDK method and implementation
status. Updated as each phase in `TECH_SPEC.md` §10 lands. This table is the
verifiable definition of "covers all actions" — an endpoint with no row, or a
row not marked `done`, is not yet supported.

Status values: `planned`, `in-progress`, `done`.

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
| `POST .../user-groups/{userGroupId}/users`            | `ws.user_groups.add_user(...)`       | planned |
| `DELETE .../user-groups/{userGroupId}/users/{userId}` | `ws.user_groups.remove_user(...)`    | planned |

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
