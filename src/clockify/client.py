from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Self

from clockify._auth import AddonTokenAuth
from clockify._auth import ApiKeyAuth
from clockify._transport import AsyncTransport
from clockify._transport import Transport
from clockify.config import ClientConfig
from clockify.config import ClientOptions
from clockify.config import resolve_credentials
from clockify.config import resolve_urls
from clockify.errors import ConfigurationError
from clockify.ids import WorkspaceId
from clockify.resources.user import AsyncUserResource
from clockify.resources.user import UserResource
from clockify.resources.workspaces import AsyncWorkspacesResource
from clockify.resources.workspaces import WorkspacesResource
from clockify.retry import RetryPolicy
from clockify.workspace import AsyncWorkspaceClient
from clockify.workspace import WorkspaceClient

if TYPE_CHECKING:
    from clockify.config import AddonTokenProvider
    from clockify.config import ApiKeyProvider


def _build_config_and_auth(
    api_key: str | ApiKeyProvider | None, addon_token: str | AddonTokenProvider | None, options: ClientOptions | None
) -> tuple[ClientConfig, ApiKeyAuth | AddonTokenAuth]:
    resolved_options = options or ClientOptions()
    resolved_key, resolved_token = resolve_credentials(api_key, addon_token)
    resolved_base, resolved_reports = resolve_urls(
        resolved_options.region, resolved_options.base_url, resolved_options.reports_base_url
    )
    config = ClientConfig(
        api_key=resolved_key,
        addon_token=resolved_token,
        base_url=resolved_base,
        reports_base_url=resolved_reports,
        timeout=resolved_options.timeout,
        retry=resolved_options.retry or RetryPolicy(),
    )
    auth: ApiKeyAuth | AddonTokenAuth
    if resolved_key is not None:
        auth = ApiKeyAuth(resolved_key)
    else:
        # resolve_credentials returns exactly one non-None credential.
        assert resolved_token is not None  # ruff: ignore[assert]
        auth = AddonTokenAuth(resolved_token)
    return config, auth


class ClockifyClient:
    def __init__(
        self,
        api_key: str | ApiKeyProvider | None = None,
        *,
        addon_token: str | AddonTokenProvider | None = None,
        options: ClientOptions | None = None,
    ) -> None:
        self._config, auth = _build_config_and_auth(api_key, addon_token, options)
        event_hooks = (options or ClientOptions()).event_hooks
        self._transport = Transport(self._config, self._config.base_url, auth, event_hooks=event_hooks)
        self._reports_transport = Transport(self._config, self._config.reports_base_url, auth, event_hooks=event_hooks)
        self.user = UserResource(self._transport)
        self.workspaces = WorkspacesResource(self._transport)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._transport.close()
        self._reports_transport.close()

    def default_workspace(self) -> WorkspaceClient:
        user = self.user.me()
        if user.active_workspace is None:
            message = "Current user has no active workspace"
            raise ConfigurationError(message)
        return self.workspace(user.active_workspace)

    def workspace(self, workspace_id: WorkspaceId | str) -> WorkspaceClient:
        return WorkspaceClient(self._transport, WorkspaceId(str(workspace_id)), page_size=self._config.page_size)


class AsyncClockifyClient:
    # Async twin of ClockifyClient. The auth object is the same httpx.Auth: a credential
    # provider runs inside the event loop on every request, so it must not block.
    def __init__(
        self,
        api_key: str | ApiKeyProvider | None = None,
        *,
        addon_token: str | AddonTokenProvider | None = None,
        options: ClientOptions | None = None,
    ) -> None:
        self._config, auth = _build_config_and_auth(api_key, addon_token, options)
        event_hooks = (options or ClientOptions()).event_hooks
        self._transport = AsyncTransport(self._config, self._config.base_url, auth, event_hooks=event_hooks)
        self._reports_transport = AsyncTransport(
            self._config, self._config.reports_base_url, auth, event_hooks=event_hooks
        )
        self.user = AsyncUserResource(self._transport)
        self.workspaces = AsyncWorkspacesResource(self._transport)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._transport.aclose()
        await self._reports_transport.aclose()

    async def default_workspace(self) -> AsyncWorkspaceClient:
        user = await self.user.me()
        if user.active_workspace is None:
            message = "Current user has no active workspace"
            raise ConfigurationError(message)
        return self.workspace(user.active_workspace)

    def workspace(self, workspace_id: WorkspaceId | str) -> AsyncWorkspaceClient:
        return AsyncWorkspaceClient(self._transport, WorkspaceId(str(workspace_id)), page_size=self._config.page_size)
