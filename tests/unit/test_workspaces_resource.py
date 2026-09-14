from __future__ import annotations

from typing import Final

import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import CqsKind
from clockify.ids import WorkspaceId

BASE_URL: Final = "https://fake.clockify.test/api/v1"

WORKSPACE_PAYLOAD: Final = {
    "id": "64a1f0000000000000000001",
    "name": "Cool Company",
    "imageUrl": "https://www.url.com/image.jpg",
}


def _client() -> ClockifyClient:
    return ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


@respx.mock
def test_list_returns_all_workspaces() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/workspaces").mock(return_value=Response(200, json=[WORKSPACE_PAYLOAD]))
    client = _client()
    # Act
    workspaces = client.workspaces.list()
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.url.path == "/api/v1/workspaces"
    assert [workspace.model_dump(by_alias=True, exclude_unset=True) for workspace in workspaces] == [WORKSPACE_PAYLOAD]
    client.close()


@respx.mock
def test_list_declares_query_cqs_kind() -> None:
    # Arrange
    respx.get(f"{BASE_URL}/workspaces").mock(return_value=Response(200, json=[WORKSPACE_PAYLOAD]))
    client = _client()
    # Act
    client.workspaces.list()
    # Assert
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    client.close()


@respx.mock
def test_get_returns_single_workspace() -> None:
    # Arrange
    workspace_id = WorkspaceId("64a1f0000000000000000001")
    route = respx.get(f"{BASE_URL}/workspaces/{workspace_id}").mock(return_value=Response(200, json=WORKSPACE_PAYLOAD))
    client = _client()
    # Act
    workspace = client.workspaces.get(workspace_id)
    # Assert
    assert route.call_count == 1
    assert workspace.name == "Cool Company"
    client.close()
