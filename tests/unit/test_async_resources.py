from __future__ import annotations

from typing import Final

import pytest
import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import AsyncClockifyClient
from clockify import ClientCreate
from clockify import ClientOptions
from clockify import ClientUpdate
from clockify import CustomFieldCreate
from clockify import CustomFieldType
from clockify import CustomFieldUpdate
from clockify import ProjectCreate
from clockify import ProjectUpdate
from clockify import TagCreate
from clockify import TagUpdate
from clockify import TaskCreate
from clockify import TaskUpdate
from clockify import TimeEntryCreate
from clockify import TimeEntryFilter
from clockify import TimeEntryUpdate
from clockify import UserGroupCreate
from clockify import UserGroupUpdate
from clockify.ids import ProjectId
from clockify.ids import UserId
from clockify.ids import WorkspaceId

BASE_URL: Final = "https://fake.clockify.test/api/v1"
WORKSPACE_ID: Final = WorkspaceId("64a1f0000000000000000001")
USER_ID: Final = UserId("5a0f5b1f1f1f1f1f1f1f1f1f")
PROJECT_ID: Final = ProjectId("5b0f5b1f1f1f1f1f1f1f1f1f")
ITEM_ID: Final = "5c0f5b1f1f1f1f1f1f1f1f1f"
WS: Final = f"{BASE_URL}/workspaces/{WORKSPACE_ID}"

NAMED: Final = {"id": ITEM_ID, "name": "thing", "workspaceId": str(WORKSPACE_ID)}
TASK: Final = {"id": ITEM_ID, "name": "thing", "projectId": str(PROJECT_ID), "status": "ACTIVE"}
CUSTOM_FIELD: Final = {**NAMED, "type": "TXT", "entityType": "TIMEENTRY", "status": "VISIBLE"}
USER_PAYLOAD: Final = {"id": ITEM_ID, "email": "a@b.test", "name": "n", "status": "ACTIVE"}
TIME_ENTRY: Final = {
    "id": ITEM_ID,
    "workspaceId": str(WORKSPACE_ID),
    "userId": str(USER_ID),
    "description": "Build API",
    "timeInterval": {"start": "2026-08-26T10:00:00Z", "end": "2026-08-26T11:30:00Z", "duration": "PT1H30M"},
    "type": "REGULAR",
}
START: Final = "2026-08-26T10:00:00Z"

# (attribute, path, payload, create model, update model)
SIMPLE: Final = [
    ("clients", "clients", NAMED, ClientCreate(name="thing"), ClientUpdate(name="thing")),
    ("projects", "projects", NAMED, ProjectCreate(name="thing"), ProjectUpdate(name="thing")),
    ("tags", "tags", NAMED, TagCreate(name="thing"), TagUpdate(name="thing")),
    ("user_groups", "user-groups", NAMED, UserGroupCreate(name="thing"), UserGroupUpdate(name="thing")),
    (
        "custom_fields",
        "custom-fields",
        CUSTOM_FIELD,
        CustomFieldCreate(name="thing", type=CustomFieldType.TXT),
        CustomFieldUpdate(name="thing"),
    ),
]
NO_GET: Final = frozenset({"user_groups", "custom_fields"})


def _client() -> AsyncClockifyClient:
    return AsyncClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


@pytest.mark.parametrize(("attr", "path", "payload", "unused_create", "unused_update"), SIMPLE)
@respx.mock
async def test_simple_resource_list_page_and_list(attr, path, payload, unused_create, unused_update) -> None:
    del unused_create, unused_update
    # Arrange
    route = respx.get(f"{WS}/{path}").mock(return_value=Response(200, json=[payload]))
    client = _client()
    resource = getattr(client.workspace(WORKSPACE_ID), attr)
    # Act
    page = await resource.list_page()
    items = [item async for item in resource.list()]
    # Assert
    assert [item.id for item in page.items] == [ITEM_ID]
    assert [item.id for item in items] == [ITEM_ID]
    assert route.calls[0].request.url.params["page-size"] == "200"
    await client.aclose()


@pytest.mark.parametrize(("attr", "path", "payload", "create", "unused_update"), SIMPLE)
@respx.mock
async def test_simple_resource_create_posts_body(attr, path, payload, create, unused_update) -> None:
    del unused_update
    # Arrange
    route = respx.post(f"{WS}/{path}").mock(return_value=Response(200, json=payload))
    client = _client()
    resource = getattr(client.workspace(WORKSPACE_ID), attr)
    # Act
    created = await resource.create(create)
    # Assert
    assert created.id == ITEM_ID
    assert route.calls[0].request.content.startswith(b'{"name":"thing"')
    await client.aclose()


@pytest.mark.parametrize(("attr", "path", "payload", "unused_create", "update"), SIMPLE)
@respx.mock
async def test_simple_resource_update_puts_and_delete_removes(attr, path, payload, unused_create, update) -> None:
    del unused_create
    # Arrange
    put = respx.put(f"{WS}/{path}/{ITEM_ID}").mock(return_value=Response(200, json=payload))
    delete = respx.delete(f"{WS}/{path}/{ITEM_ID}").mock(return_value=Response(204))
    client = _client()
    resource = getattr(client.workspace(WORKSPACE_ID), attr)
    # Act
    updated = await resource.update(ITEM_ID, update)
    result = await resource.delete(ITEM_ID)
    # Assert
    assert updated.id == ITEM_ID
    assert result is None
    assert put.call_count == 1
    assert delete.call_count == 1
    await client.aclose()


