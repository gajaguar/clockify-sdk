from __future__ import annotations

from typing import Final

import pytest
import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import ConfigurationError
from clockify.ids import WorkspaceId

BASE_URL: Final = "https://fake.clockify.test/api/v1"

USER_PAYLOAD: Final = {
    "id": "5b0f5b1f1f1f1f1f1f1f1f1f",
    "email": "someone@example.com",
    "name": "Some One",
    "activeWorkspace": "64a1f0000000000000000001",
    "defaultWorkspace": "64a1f0000000000000000002",
    "status": "ACTIVE",
}


def _client() -> ClockifyClient:
    return ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


def test_workspace_binds_without_any_request() -> None:
    # Arrange
    client = _client()
    # Act
    workspace = client.workspace("64a1f0000000000000000001")
    # Assert
    assert workspace.id == WorkspaceId("64a1f0000000000000000001")
    client.close()


@respx.mock
def test_default_workspace_binds_to_current_users_active_workspace() -> None:
    # Arrange
    respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json=USER_PAYLOAD))
    client = _client()
    # Act
    workspace = client.default_workspace()
    # Assert
    assert workspace.id == WorkspaceId("64a1f0000000000000000001")
    client.close()


@respx.mock
def test_default_workspace_raises_when_user_has_no_active_workspace() -> None:
    # Arrange
    payload = {**USER_PAYLOAD, "activeWorkspace": None}
    respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json=payload))
    client = _client()
    # Act
    # Assert
    with pytest.raises(ConfigurationError):
        client.default_workspace()
    client.close()
