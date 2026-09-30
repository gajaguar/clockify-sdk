from __future__ import annotations

from typing import Final

import pytest
import respx
from httpx import Response

from clockify import AsyncClockifyClient
from clockify import AsyncWorkspaceClient
from clockify import ClientOptions
from clockify import ConfigurationError
from clockify import MissingCredentialsError
from clockify.retry import NO_RETRY

BASE_URL: Final = "https://fake.test/api/v1"
USER: Final = {"id": "u1", "email": "a@b.test", "name": "n", "status": "ACTIVE", "activeWorkspace": "w1"}


def _options() -> ClientOptions:
    return ClientOptions(base_url=BASE_URL, retry=NO_RETRY)


@respx.mock
async def test_api_key_argument_is_sent_as_the_api_key_header(monkeypatch) -> None:
    # Arrange
    monkeypatch.delenv("CLOCKIFY_ADDON_TOKEN", raising=False)
    route = respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json=USER))
    # Act
    async with AsyncClockifyClient(api_key="key", options=_options()) as client:
        user = await client.user.me()
    # Assert
    assert user.id == "u1"
    assert route.calls[0].request.headers["X-Api-Key"] == "key"


@respx.mock
async def test_addon_token_is_sent_as_the_addon_token_header(monkeypatch) -> None:
    # Arrange
    monkeypatch.delenv("CLOCKIFY_API_KEY", raising=False)
    route = respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json=USER))
    # Act
    async with AsyncClockifyClient(addon_token="tok", options=_options()) as client:
        await client.user.me()
    # Assert
    headers = route.calls[0].request.headers
    assert headers["X-Addon-Token"] == "tok"
    assert "X-Api-Key" not in headers


@respx.mock
async def test_provider_is_invoked_on_every_request() -> None:
    # Arrange
    calls: list[int] = []
    provider = lambda: calls.append(1) or "key"  # ruff: ignore[lambda-assignment]
    respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json=USER))
    client = AsyncClockifyClient(api_key=provider, options=_options())
    calls_before = len(calls)
    # Act
    await client.user.me()
    await client.user.me()
    # Assert
    assert calls_before == 0
    assert len(calls) == 2
    await client.aclose()


def test_missing_credentials_raise_at_construction(monkeypatch) -> None:
    # Arrange
    monkeypatch.delenv("CLOCKIFY_API_KEY", raising=False)
    monkeypatch.delenv("CLOCKIFY_ADDON_TOKEN", raising=False)
    # Act
    # Assert
    with pytest.raises(MissingCredentialsError):
        AsyncClockifyClient()


def test_both_credentials_are_rejected() -> None:
    # Arrange
    # Act
    # Assert
    with pytest.raises(ConfigurationError):
        AsyncClockifyClient(api_key="k", addon_token="t")


@respx.mock
async def test_default_workspace_uses_the_active_workspace() -> None:
    # Arrange
    respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json=USER))
    client = AsyncClockifyClient(api_key="key", options=_options())
    # Act
    workspace = await client.default_workspace()
    # Assert
    assert isinstance(workspace, AsyncWorkspaceClient)
    assert workspace.id == "w1"
    await client.aclose()


@respx.mock
async def test_default_workspace_without_active_workspace_raises() -> None:
    # Arrange
    respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json={**USER, "activeWorkspace": None}))
    client = AsyncClockifyClient(api_key="key", options=_options())
    # Act
    # Assert
    with pytest.raises(ConfigurationError):
        await client.default_workspace()
    await client.aclose()


@respx.mock
async def test_workspaces_list_returns_workspaces() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/workspaces").mock(return_value=Response(200, json=[{"id": "w1", "name": "W"}]))
    respx.get(f"{BASE_URL}/workspaces/w1").mock(return_value=Response(200, json={"id": "w1", "name": "W"}))
    client = AsyncClockifyClient(api_key="key", options=_options())
    # Act
    listed = await client.workspaces.list()
    fetched = await client.workspaces.get("w1")
    # Assert
    assert route.call_count == 1
    assert [w.id for w in listed] == ["w1"]
    assert fetched.name == "W"
    await client.aclose()
