---
type: convention
title: Credentials
description: The SDK reads the API key from an argument, a provider, or CLOCKIFY_API_KEY, and leaves acquiring and storing it to the application.
tags: [sdk, auth]
status: stable
---

# Credentials

The SDK resolves one credential, the API key, and never obtains or stores
it. Acquiring the key, asking the user for it and keeping it safe belong to
the application, as [`clockify-cli`](https://github.com/gajaguar/clockify-cli)
does. `bitbucket-sdk` follows the same contract with an email and an API
token.

## Sources and precedence

`resolve_api_key` in `src/clockify/config.py` returns the first source that
has a value:

1. A provider: a zero-argument callable passed as `api_key`.
2. The `api_key` string argument.
3. The `CLOCKIFY_API_KEY` environment variable, exported as
   `API_KEY_ENV_VAR`.

When none has a value it raises `MissingCredentialsError`. The message names
the argument, the variable and the page in Clockify where the key is
created.

## The provider

A provider is invoked inside `ApiKeyAuth.auth_flow` on every request and its
result is never cached, so a rotating or externally managed key is always
current. An empty result raises `MissingCredentialsError`.

## Where the key is created

Profile settings → Advanced → Manage API keys → Generate new. Clockify shows
the key once. It has no scopes and no OAuth flow.

## Keeping the key out of output

* `ClientConfig.api_key` uses `repr=False`, so a traceback that captures the
  configuration does not print the key.
* `Transport` logs only the method, the path, the status and the elapsed
  time. It never logs headers or the configuration.

## Auth is injected

`ClockifyClient` builds one `ApiKeyAuth` and passes it to each `Transport`.
A new credential type therefore arrives as another `httpx.Auth` subclass
without changing the transport.

## What the SDK does not do

No keyring or keychain, no password manager, no OAuth or SSO flow and no
interactive prompts. See the README's Authentication section.
