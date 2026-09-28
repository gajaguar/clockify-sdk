from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from clockify.errors import MissingCredentialsError

if TYPE_CHECKING:
    from collections.abc import Generator

    from clockify.config import ApiKeyProvider


class ApiKeyAuth(httpx.Auth):
    def __init__(self, api_key: str | ApiKeyProvider) -> None:
        self._api_key = api_key

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response]:
        # A callable is invoked on every request, never cached, so a rotating or
        # externally-managed key is always current.
        key = self._api_key() if callable(self._api_key) else self._api_key
        if not key:
            message = "The API key provider returned an empty value."
            raise MissingCredentialsError(message)
        request.headers["X-Api-Key"] = key
        yield request
