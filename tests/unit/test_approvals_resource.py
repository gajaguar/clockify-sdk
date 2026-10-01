from __future__ import annotations

import datetime
import json
from typing import Final

import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import ApprovalRequestCreate
from clockify import ApprovalRequestFilter
from clockify import ApprovalRequestResubmit
from clockify import ApprovalRequestType
from clockify import ApprovalRequestUpdate
from clockify import ApprovalSortColumn
from clockify import ApprovalSortOrder
from clockify import ApprovalState
from clockify import AsyncClockifyClient
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import CqsKind
from clockify._auth import ApiKeyAuth  # ruff: ignore[import-private-name]
from clockify._transport import AsyncTransport  # ruff: ignore[import-private-name]
from clockify._transport import Transport  # ruff: ignore[import-private-name]
from clockify.config import ClientConfig
from clockify.ids import WorkspaceId
from clockify.resources.approvals import ApprovalsResource
from clockify.resources.approvals import AsyncApprovalsResource

BASE_URL: Final = "https://fake.clockify.test/api/v1"
WORKSPACE_ID: Final = WorkspaceId("64a1f0000000000000000001")
APPROVALS_URL: Final = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/approval-requests"
APPROVAL_ID: Final = "6a0000000000000000000001"
USER_ID: Final = "5a0ab5acb07987125438b60f"

REQUEST_PAYLOAD: Final = {
    "id": APPROVAL_ID,
    "workspaceId": str(WORKSPACE_ID),
    "type": "TIMESHEET",
    "status": {"state": "PENDING"},
}
DETAILS_PAYLOAD: Final = {"approvalRequest": REQUEST_PAYLOAD, "trackedTime": "PT8H"}
PERIOD_START: Final = datetime.datetime(2026, 9, 28, tzinfo=datetime.UTC)
CREATE: Final = ApprovalRequestCreate(period_start=PERIOD_START)
CREATE_BODY: Final = {"periodStart": "2026-09-28T00:00:00Z"}
RESUBMIT: Final = ApprovalRequestResubmit(period_start=PERIOD_START, type=ApprovalRequestType.TIMESHEET)
UPDATE: Final = ApprovalRequestUpdate(state=ApprovalState.APPROVED, note="ok")


def _client() -> ClockifyClient:
    return ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


def _async_client() -> AsyncClockifyClient:
    return AsyncClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


@respx.mock
def test_list_page_sends_page_params_and_declares_query() -> None:
    # Arrange
    route = respx.get(APPROVALS_URL).mock(return_value=Response(200, json=[DETAILS_PAYLOAD]))
    client = _client()
    # Act
    page = client.workspace(WORKSPACE_ID).approvals.list_page(page_size=10)
    # Assert
    assert dict(route.calls[0].request.url.params) == {"page": "1", "page-size": "10"}
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    assert page.items[0].approval_request is not None
    assert page.items[0].approval_request.id == APPROVAL_ID
    client.close()


@respx.mock
def test_list_page_sends_the_filter() -> None:
    # Arrange
    route = respx.get(APPROVALS_URL).mock(return_value=Response(200, json=[]))
    client = _client()
    request_filter = ApprovalRequestFilter(
        status=ApprovalState.PENDING,
        sort_column=ApprovalSortColumn.START,
        sort_order=ApprovalSortOrder.ASCENDING,
        types=[ApprovalRequestType.TIMESHEET, ApprovalRequestType.EXPENSE],
    )
    # Act
    client.workspace(WORKSPACE_ID).approvals.list_page(request_filter=request_filter, page=2, page_size=50)
    # Assert
    assert route.calls[0].request.url.params.multi_items() == [
        ("status", "PENDING"),
        ("sort-column", "START"),
        ("sort-order", "ASCENDING"),
        ("types", "TIMESHEET"),
        ("types", "EXPENSE"),
        ("page", "2"),
        ("page-size", "50"),
    ]
    client.close()


