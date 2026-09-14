from __future__ import annotations

from typing import Final

import pytest
import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import CqsKind
from clockify import UserGroupCreate
from clockify import UserGroupUpdate
from clockify.ids import WorkspaceId

BASE_URL: Final = "https://fake.clockify.test/api/v1"
WORKSPACE_ID: Final = WorkspaceId("64a1f0000000000000000001")

USER_GROUP_PAYLOAD: Final = {
    "id": "76a687e29ae1f428e7ebe101",
    "name": "development_team",
    "workspaceId": str(WORKSPACE_ID),
    "userIds": ["5a0ab5acb07987125438b60f"],
}


def _client() -> ClockifyClient:
    return ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


@respx.mock
def test_list_returns_user_groups() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user-groups").mock(
        return_value=Response(200, json=[USER_GROUP_PAYLOAD])
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    page = workspace.user_groups.list_page()
    # Assert
    assert route.call_count == 1
    assert [group.model_dump(by_alias=True, exclude_unset=True) for group in page.items] == [USER_GROUP_PAYLOAD]
    client.close()


@respx.mock
def test_create_posts_name_and_declares_non_idempotent_command() -> None:
    # Arrange
    route = respx.post(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user-groups").mock(
        return_value=Response(200, json=USER_GROUP_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    group = workspace.user_groups.create(UserGroupCreate(name="development_team"))
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert group.name == "development_team"
    client.close()


@respx.mock
def test_update_puts_name_and_declares_idempotent_command() -> None:
    # Arrange
    group_id = USER_GROUP_PAYLOAD["id"]
    route = respx.put(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user-groups/{group_id}").mock(
        return_value=Response(200, json=USER_GROUP_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    group = workspace.user_groups.update(group_id, UserGroupUpdate(name="development_team"))
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    assert group.id == group_id
    client.close()


@respx.mock
def test_delete_declares_idempotent_command() -> None:
    # Arrange
    group_id = USER_GROUP_PAYLOAD["id"]
    route = respx.delete(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user-groups/{group_id}").mock(
        return_value=Response(204)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    workspace.user_groups.delete(group_id)
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    client.close()


def test_get_is_not_supported_by_the_clockify_api() -> None:
    # Arrange
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    # Assert
    with pytest.raises(NotImplementedError):
        workspace.user_groups.get("76a687e29ae1f428e7ebe101")
    client.close()
