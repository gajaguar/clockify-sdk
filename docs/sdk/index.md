---
okf_version: "0.2"
---

# SDK

How the SDK is layered, how a request flows, how it reads, protects and
tests the credentials its callers give it, and the process for adding a new
Clockify endpoint.

* [SDK layering](layering.md) - `ClockifyClient`, `WorkspaceClient`,
  resources, and `_transport`.
* [Request lifecycle](request-lifecycle.md) - the auth → retry →
  error-mapping → validation pipeline every request goes through.
* [Clockify API key](credentials.md) - the names the SDK uses for the API
  key, and where the key is created.
* [Credential contract](credential-contract.md) - the sources the SDK reads
  a credential from, their order, and how the credential stays out of logs
  and output.
* [Why the SDK does not acquire credentials](credential-sources.md) - the
  decision to read credentials, not to obtain or store them, with the
  alternatives it rejected.
* [Credential tests](credential-tests.md) - the tests every SDK carries to
  prove the contract.
* [Offset pagination](pagination.md) - how `list()` and `list_page()` hide
  Clockify's `page`/`page-size` pagination.
* [Endpoint comment convention](endpoint-comments.md) - the `# METHOD /path`
  comment every resource method carries.
* [Adding a new endpoint](adding-an-endpoint.md) - the six-step procedure.
* [Release checklist](release-checklist.md) - steps before tagging a
  release.
* [Endpoint coverage](coverage.md) - the endpoint-to-method mapping table.

See [`../log.md`](../log.md) for the bundle's change history.
