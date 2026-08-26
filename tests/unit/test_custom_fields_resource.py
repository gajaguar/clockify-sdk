from __future__ import annotations

from typing import Final

import pytest
import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import CqsKind
from clockify import CustomFieldCreate
from clockify import CustomFieldType
from clockify import CustomFieldUpdate
from clockify.ids import WorkspaceId

BASE_URL: Final = "https://fake.clockify.test/api/v1"
WORKSPACE_ID: Final = WorkspaceId("64a1f0000000000000000001")

CUSTOM_FIELD_PAYLOAD: Final = {
    "id": "5b0f5b1f1f1f1f1f1f1f1f1f",
    "name": "PO Number",
    "type": "TXT",
    "entityType": "TIMEENTRY",
    "status": "VISIBLE",
    "workspaceId": str(WORKSPACE_ID),
    "required": False,
    "onlyAdminCanEdit": False,
}


def _client() -> ClockifyClient:
    return ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


@respx.mock
def test_list_returns_custom_fields() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/custom-fields").mock(
        return_value=Response(200, json=[CUSTOM_FIELD_PAYLOAD])
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    page = workspace.custom_fields.list_page()
    # Assert
    assert route.call_count == 1
    assert [field.model_dump(by_alias=True, exclude_unset=True) for field in page.items] == [CUSTOM_FIELD_PAYLOAD]
    client.close()


@respx.mock
def test_create_posts_name_and_type_and_declares_non_idempotent_command() -> None:
    # Arrange
    route = respx.post(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/custom-fields").mock(
        return_value=Response(200, json=CUSTOM_FIELD_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    field = workspace.custom_fields.create(CustomFieldCreate(name="PO Number", type=CustomFieldType.TXT))
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert field.name == "PO Number"
    client.close()


@respx.mock
def test_update_puts_name_and_declares_idempotent_command() -> None:
    # Arrange
    field_id = CUSTOM_FIELD_PAYLOAD["id"]
    route = respx.put(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/custom-fields/{field_id}").mock(
        return_value=Response(200, json=CUSTOM_FIELD_PAYLOAD)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    field = workspace.custom_fields.update(field_id, CustomFieldUpdate(name="PO Number"))
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    assert field.id == field_id
    client.close()


@respx.mock
def test_delete_declares_idempotent_command() -> None:
    # Arrange
    field_id = CUSTOM_FIELD_PAYLOAD["id"]
    route = respx.delete(f"{BASE_URL}/workspaces/{WORKSPACE_ID}/custom-fields/{field_id}").mock(
        return_value=Response(204)
    )
    client = _client()
    workspace = client.workspace(WORKSPACE_ID)
    # Act
    workspace.custom_fields.delete(field_id)
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
        workspace.custom_fields.get("5b0f5b1f1f1f1f1f1f1f1f1f")
    client.close()
