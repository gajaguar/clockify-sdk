from __future__ import annotations

from typing import Final

import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import ClientCreate
from clockify import ClientOptions
from clockify import ClientUpdate
from clockify import ClockifyClient
from clockify import CqsKind
from clockify.ids import WorkspaceId

BASE_URL: Final = "https://fake.clockify.test/api/v1"
WORKSPACE_ID: Final = WorkspaceId("64a1f0000000000000000001")

CLIENT_PAYLOAD: Final = {
    "id": "5b0f5b1f1f1f1f1f1f1f1f1f",
    "name": "Acme Corp",
    "workspaceId": str(WORKSPACE_ID),
    "email": "billing@acme.test",
    "archived": False,
}


def _client() -> ClockifyClient:
    return ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


@respx.mock
def test_list_returns_clients() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/clients").mock(
        return_value=Response(200, json=[CLIENT_PAYLOAD])
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    page = workspace.clients.list_page()
    # Assert
    assert route.call_count == 1
    assert [entry.model_dump(by_alias=True, exclude_unset=True) for entry in page.items] == [CLIENT_PAYLOAD]
    client.close()


@respx.mock
def test_get_returns_single_client() -> None:
    # Arrange
    client_id = CLIENT_PAYLOAD["id"]
    route = respx.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/clients/{client_id}").mock(
        return_value=Response(200, json=CLIENT_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    entry = workspace.clients.get(client_id)
    # Assert
    assert route.call_count == 1
    assert entry.name == "Acme Corp"
    client.close()


@respx.mock
def test_create_posts_name_and_declares_non_idempotent_command() -> None:
    # Arrange
    route = respx.post(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/clients").mock(
        return_value=Response(200, json=CLIENT_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    entry = workspace.clients.create(ClientCreate(name="Acme Corp"))
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert entry.name == "Acme Corp"
    client.close()


@respx.mock
def test_update_puts_name_and_declares_idempotent_command() -> None:
    # Arrange
    client_id = CLIENT_PAYLOAD["id"]
    route = respx.put(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/clients/{client_id}").mock(
        return_value=Response(200, json=CLIENT_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    entry = workspace.clients.update(client_id, ClientUpdate(name="Acme Corp"))
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    assert entry.id == client_id
    client.close()


@respx.mock
def test_delete_declares_idempotent_command() -> None:
    # Arrange
    client_id = CLIENT_PAYLOAD["id"]
    route = respx.delete(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/clients/{client_id}").mock(return_value=Response(204))
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    workspace.clients.delete(client_id)
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    client.close()
