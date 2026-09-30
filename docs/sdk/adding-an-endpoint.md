---
type: playbook
title: Adding a new endpoint
description: The six-step procedure for wiring up a new Clockify endpoint, from the pydantic model through coverage.md.
tags: [sdk]
status: stable
---

# Adding a new endpoint

1. Add or extend the pydantic model(s) in `src/clockify/models/`. Read
   models and write models (`XCreate`/`XUpdate`) are separate types; write
   models must not carry server-assigned fields.
2. Add the method to the relevant resource in `src/clockify/resources/`,
   following the CRUD naming contract (`list`/`list_page` → `get` → `create`
   → `update` → `delete`, each returning the corresponding model). Prefix it
   with a `# METHOD /path` comment — see
   [`endpoint-comments.md`](endpoint-comments.md). Add the same method to the
   async twin in the same module (`Async...Resource`, see
   [`async-client.md`](async-client.md)) with the same comment and CQS kind.
3. Declare the method's CQS kind — query, idempotent command, or
   non-idempotent command. The retry transport reads it to decide `5xx`
   eligibility, so getting it wrong either strips retry protection from a
   read or risks duplicating a write. Reports are queries despite being
   `POST`.
4. Add a unit test in `tests/unit/` asserting the exact HTTP method, path,
   query parameters, and body the method produces (respx), for both the sync
   and the async method.
5. Update [`coverage.md`](coverage.md): flip the endpoint's status to `done`
   and link the method.
6. Run `make check && make test` before committing.
