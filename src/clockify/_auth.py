from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from collections.abc import Generator


class ApiKeyAuth(httpx.Auth):
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response]:
        request.headers["X-Api-Key"] = self._api_key
        yield request
