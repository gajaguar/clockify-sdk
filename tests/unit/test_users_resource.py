from __future__ import annotations

from typing import Final

import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify._transport import Transport  # ruff: ignore[import-private-name]
from clockify.config import ClientConfig
from clockify.ids import WorkspaceId
from clockify.resources.users import UsersResource

BASE_URL: Final = "https://fake.clockify.test/api/v1"
WORKSPACE_ID: Final = WorkspaceId("64a1f0000000000000000001")

USER_PAYLOAD: Final = {
    "id": "5b0f5b1f1f1f1f1f1f1f1f1f",
    "email": "someone@example.com",
    "name": "Some One",
    "status": "ACTIVE",
}


def _client() -> ClockifyClient:
    return ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


@respx.mock
def test_list_page_returns_workspace_users() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/users").mock(
        return_value=Response(200, json=[USER_PAYLOAD])
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    page = workspace.users.list_page()
    # Assert
    assert route.call_count == 1
    assert dict(respx.calls[0].request.url.params) == {"page": "1", "page-size": "200"}
    assert [user.model_dump(by_alias=True, exclude_unset=True) for user in page.items] == [USER_PAYLOAD]
    client.close()


@respx.mock
def test_list_auto_paginates_across_pages() -> None:
    # Arrange
    second_user = {**USER_PAYLOAD, "id": "5b0f5b1f1f1f1f1f1f1f1f20"}
    respx.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/users").mock(
        side_effect=[
            Response(200, json=[USER_PAYLOAD, USER_PAYLOAD]),
            Response(200, json=[second_user]),
        ]
    )
    config = ClientConfig(api_key="dummy", base_url=BASE_URL, reports_base_url=BASE_URL, retry=NO_RETRY)
    transport = Transport(config, BASE_URL)
    resource = UsersResource(transport, WORKSPACE_ID, page_size=2)
    # Act
    users = list(resource.list())
    # Assert
    assert len(users) == 3
    transport.close()
