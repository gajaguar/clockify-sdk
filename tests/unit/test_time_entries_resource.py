from __future__ import annotations

from typing import Final

import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import CqsKind
from clockify import TimeEntryCreate
from clockify import TimeEntryFilter
from clockify import TimeEntryUpdate
from clockify.ids import ProjectId
from clockify.ids import TagId
from clockify.ids import UserId
from clockify.ids import WorkspaceId

BASE_URL: Final = "https://fake.clockify.test/api/v1"
WORKSPACE_ID: Final = WorkspaceId("64a1f0000000000000000001")
USER_ID: Final = UserId("5a0f5b1f1f1f1f1f1f1f1f1f")
PROJECT_ID: Final = ProjectId("5b0f5b1f1f1f1f1f1f1f1f1f")

TIME_ENTRY_PAYLOAD: Final = {
    "id": "5c0f5b1f1f1f1f1f1f1f1f1f",
    "workspaceId": str(WORKSPACE_ID),
    "userId": str(USER_ID),
    "description": "Build API",
    "projectId": str(PROJECT_ID),
    "billable": True,
    "timeInterval": {
        "start": "2026-08-26T10:00:00Z",
        "end": "2026-08-26T11:30:00Z",
        "duration": "PT1H30M",
    },
    "type": "REGULAR",
    "isLocked": False,
}


def _client() -> ClockifyClient:
    return ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


@respx.mock
def test_list_page_returns_time_entries_for_user() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries").mock(
        return_value=Response(200, json=[TIME_ENTRY_PAYLOAD])
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    page = workspace.time_entries.list_page(USER_ID)
    # Assert
    assert route.call_count == 1
    dumped = [entry.model_dump(mode="json", by_alias=True, exclude_unset=True) for entry in page.items]
    assert dumped == [TIME_ENTRY_PAYLOAD]
    client.close()


@respx.mock
def test_list_wires_through_paginate_and_yields_page_items() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries").mock(
        return_value=Response(200, json=[TIME_ENTRY_PAYLOAD])
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    entries = list(workspace.time_entries.list(USER_ID))
    # Assert
    assert route.call_count == 1
    assert [entry.id for entry in entries] == [TIME_ENTRY_PAYLOAD["id"]]
    client.close()


@respx.mock
def test_list_page_renders_filter_as_kebab_case_query_params() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries").mock(
        return_value=Response(200, json=[])
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    entry_filter = TimeEntryFilter(
        project=PROJECT_ID,
        project_required=True,
        in_progress=False,
        tag_ids=[TagId("t1"), TagId("t2")],
    )
    # Act
    workspace.time_entries.list_page(USER_ID, entry_filter=entry_filter)
    # Assert
    sent = route.calls[0].request.url.params
    assert sent.get("project") == str(PROJECT_ID)
    assert sent.get("project-required") == "true"
    assert sent.get("in-progress") == "false"
    assert sent.get_list("tags") == ["t1", "t2"]
    client.close()


@respx.mock
def test_get_returns_single_time_entry() -> None:
    # Arrange
    entry_id = TIME_ENTRY_PAYLOAD["id"]
    route = respx.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/time-entries/{entry_id}").mock(
        return_value=Response(200, json=TIME_ENTRY_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    entry = workspace.time_entries.get(entry_id)
    # Assert
    assert route.call_count == 1
    assert entry.description == "Build API"
    client.close()


@respx.mock
def test_create_posts_to_collection_and_declares_non_idempotent_command() -> None:
    # Arrange
    route = respx.post(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/time-entries").mock(
        return_value=Response(200, json=TIME_ENTRY_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    entry = workspace.time_entries.create(TimeEntryCreate(start="2026-08-26T10:00:00Z"))
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert entry.model_dump(mode="json", by_alias=True, exclude_unset=True) == TIME_ENTRY_PAYLOAD
    client.close()


@respx.mock
def test_start_posts_to_user_path_and_declares_non_idempotent_command() -> None:
    # Arrange
    route = respx.post(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries").mock(
        return_value=Response(200, json=TIME_ENTRY_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    entry = workspace.time_entries.start(USER_ID, TimeEntryCreate(start="2026-08-26T10:00:00Z"))
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert entry.user_id == USER_ID
    client.close()


@respx.mock
def test_update_puts_to_item_path_and_declares_idempotent_command() -> None:
    # Arrange
    entry_id = TIME_ENTRY_PAYLOAD["id"]
    route = respx.put(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/time-entries/{entry_id}").mock(
        return_value=Response(200, json=TIME_ENTRY_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    entry = workspace.time_entries.update(entry_id, TimeEntryUpdate(start="2026-08-26T10:00:00Z"))
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    assert entry.id == entry_id
    client.close()


@respx.mock
def test_delete_declares_idempotent_command() -> None:
    # Arrange
    entry_id = TIME_ENTRY_PAYLOAD["id"]
    route = respx.delete(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/time-entries/{entry_id}").mock(
        return_value=Response(204)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    workspace.time_entries.delete(entry_id)
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    client.close()


@respx.mock
def test_stop_patches_user_path_with_end_and_declares_non_idempotent_command() -> None:
    # Arrange
    stopped_payload = dict(TIME_ENTRY_PAYLOAD)
    route = respx.patch(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries").mock(
        return_value=Response(200, json=stopped_payload)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    entry = workspace.time_entries.stop(USER_ID)
    # Assert
    assert route.call_count == 1
    sent_body = respx.calls[0].request.content
    assert b'"end"' in sent_body
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert entry.model_dump(mode="json", by_alias=True, exclude_unset=True) == stopped_payload
    client.close()
