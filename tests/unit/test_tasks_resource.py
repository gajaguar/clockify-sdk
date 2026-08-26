from __future__ import annotations

from typing import Final

import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import CqsKind
from clockify import TaskCreate
from clockify import TaskUpdate
from clockify.ids import ProjectId
from clockify.ids import WorkspaceId

BASE_URL: Final = "https://fake.clockify.test/api/v1"
WORKSPACE_ID: Final = WorkspaceId("64a1f0000000000000000001")
PROJECT_ID: Final = ProjectId("5b0f5b1f1f1f1f1f1f1f1f1f")

TASK_PAYLOAD: Final = {
    "id": "5c0f5b1f1f1f1f1f1f1f1f1f",
    "name": "Build API",
    "projectId": str(PROJECT_ID),
    "status": "ACTIVE",
}


def _client() -> ClockifyClient:
    return ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


@respx.mock
def test_list_returns_tasks_for_project() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/projects/{PROJECT_ID}/tasks").mock(
        return_value=Response(200, json=[TASK_PAYLOAD])
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    page = workspace.tasks.list_page(PROJECT_ID)
    # Assert
    assert route.call_count == 1
    assert [task.model_dump(by_alias=True, exclude_unset=True) for task in page.items] == [TASK_PAYLOAD]
    client.close()


@respx.mock
def test_get_returns_single_task() -> None:
    # Arrange
    task_id = TASK_PAYLOAD["id"]
    route = respx.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/projects/{PROJECT_ID}/tasks/{task_id}").mock(
        return_value=Response(200, json=TASK_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    task = workspace.tasks.get(PROJECT_ID, task_id)
    # Assert
    assert route.call_count == 1
    assert task.name == "Build API"
    client.close()


@respx.mock
def test_create_posts_name_and_declares_non_idempotent_command() -> None:
    # Arrange
    route = respx.post(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/projects/{PROJECT_ID}/tasks").mock(
        return_value=Response(200, json=TASK_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    task = workspace.tasks.create(PROJECT_ID, TaskCreate(name="Build API"))
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert task.name == "Build API"
    client.close()


@respx.mock
def test_update_puts_name_and_declares_idempotent_command() -> None:
    # Arrange
    task_id = TASK_PAYLOAD["id"]
    route = respx.put(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/projects/{PROJECT_ID}/tasks/{task_id}").mock(
        return_value=Response(200, json=TASK_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    task = workspace.tasks.update(PROJECT_ID, task_id, TaskUpdate(name="Build API"))
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    assert task.id == task_id
    client.close()


@respx.mock
def test_delete_declares_idempotent_command() -> None:
    # Arrange
    task_id = TASK_PAYLOAD["id"]
    route = respx.delete(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/projects/{PROJECT_ID}/tasks/{task_id}").mock(
        return_value=Response(204)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    workspace.tasks.delete(PROJECT_ID, task_id)
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    client.close()
