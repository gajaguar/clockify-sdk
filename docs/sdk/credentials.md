---
type: reference
title: Clockify credentials
description: The names the SDK uses for the Clockify API key and add-on token, and where each is created.
tags: [sdk, auth]
status: stable
---

# Clockify credentials

The SDK follows the [credential contract](credential-contract.md). This note
holds the values that belong to Clockify. The two credentials are mutually
exclusive.

## API key

* **Argument:** `ClockifyClient(api_key=...)`, a string or a provider.
* **Environment variable:** `CLOCKIFY_API_KEY`, exported as `API_KEY_ENV_VAR`.
* **Provider type:** `ApiKeyProvider`.
* **Resolver:** `resolve_api_key` in `src/clockify/config.py`.
* **Header:** `X-Api-Key`, set by `ApiKeyAuth` in `src/clockify/_auth.py`.
* **Where it is created:** Profile settings → Advanced → Manage API keys →
  Generate new. Clockify shows the key once.

## Add-on token

* **Argument:** `ClockifyClient(addon_token=...)`, a string or a provider.
* **Environment variable:** `CLOCKIFY_ADDON_TOKEN`, exported as
  `ADDON_TOKEN_ENV_VAR`.
* **Provider type:** `AddonTokenProvider`.
* **Resolver:** `resolve_addon_token` in `src/clockify/config.py`.
* **Header:** `X-Addon-Token`, set by `AddonTokenAuth` in
  `src/clockify/_auth.py`.
* **Where it comes from:** Clockify issues it to an add-on when the add-on is
  installed in a workspace. Its rate limit is 50 requests per second per
  workspace.

## Choosing between them

`resolve_credentials` returns exactly one. Two explicit arguments, or two
environment variables with no argument, raise a `ConfigurationError`. An
explicit argument beats the other credential's environment variable.

## Shared

* **Scopes and OAuth:** none.
* **Errors:** `MissingCredentialsError` when no source has a value,
  `ConfigurationError` when both credentials are given,
  `AuthenticationError` for a `401` and `ForbiddenError` for a `403`.
