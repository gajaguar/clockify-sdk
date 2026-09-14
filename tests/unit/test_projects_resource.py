from __future__ import annotations

from typing import Final

import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import CqsKind
from clockify import ProjectCreate
from clockify import ProjectUpdate
from clockify.ids import WorkspaceId

BASE_URL: Final = "https://fake.clockify.test/api/v1"
WORKSPACE_ID: Final = WorkspaceId("64a1f0000000000000000001")

PROJECT_PAYLOAD: Final = {
    "id": "5b0f5b1f1f1f1f1f1f1f1f1f",
    "name": "Apollo",
    "workspaceId": str(WORKSPACE_ID),
    "clientId": "5a0ab5acb07987125438b60f",
    "archived": False,
    "public": True,
    "billable": True,
}


def _client() -> ClockifyClient:
    return ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


@respx.mock
def test_list_returns_projects() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/projects").mock(
        return_value=Response(200, json=[PROJECT_PAYLOAD])
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    page = workspace.projects.list_page()
    # Assert
    assert route.call_count == 1
    assert [project.model_dump(by_alias=True, exclude_unset=True) for project in page.items] == [PROJECT_PAYLOAD]
    client.close()


@respx.mock
def test_get_returns_single_project() -> None:
    # Arrange
    project_id = PROJECT_PAYLOAD["id"]
    route = respx.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/projects/{project_id}").mock(
        return_value=Response(200, json=PROJECT_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    project = workspace.projects.get(project_id)
    # Assert
    assert route.call_count == 1
    assert project.name == "Apollo"
    client.close()


@respx.mock
def test_create_posts_name_and_declares_non_idempotent_command() -> None:
    # Arrange
    route = respx.post(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/projects").mock(
        return_value=Response(200, json=PROJECT_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    project = workspace.projects.create(ProjectCreate(name="Apollo"))
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert project.name == "Apollo"
    client.close()


@respx.mock
def test_update_puts_name_and_declares_idempotent_command() -> None:
    # Arrange
    project_id = PROJECT_PAYLOAD["id"]
    route = respx.put(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/projects/{project_id}").mock(
        return_value=Response(200, json=PROJECT_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    project = workspace.projects.update(project_id, ProjectUpdate(name="Apollo"))
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    assert project.id == project_id
    client.close()


@respx.mock
def test_delete_declares_idempotent_command() -> None:
    # Arrange
    project_id = PROJECT_PAYLOAD["id"]
    route = respx.delete(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/projects/{project_id}").mock(
        return_value=Response(204)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    workspace.projects.delete(project_id)
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    client.close()