@respx.mock
def test_list_auto_paginates_across_pages() -> None:
    # Arrange
    route = respx.get(APPROVALS_URL).mock(
        side_effect=[Response(200, json=[DETAILS_PAYLOAD, DETAILS_PAYLOAD]), Response(200, json=[DETAILS_PAYLOAD])]
    )
    config = ClientConfig(api_key="dummy", base_url=BASE_URL, reports_base_url=BASE_URL, retry=NO_RETRY)
    transport = Transport(config, BASE_URL, ApiKeyAuth("dummy"))
    resource = ApprovalsResource(transport, WORKSPACE_ID, page_size=2)
    # Act
    items = list(resource.list())
    # Assert
    assert len(items) == 3
    assert [call.request.url.params["page"] for call in route.calls] == ["1", "2"]
    transport.close()


@respx.mock
def test_submit_posts_to_the_type_path() -> None:
    # Arrange
    route = respx.post(f"{APPROVALS_URL}/TIMESHEET").mock(return_value=Response(201, json=REQUEST_PAYLOAD))
    client = _client()
    # Act
    request = client.workspace(WORKSPACE_ID).approvals.submit(ApprovalRequestType.TIMESHEET, CREATE)
    # Assert
    assert route.call_count == 1
    assert not route.calls[0].request.url.params
    assert json.loads(route.calls[0].request.content) == CREATE_BODY
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert request.id == APPROVAL_ID
    client.close()


@respx.mock
def test_submit_sends_time_view_mode() -> None:
    # Arrange
    route = respx.post(f"{APPROVALS_URL}/EXPENSE").mock(return_value=Response(201, json=REQUEST_PAYLOAD))
    client = _client()
    # Act
    client.workspace(WORKSPACE_ID).approvals.submit(ApprovalRequestType.EXPENSE, CREATE, time_view_mode="DECIMAL")
    # Assert
    assert dict(route.calls[0].request.url.params) == {"timeViewMode": "DECIMAL"}
    client.close()


@respx.mock
def test_submit_for_user_posts_to_the_user_type_path() -> None:
    # Arrange
    route = respx.post(f"{APPROVALS_URL}/users/{USER_ID}/TIMESHEET_AND_EXPENSE").mock(
        return_value=Response(201, json=REQUEST_PAYLOAD)
    )
    client = _client()
    # Act
    request = client.workspace(WORKSPACE_ID).approvals.submit_for_user(
        USER_ID, ApprovalRequestType.TIMESHEET_AND_EXPENSE, CREATE, time_view_mode="FULL"
    )
    # Assert
    assert dict(route.calls[0].request.url.params) == {"timeViewMode": "FULL"}
    assert json.loads(route.calls[0].request.content) == CREATE_BODY
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert request.id == APPROVAL_ID
    client.close()


@respx.mock
def test_update_patches_and_declares_idempotent_command() -> None:
    # Arrange
    route = respx.patch(f"{APPROVALS_URL}/{APPROVAL_ID}").mock(return_value=Response(200, json=REQUEST_PAYLOAD))
    client = _client()
    # Act
    request = client.workspace(WORKSPACE_ID).approvals.update(APPROVAL_ID, UPDATE)
    # Assert
    assert route.call_count == 1
    assert json.loads(route.calls[0].request.content) == {"state": "APPROVED", "note": "ok"}
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    assert request.id == APPROVAL_ID
    client.close()


@respx.mock
def test_resubmit_posts_and_declares_non_idempotent_command() -> None:
    # Arrange
    route = respx.post(f"{APPROVALS_URL}/resubmit-entries-for-approval").mock(
        return_value=Response(200, json=REQUEST_PAYLOAD)
    )
    client = _client()
    # Act
    request = client.workspace(WORKSPACE_ID).approvals.resubmit(RESUBMIT, time_view_mode="DECIMAL")
    # Assert
    assert dict(route.calls[0].request.url.params) == {"timeViewMode": "DECIMAL"}
    assert json.loads(route.calls[0].request.content) == {"periodStart": "2026-09-28T00:00:00Z", "type": "TIMESHEET"}
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert request.id == APPROVAL_ID
    client.close()