@pytest.mark.parametrize(
    ("attr", "path", "payload", "unused_create", "unused_update"), [s for s in SIMPLE if s[0] not in NO_GET]
)
@respx.mock
async def test_simple_resource_get_returns_one(attr, path, payload, unused_create, unused_update) -> None:
    del unused_create, unused_update
    # Arrange
    route = respx.get(f"{WS}/{path}/{ITEM_ID}").mock(return_value=Response(200, json=payload))
    client = _client()
    resource = getattr(client.workspace(WORKSPACE_ID), attr)
    # Act
    item = await resource.get(ITEM_ID)
    # Assert
    assert item.id == ITEM_ID
    assert route.call_count == 1
    await client.aclose()


@pytest.mark.parametrize("attr", sorted(NO_GET))
async def test_get_is_not_supported_where_clockify_has_no_endpoint(attr) -> None:
    # Arrange
    client = _client()
    resource = getattr(client.workspace(WORKSPACE_ID), attr)
    # Act
    # Assert
    with pytest.raises(NotImplementedError, match="filter list"):
        await resource.get(ITEM_ID)
    await client.aclose()


@respx.mock
async def test_users_list_page_and_list() -> None:
    # Arrange
    route = respx.get(f"{WS}/users").mock(return_value=Response(200, json=[USER_PAYLOAD]))
    client = _client()
    users = client.workspace(WORKSPACE_ID).users
    # Act
    page = await users.list_page()
    listed = [u async for u in users.list()]
    # Assert
    assert [u.id for u in page.items] == [ITEM_ID]
    assert [u.id for u in listed] == [ITEM_ID]
    assert route.call_count == 2
    await client.aclose()


@respx.mock
async def test_tasks_crud_uses_project_scoped_paths() -> None:
    # Arrange
    base = f"{WS}/projects/{PROJECT_ID}/tasks"
    listing = respx.get(base).mock(return_value=Response(200, json=[TASK]))
    post = respx.post(base).mock(return_value=Response(200, json=TASK))
    get = respx.get(f"{base}/{ITEM_ID}").mock(return_value=Response(200, json=TASK))
    put = respx.put(f"{base}/{ITEM_ID}").mock(return_value=Response(200, json=TASK))
    delete = respx.delete(f"{base}/{ITEM_ID}").mock(return_value=Response(204))
    client = _client()
    tasks = client.workspace(WORKSPACE_ID).tasks
    # Act
    page = await tasks.list_page(PROJECT_ID)
    listed = [t async for t in tasks.list(PROJECT_ID)]
    created = await tasks.create(PROJECT_ID, TaskCreate(name="thing"))
    fetched = await tasks.get(PROJECT_ID, ITEM_ID)
    updated = await tasks.update(PROJECT_ID, ITEM_ID, TaskUpdate(name="thing"))
    deleted = await tasks.delete(PROJECT_ID, ITEM_ID)
    # Assert
    assert [t.id for t in page.items] == [ITEM_ID]
    assert [t.id for t in listed] == [ITEM_ID]
    assert {created.id, fetched.id, updated.id} == {ITEM_ID}
    assert deleted is None
    assert listing.call_count == 2
    assert all(route.call_count == 1 for route in (post, get, put, delete))
    await client.aclose()


@respx.mock
async def test_time_entries_user_scoped_paths() -> None:
    # Arrange
    user_path = f"{WS}/user/{USER_ID}/time-entries"
    listing = respx.get(user_path).mock(return_value=Response(200, json=[TIME_ENTRY]))
    start = respx.post(user_path).mock(return_value=Response(200, json=TIME_ENTRY))
    stop = respx.patch(user_path).mock(return_value=Response(200, json=TIME_ENTRY))
    client = _client()
    entries = client.workspace(WORKSPACE_ID).time_entries
    # Act
    page = await entries.list_page(USER_ID, entry_filter=TimeEntryFilter(in_progress=False))
    listed = [e async for e in entries.list(USER_ID)]
    started = await entries.start(USER_ID, TimeEntryCreate(start=START))
    stopped = await entries.stop(USER_ID)
    # Assert
    assert [e.id for e in page.items] == [ITEM_ID]
    assert [e.id for e in listed] == [ITEM_ID]
    assert {started.id, stopped.id} == {ITEM_ID}
    assert listing.calls[0].request.url.params["in-progress"] == "false"
    assert b'"end"' in stop.calls[0].request.content
    assert start.call_count == 1
    await client.aclose()


@respx.mock
async def test_time_entries_direct_paths() -> None:
    # Arrange
    direct = f"{WS}/time-entries"
    create = respx.post(direct).mock(return_value=Response(200, json=TIME_ENTRY))
    get = respx.get(f"{direct}/{ITEM_ID}").mock(return_value=Response(200, json=TIME_ENTRY))
    put = respx.put(f"{direct}/{ITEM_ID}").mock(return_value=Response(200, json=TIME_ENTRY))
    delete = respx.delete(f"{direct}/{ITEM_ID}").mock(return_value=Response(204))
    client = _client()
    entries = client.workspace(WORKSPACE_ID).time_entries
    # Act
    created = await entries.create(TimeEntryCreate(start=START))
    fetched = await entries.get(ITEM_ID)
    updated = await entries.update(ITEM_ID, TimeEntryUpdate(start=START))
    deleted = await entries.delete(ITEM_ID)
    # Assert
    assert {created.id, fetched.id, updated.id} == {ITEM_ID}
    assert deleted is None
    assert all(route.call_count == 1 for route in (create, get, put, delete))
    await client.aclose()
