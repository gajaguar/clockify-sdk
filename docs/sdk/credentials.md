---
type: reference
title: Clockify API key
description: The names the SDK uses for the Clockify API key, and where the key is created.
tags: [sdk, auth]
status: stable
---

# Clockify API key

The SDK follows the [credential contract](credential-contract.md). This note
holds the values that belong to Clockify.

* **Credential:** one API key.
* **Argument:** `ClockifyClient(api_key=...)`, a string or a provider.
* **Environment variable:** `CLOCKIFY_API_KEY`, exported as `API_KEY_ENV_VAR`.
* **Provider type:** `ApiKeyProvider`.
* **Resolver:** `resolve_api_key` in `src/clockify/config.py`.
* **Header:** `X-Api-Key`, set by `ApiKeyAuth` in `src/clockify/_auth.py`.
* **Where it is created:** Profile settings → Advanced → Manage API keys →
  Generate new. Clockify shows the key once.
* **Scopes and OAuth:** none. An API key is the only credential.
* **Errors:** `MissingCredentialsError` when no source has a value,
  `AuthenticationError` for a `401` and `ForbiddenError` for a `403`.
