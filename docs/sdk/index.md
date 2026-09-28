---
okf_version: "0.2"
---

# SDK

How the SDK is layered, why it is layered that way, the request lifecycle,
and the process for adding a new Clockify endpoint. Replaces the former
`docs/ARCHITECTURE.md` and `docs/coverage.md`.

* [SDK layering](layering.md) - `ClockifyClient`, `WorkspaceClient`,
  resources, and `_transport`.
* [Request lifecycle](request-lifecycle.md) - the auth → retry →
  error-mapping → validation pipeline every request goes through.
* [Offset pagination](pagination.md) - how `list()` and `list_page()` hide
  Clockify's `page`/`page-size` pagination.
* [Endpoint comment convention](endpoint-comments.md) - the `# METHOD /path`
  comment every resource method carries.
* [Adding a new endpoint](adding-an-endpoint.md) - the six-step procedure.
* [Release checklist](release-checklist.md) - steps before tagging a
  release.
* [Endpoint coverage](coverage.md) - the endpoint-to-method mapping table.

See [`../log.md`](../log.md) for the bundle's change history.
