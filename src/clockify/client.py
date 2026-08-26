from __future__ import annotations

from typing import Self

from clockify._transport import Transport
from clockify.config import ClientConfig
from clockify.config import ClientOptions
from clockify.config import resolve_api_key
from clockify.config import resolve_urls
from clockify.resources.user import UserResource
from clockify.retry import RetryPolicy


class ClockifyClient:
    def __init__(self, api_key: str | None = None, *, options: ClientOptions | None = None) -> None:
        resolved_options = options or ClientOptions()
        resolved_key = resolve_api_key(api_key)
        resolved_base, resolved_reports = resolve_urls(
            resolved_options.region, resolved_options.base_url, resolved_options.reports_base_url
        )
        self._config = ClientConfig(
            api_key=resolved_key,
            base_url=resolved_base,
            reports_base_url=resolved_reports,
            timeout=resolved_options.timeout,
            retry=resolved_options.retry or RetryPolicy(),
        )
        self._transport = Transport(self._config, resolved_base, event_hooks=resolved_options.event_hooks)
        self._reports_transport = Transport(self._config, resolved_reports, event_hooks=resolved_options.event_hooks)
        self.user = UserResource(self._transport)

    def close(self) -> None:
        self._transport.close()
        self._reports_transport.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
