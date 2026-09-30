from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

import httpx

from clockify.errors import MissingCredentialsError

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Generator


class _HeaderAuth(httpx.Auth):
    _header: ClassVar[str]
    _label: ClassVar[str]

    def __init__(self, secret: str | Callable[[], str]) -> None:
        self._secret = secret

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response]:
        # A callable is invoked on every request, never cached, so a rotating or
        # externally-managed secret is always current.
        value = self._secret() if callable(self._secret) else self._secret
        if not value:
            message = f"The {self._label} provider returned an empty value."
            raise MissingCredentialsError(message)
        request.headers[self._header] = value
        yield request


class ApiKeyAuth(_HeaderAuth):
    _header = "X-Api-Key"
    _label = "API key"


class AddonTokenAuth(_HeaderAuth):
    _header = "X-Addon-Token"
    _label = "add-on token"
