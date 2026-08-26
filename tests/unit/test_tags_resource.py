from __future__ import annotations

from typing import Final

import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import CqsKind
from clockify import TagCreate
from clockify import TagUpdate
from clockify.ids import WorkspaceId

BASE_URL: Final = "https://fake.clockify.test/api/v1"
WORKSPACE_ID: Final = WorkspaceId("64a1f0000000000000000001")

TAG_PAYLOAD: Final = {
    "id": "5b0f5b1f1f1f1f1f1f1f1f1f",
    "name": "billable",
    "workspaceId": str(WORKSPACE_ID),
    "archived": False,
}


def _client() -> ClockifyClient:
    return ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


@respx.mock
def test_list_returns_tags() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/tags").mock(
        return_value=Response(200, json=[TAG_PAYLOAD])
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    page = workspace.tags.list_page()
    # Assert
    assert route.call_count == 1
    assert [tag.model_dump(by_alias=True, exclude_unset=True) for tag in page.items] == [TAG_PAYLOAD]
    client.close()


@respx.mock
def test_get_returns_single_tag() -> None:
    # Arrange
    tag_id = TAG_PAYLOAD["id"]
    route = respx.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/tags/{tag_id}").mock(
        return_value=Response(200, json=TAG_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    tag = workspace.tags.get(tag_id)
    # Assert
    assert route.call_count == 1
    assert tag.name == "billable"
    client.close()


@respx.mock
def test_create_posts_name_and_declares_non_idempotent_command() -> None:
    # Arrange
    route = respx.post(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/tags").mock(return_value=Response(200, json=TAG_PAYLOAD))
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    tag = workspace.tags.create(TagCreate(name="billable"))
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert tag.name == "billable"
    client.close()


@respx.mock
def test_update_puts_name_and_declares_idempotent_command() -> None:
    # Arrange
    tag_id = TAG_PAYLOAD["id"]
    route = respx.put(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/tags/{tag_id}").mock(
        return_value=Response(200, json=TAG_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    tag = workspace.tags.update(tag_id, TagUpdate(name="billable"))
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    assert tag.id == tag_id
    client.close()


@respx.mock
def test_delete_declares_idempotent_command() -> None:
    # Arrange
    tag_id = TAG_PAYLOAD["id"]
    route = respx.delete(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/tags/{tag_id}").mock(return_value=Response(204))
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    workspace.tags.delete(tag_id)
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    client.close()
