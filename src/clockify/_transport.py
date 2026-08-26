from __future__ import annotations

from logging import NullHandler
from logging import getLogger
from typing import TYPE_CHECKING
from typing import Any
from typing import Final
from typing import cast

import httpx

from clockify._auth import ApiKeyAuth
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

type JSONValue = (  # pylint: disable=app-module-const-naming
    bool | int | float | str | list[JSONValue] | dict[str, JSONValue] | None
)


def _elapsed_ms(response: httpx.Response) -> float:
    try:
        return response.elapsed.total_seconds() * 1000
    except RuntimeError:
        # Timing is unavailable when the response never went through a real network
        # transport (mocked transports in tests). Logging must not fail because of it.
        return 0.0


class Transport:
    def __init__(
        self,
        config: ClientConfig,
        base_url: str,
        *,
        event_hooks: dict[str, list[Callable[..., Any]]] | None = None,
    ) -> None:
        self._config = config
        self._client = httpx.Client(
            base_url=base_url,
            auth=ApiKeyAuth(config.api_key),
            timeout=config.timeout,
            transport=RetryTransport(httpx.HTTPTransport(), policy=config.retry),
            headers={"User-Agent": config.user_agent},
            event_hooks=event_hooks or {},
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        kind: CqsKind,
        params: Mapping[str, str | int | float | bool | None] | None = None,
        json: JSONValue = None,
    ) -> JSONValue:
        try:
            response = self._client.request(
                method,
                path,
                params=params,
                json=json,
                extensions={"clockify_cqs": kind},
            )
        except httpx.TransportError as exc:
            raise TransportError(str(exc)) from exc
        # Only primitives are logged; headers and the config object are never logged so the
        # X-Api-Key value cannot leak into a caller's log sink.
        elapsed_ms = _elapsed_ms(response)
        LOGGER.debug("%s %s -> %s (%.1fms)", method, path, response.status_code, elapsed_ms)
        if response.status_code == _NO_CONTENT:
            return None
        if not response.is_success:
            raise error_for_response(response)
        # httpx's Response.json() is typed Any; the wire body is trusted to be the JSON
        # subset the JSONValue alias describes, per Clockify's documented content type.
        return cast("JSONValue", response.json())

    def close(self) -> None:
        self._client.close()
