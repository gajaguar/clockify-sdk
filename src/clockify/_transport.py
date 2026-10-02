from __future__ import annotations

from dataclasses import dataclass
from logging import NullHandler
from logging import getLogger
from typing import TYPE_CHECKING
from typing import Any
from typing import Final
from typing import cast

import httpx

from clockify._retry_transport import AsyncRetryTransport
from clockify._retry_transport import RetryTransport
from clockify.errors import TransportError
from clockify.errors import error_for_response

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Mapping

    from clockify.config import ClientConfig
    from clockify.retry import CqsKind

LOGGER: Final = getLogger("clockify")
LOGGER.addHandler(NullHandler())

_NO_CONTENT: Final = 204

type JSONValue = (  # pylint: disable=gajaguar-module-const-naming
    bool | int | float | str | list[JSONValue] | dict[str, JSONValue] | None
)


# (filename or None for a plain form field, content, content type or None), as httpx's
# `files=` takes it. Bytes only, so a retry can resend the same body.
type MultipartPart = tuple[str | None, bytes, str | None]  # pylint: disable=gajaguar-module-const-naming


@dataclass(frozen=True, slots=True)
class Multipart:
    # A multipart/form-data body, passed through the `json` argument of `request` so the
    # signature stays within the argument limit and existing callers keep working.
    parts: tuple[tuple[str, MultipartPart], ...]


def _body_kwargs(body: JSONValue | Multipart) -> dict[str, Any]:
    if isinstance(body, Multipart):
        return {"files": list(body.parts)}
    return {"json": body}


def _elapsed_ms(response: httpx.Response) -> float:
    try:
        return response.elapsed.total_seconds() * 1000
    except RuntimeError:
        # Timing is unavailable when the response never went through a real network
        # transport (mocked transports in tests). Logging must not fail because of it.
        return 0.0


def _check_response(method: str, path: str, response: httpx.Response) -> None:
    # Only primitives are logged; headers and the config object are never logged so the
    # X-Api-Key / X-Addon-Token value cannot leak into a caller's log sink.
    elapsed_ms = _elapsed_ms(response)
    LOGGER.debug("%s %s -> %s (%.1fms)", method, path, response.status_code, elapsed_ms)
    if not response.is_success:
        raise error_for_response(response)


def _handle_response(method: str, path: str, response: httpx.Response) -> JSONValue:
    _check_response(method, path, response)
    # Clockify answers some deletes (webhooks) with 200 and no body, not 204.
    if response.status_code == _NO_CONTENT or not response.content:
        return None
    # httpx's Response.json() is typed Any; the wire body is trusted to be the JSON
    # subset the JSONValue alias describes, per Clockify's documented content type.
    return cast("JSONValue", response.json())


class Transport:
    def __init__(
        self,
        config: ClientConfig,
        base_url: str,
        auth: httpx.Auth,
        *,
        event_hooks: dict[str, list[Callable[..., Any]]] | None = None,
    ) -> None:
        self._config = config
        self._client = httpx.Client(
            base_url=base_url,
            auth=auth,
            timeout=config.timeout,
            transport=RetryTransport(httpx.HTTPTransport(), policy=config.retry),
            headers={"User-Agent": config.user_agent},
            event_hooks=event_hooks or {},
        )

    def _send(
        self,
        method: str,
        path: str,
        kind: CqsKind,
        params: Mapping[str, str | int | float | bool | list[str] | None] | None,
        json: JSONValue | Multipart,
    ) -> httpx.Response:
        try:
            return self._client.request(
                method,
                path,
                params=params,
                **_body_kwargs(json),
                extensions={"clockify_cqs": kind},
            )
        except httpx.TransportError as exc:
            raise TransportError(str(exc)) from exc

    def request(
        self,
        method: str,
        path: str,
        *,
        kind: CqsKind,
        params: Mapping[str, str | int | float | bool | list[str] | None] | None = None,
        json: JSONValue | Multipart = None,
    ) -> JSONValue:
        return _handle_response(method, path, self._send(method, path, kind, params, json))

    # For an endpoint that answers with a file, not JSON: the body is returned as it came.
    def request_bytes(
        self,
        method: str,
        path: str,
        *,
        kind: CqsKind,
        params: Mapping[str, str | int | float | bool | list[str] | None] | None = None,
    ) -> bytes:
        response = self._send(method, path, kind, params, None)
        _check_response(method, path, response)
        return response.content

    def close(self) -> None:
        self._client.close()


class AsyncTransport:
    def __init__(
        self,
        config: ClientConfig,
        base_url: str,
        auth: httpx.Auth,
        *,
        event_hooks: dict[str, list[Callable[..., Any]]] | None = None,
    ) -> None:
        self._config = config
        self._client = httpx.AsyncClient(
            base_url=base_url,
            auth=auth,
            timeout=config.timeout,
            transport=AsyncRetryTransport(httpx.AsyncHTTPTransport(), policy=config.retry),
            headers={"User-Agent": config.user_agent},
            event_hooks=event_hooks or {},
        )

    async def _send(
        self,
        method: str,
        path: str,
        kind: CqsKind,
        params: Mapping[str, str | int | float | bool | list[str] | None] | None,
        json: JSONValue | Multipart,
    ) -> httpx.Response:
        try:
            return await self._client.request(
                method,
                path,
                params=params,
                **_body_kwargs(json),
                extensions={"clockify_cqs": kind},
            )
        except httpx.TransportError as exc:
            raise TransportError(str(exc)) from exc

    async def request(
        self,
        method: str,
        path: str,
        *,
        kind: CqsKind,
        params: Mapping[str, str | int | float | bool | list[str] | None] | None = None,
        json: JSONValue | Multipart = None,
    ) -> JSONValue:
        return _handle_response(method, path, await self._send(method, path, kind, params, json))

    # For an endpoint that answers with a file, not JSON: the body is returned as it came.
    async def request_bytes(
        self,
        method: str,
        path: str,
        *,
        kind: CqsKind,
        params: Mapping[str, str | int | float | bool | list[str] | None] | None = None,
    ) -> bytes:
        response = await self._send(method, path, kind, params, None)
        _check_response(method, path, response)
        return response.content

    async def aclose(self) -> None:
        await self._client.aclose()