@respx.mock
async def test_async_list_page_sends_the_filter_and_declares_query() -> None:
    # Arrange
    route = respx.get(APPROVALS_URL).mock(return_value=Response(200, json=[DETAILS_PAYLOAD]))
    client = _async_client()
    request_filter = ApprovalRequestFilter(status=ApprovalState.APPROVED, types=[ApprovalRequestType.EXPENSE])
    # Act
    page = await client.workspace(WORKSPACE_ID).approvals.list_page(request_filter=request_filter, page_size=5)
    # Assert
    assert route.calls[0].request.url.params.multi_items() == [
        ("status", "APPROVED"),
        ("types", "EXPENSE"),
        ("page", "1"),
        ("page-size", "5"),
    ]
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    assert len(page.items) == 1
    await client.aclose()


@respx.mock
async def test_async_list_auto_paginates() -> None:
    # Arrange
    route = respx.get(APPROVALS_URL).mock(
        side_effect=[Response(200, json=[DETAILS_PAYLOAD] * 2), Response(200, json=[DETAILS_PAYLOAD])]
    )
    config = ClientConfig(api_key="dummy", base_url=BASE_URL, reports_base_url=BASE_URL, retry=NO_RETRY)
    transport = AsyncTransport(config, BASE_URL, ApiKeyAuth("dummy"))
    resource = AsyncApprovalsResource(transport, WORKSPACE_ID, page_size=2)
    # Act
    items = [item async for item in resource.list()]
    # Assert
    assert len(items) == 3
    assert route.call_count == 2
    await transport.aclose()


@respx.mock
async def test_async_submit_posts_to_the_type_path() -> None:
    # Arrange
    route = respx.post(f"{APPROVALS_URL}/TIMESHEET").mock(return_value=Response(201, json=REQUEST_PAYLOAD))
    client = _async_client()
    # Act
    request = await client.workspace(WORKSPACE_ID).approvals.submit(
        ApprovalRequestType.TIMESHEET, CREATE, time_view_mode="DECIMAL"
    )
    # Assert
    assert dict(route.calls[0].request.url.params) == {"timeViewMode": "DECIMAL"}
    assert json.loads(route.calls[0].request.content) == CREATE_BODY
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert request.id == APPROVAL_ID
    await client.aclose()


@respx.mock
async def test_async_submit_for_user_posts_to_the_user_type_path() -> None:
    # Arrange
    route = respx.post(f"{APPROVALS_URL}/users/{USER_ID}/EXPENSE").mock(
        return_value=Response(201, json=REQUEST_PAYLOAD)
    )
    client = _async_client()
    # Act
    request = await client.workspace(WORKSPACE_ID).approvals.submit_for_user(
        USER_ID, ApprovalRequestType.EXPENSE, CREATE
    )
    # Assert
    assert not route.calls[0].request.url.params
    assert json.loads(route.calls[0].request.content) == CREATE_BODY
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert request.id == APPROVAL_ID
    await client.aclose()


@respx.mock
async def test_async_update_patches_and_declares_idempotent_command() -> None:
    # Arrange
    route = respx.patch(f"{APPROVALS_URL}/{APPROVAL_ID}").mock(return_value=Response(200, json=REQUEST_PAYLOAD))
    client = _async_client()
    # Act
    request = await client.workspace(WORKSPACE_ID).approvals.update(APPROVAL_ID, UPDATE)
    # Assert
    assert json.loads(route.calls[0].request.content) == {"state": "APPROVED", "note": "ok"}
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    assert request.id == APPROVAL_ID
    await client.aclose()


@respx.mock
async def test_async_resubmit_posts_and_declares_non_idempotent_command() -> None:
    # Arrange
    route = respx.post(f"{APPROVALS_URL}/resubmit-entries-for-approval").mock(
        return_value=Response(200, json=REQUEST_PAYLOAD)
    )
    client = _async_client()
    # Act
    request = await client.workspace(WORKSPACE_ID).approvals.resubmit(RESUBMIT)
    # Assert
    assert not route.calls[0].request.url.params
    assert json.loads(route.calls[0].request.content) == {"periodStart": "2026-09-28T00:00:00Z", "type": "TIMESHEET"}
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert request.id == APPROVAL_ID
    await client.aclose()
