from __future__ import annotations

import datetime
import json
from typing import Final

import pytest
import respx
from httpx import Request
from httpx import Response

from clockify import NO_RETRY
from clockify import ApprovalSortOrder
from clockify import AsyncClockifyClient
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import CqsKind
from clockify import ExpenseCategoryCreate
from clockify import ExpenseCategoryFilter
from clockify import ExpenseCategorySortColumn
from clockify import ExpenseCategoryStatusUpdate
from clockify import ExpenseCategoryUpdate
from clockify import ExpenseChangeField
from clockify import ExpenseCreate
from clockify import ExpenseFile
from clockify import ExpenseUpdate
from clockify import RetryPolicy
from clockify._auth import ApiKeyAuth  # ruff: ignore[import-private-name]
from clockify._transport import AsyncTransport  # ruff: ignore[import-private-name]
from clockify._transport import Transport  # ruff: ignore[import-private-name]
from clockify.config import ClientConfig
from clockify.ids import WorkspaceId
from clockify.resources.expenses import AsyncExpenseCategoriesResource
from clockify.resources.expenses import AsyncExpensesResource
from clockify.resources.expenses import ExpenseCategoriesResource
from clockify.resources.expenses import ExpensesResource

BASE_URL: Final = "https://fake.clockify.test/api/v1"
WORKSPACE_ID: Final = WorkspaceId("64a1f0000000000000000001")
EXPENSES_URL: Final = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/expenses"
CATEGORIES_URL: Final = f"{EXPENSES_URL}/categories"
EXPENSE_ID: Final = "8e0000000000000000000001"
CATEGORY_ID: Final = "7c0000000000000000000001"

EXPENSE_PAYLOAD: Final = {"id": EXPENSE_ID, "userId": "u1", "categoryId": "c1", "total": 12.5}
DETAILS_PAYLOAD: Final = {"id": EXPENSE_ID, "total": 12.5, "fileName": "receipt.pdf"}
LIST_PAYLOAD: Final = {"expenses": {"count": 1, "expenses": [DETAILS_PAYLOAD]}, "dailyTotals": [], "weeklyTotals": []}
CATEGORY_PAYLOAD: Final = {"id": CATEGORY_ID, "name": "Travel", "archived": False}

DATE: Final = datetime.datetime(2026, 9, 30, tzinfo=datetime.UTC)
FILE: Final = ExpenseFile("receipt.pdf", b"%PDF-1.4 bytes", "application/pdf")
CREATE: Final = ExpenseCreate(
    user_id="u1", category_id="c1", project_id="p1", date=DATE, amount=12.5, billable=True, notes="taxi", file=FILE
)
UPDATE: Final = ExpenseUpdate(
    user_id="u1",
    category_id="c1",
    date=DATE,
    amount=15.0,
    change_fields=[ExpenseChangeField.AMOUNT, ExpenseChangeField.NOTES],
    notes="train",
)
CREATE_PARTS: Final = [
    ("userId", None, None, b"u1"),
    ("categoryId", None, None, b"c1"),
    ("projectId", None, None, b"p1"),
    ("date", None, None, b"2026-09-30T00:00:00Z"),
    ("amount", None, None, b"12.5"),
    ("billable", None, None, b"true"),
    ("notes", None, None, b"taxi"),
    ("file", "receipt.pdf", "application/pdf", b"%PDF-1.4 bytes"),
]
UPDATE_PARTS: Final = [
    ("userId", None, None, b"u1"),
    ("categoryId", None, None, b"c1"),
    ("date", None, None, b"2026-09-30T00:00:00Z"),
    ("amount", None, None, b"15.0"),
    ("changeFields", None, None, b"AMOUNT"),
    ("changeFields", None, None, b"NOTES"),
    ("notes", None, None, b"train"),
]


def _client() -> ClockifyClient:
    return ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


def _async_client() -> AsyncClockifyClient:
    return AsyncClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


def _parts(request: Request) -> list[tuple[str, str | None, str | None, bytes]]:
    content_type = request.headers["Content-Type"]
    assert content_type.startswith("multipart/form-data; boundary=")
    boundary = content_type.split("boundary=", 1)[1].encode()
    parts = []
    for chunk in request.content.split(b"--" + boundary)[1:-1]:
        head, _, body = chunk.strip(b"\r\n").partition(b"\r\n\r\n")
        headers = dict(line.decode().split(": ", 1) for line in head.split(b"\r\n"))
        disposition = headers["Content-Disposition"]
        name = disposition.split('name="', 1)[1].split('"', 1)[0]
        filename = disposition.split('filename="', 1)[1].split('"', 1)[0] if "filename=" in disposition else None
        parts.append((name, filename, headers.get("Content-Type"), body))
    return parts


@respx.mock
def test_list_page_unwraps_the_expenses_and_sends_the_filter() -> None:
    # Arrange
    route = respx.get(EXPENSES_URL).mock(return_value=Response(200, json=LIST_PAYLOAD))
    client = _client()
    # Act
    page = client.workspace(WORKSPACE_ID).expenses.list_page(user_id="u1", page=2, page_size=10)
    # Assert
    assert route.calls[0].request.url.params.multi_items() == [("user-id", "u1"), ("page", "2"), ("page-size", "10")]
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    assert [item.model_dump(by_alias=True, exclude_unset=True) for item in page.items] == [DETAILS_PAYLOAD]
    assert (page.page, page.page_size) == (2, 10)
    client.close()


@respx.mock
def test_list_page_without_expenses_is_empty() -> None:
    # Arrange
    respx.get(EXPENSES_URL).mock(return_value=Response(200, json={}))
    client = _client()
    # Act
    page = client.workspace(WORKSPACE_ID).expenses.list_page()
    # Assert
    assert page.items == []
    client.close()


@respx.mock
def test_list_auto_paginates_across_pages() -> None:
    # Arrange
    wrapped = {"expenses": {"expenses": [DETAILS_PAYLOAD] * 2}}
    route = respx.get(EXPENSES_URL).mock(
        side_effect=[Response(200, json=wrapped), Response(200, json={"expenses": {"expenses": [DETAILS_PAYLOAD]}})]
    )
    config = ClientConfig(api_key="dummy", base_url=BASE_URL, reports_base_url=BASE_URL, retry=NO_RETRY)
    transport = Transport(config, BASE_URL, ApiKeyAuth("dummy"))
    resource = ExpensesResource(transport, WORKSPACE_ID, page_size=2)
    # Act
    items = list(resource.list(user_id="u1"))
    # Assert
    assert len(items) == 3
    assert [call.request.url.params["page"] for call in route.calls] == ["1", "2"]
    transport.close()


@respx.mock
def test_get_reads_one_expense() -> None:
    # Arrange
    respx.get(f"{EXPENSES_URL}/{EXPENSE_ID}").mock(return_value=Response(200, json=EXPENSE_PAYLOAD))
    client = _client()
    # Act
    expense = client.workspace(WORKSPACE_ID).expenses.get(EXPENSE_ID)
    # Assert
    assert expense.model_dump(by_alias=True, exclude_unset=True) == EXPENSE_PAYLOAD
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    client.close()


@respx.mock
def test_create_posts_multipart_and_declares_non_idempotent_command() -> None:
    # Arrange
    route = respx.post(EXPENSES_URL).mock(return_value=Response(201, json=EXPENSE_PAYLOAD))
    client = _client()
    # Act
    expense = client.workspace(WORKSPACE_ID).expenses.create(CREATE)
    # Assert
    assert _parts(route.calls[0].request) == CREATE_PARTS
    assert not route.calls[0].request.url.params
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert expense.id == EXPENSE_ID
    client.close()


@respx.mock
def test_update_puts_multipart_without_a_file_and_declares_idempotent_command() -> None:
    # Arrange
    route = respx.put(f"{EXPENSES_URL}/{EXPENSE_ID}").mock(return_value=Response(200, json=EXPENSE_PAYLOAD))
    client = _client()
    # Act
    expense = client.workspace(WORKSPACE_ID).expenses.update(EXPENSE_ID, UPDATE)
    # Assert
    assert _parts(route.calls[0].request) == UPDATE_PARTS
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    assert expense.id == EXPENSE_ID
    client.close()


@respx.mock
def test_delete_removes_the_expense_and_declares_idempotent_command() -> None:
    # Arrange
    route = respx.delete(f"{EXPENSES_URL}/{EXPENSE_ID}").mock(return_value=Response(200))
    client = _client()
    # Act
    result = client.workspace(WORKSPACE_ID).expenses.delete(EXPENSE_ID)
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    assert result is None
    client.close()


@respx.mock
def test_update_retry_resends_the_whole_multipart_body() -> None:
    # Arrange
    route = respx.put(f"{EXPENSES_URL}/{EXPENSE_ID}").mock(
        side_effect=[Response(503), Response(200, json=EXPENSE_PAYLOAD)]
    )
    retry = RetryPolicy(max_attempts=2, backoff_base=0.0, random_source=lambda: 0.0)
    client = ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=retry))
    payload = ExpenseUpdate(
        user_id="u1", category_id="c1", date=DATE, amount=15.0, change_fields=[ExpenseChangeField.FILE], file=FILE
    )
    # Act
    expense = client.workspace(WORKSPACE_ID).expenses.update(EXPENSE_ID, payload)
    # Assert
    sent = [_parts(call.request) for call in route.calls]
    expected = [
        ("userId", None, None, b"u1"),
        ("categoryId", None, None, b"c1"),
        ("date", None, None, b"2026-09-30T00:00:00Z"),
        ("amount", None, None, b"15.0"),
        ("changeFields", None, None, b"FILE"),
        ("file", "receipt.pdf", "application/pdf", b"%PDF-1.4 bytes"),
    ]
    assert sent == [expected, expected]
    assert expense.id == EXPENSE_ID
    client.close()


@respx.mock
def test_category_list_page_unwraps_and_sends_the_filter() -> None:
    # Arrange
    route = respx.get(CATEGORIES_URL).mock(
        return_value=Response(200, json={"categories": [CATEGORY_PAYLOAD], "count": 1})
    )
    client = _client()
    category_filter = ExpenseCategoryFilter(
        archived=False,
        name="travel",
        sort_column=ExpenseCategorySortColumn.NAME,
        sort_order=ApprovalSortOrder.ASCENDING,
    )
    # Act
    page = client.workspace(WORKSPACE_ID).expense_categories.list_page(category_filter=category_filter, page_size=5)
    # Assert
    assert route.calls[0].request.url.params.multi_items() == [
        ("archived", "false"),
        ("name", "travel"),
        ("sort-column", "NAME"),
        ("sort-order", "ASCENDING"),
        ("page", "1"),
        ("page-size", "5"),
    ]
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    assert [item.model_dump(by_alias=True, exclude_unset=True) for item in page.items] == [CATEGORY_PAYLOAD]
    client.close()


@respx.mock
def test_category_list_auto_paginates() -> None:
    # Arrange
    route = respx.get(CATEGORIES_URL).mock(
        side_effect=[
            Response(200, json={"categories": [CATEGORY_PAYLOAD] * 2}),
            Response(200, json={"categories": [CATEGORY_PAYLOAD]}),
        ]
    )
    config = ClientConfig(api_key="dummy", base_url=BASE_URL, reports_base_url=BASE_URL, retry=NO_RETRY)
    transport = Transport(config, BASE_URL, ApiKeyAuth("dummy"))
    resource = ExpenseCategoriesResource(transport, WORKSPACE_ID, page_size=2)
    # Act
    items = list(resource.list())
    # Assert
    assert len(items) == 3
    assert [call.request.url.params["page"] for call in route.calls] == ["1", "2"]
    transport.close()


@respx.mock
def test_category_create_posts_json() -> None:
    # Arrange
    route = respx.post(CATEGORIES_URL).mock(return_value=Response(201, json=CATEGORY_PAYLOAD))
    client = _client()
    # Act
    category = client.workspace(WORKSPACE_ID).expense_categories.create(
        ExpenseCategoryCreate(name="Travel", has_unit_price=True, unit="km")
    )
    # Assert
    assert json.loads(route.calls[0].request.content) == {"name": "Travel", "hasUnitPrice": True, "unit": "km"}
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert category.id == CATEGORY_ID
    client.close()


@respx.mock
def test_category_update_puts_json() -> None:
    # Arrange
    route = respx.put(f"{CATEGORIES_URL}/{CATEGORY_ID}").mock(return_value=Response(200, json=CATEGORY_PAYLOAD))
    client = _client()
    # Act
    client.workspace(WORKSPACE_ID).expense_categories.update(CATEGORY_ID, ExpenseCategoryUpdate(name="Trips"))
    # Assert
    assert json.loads(route.calls[0].request.content) == {"name": "Trips"}
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    client.close()


@respx.mock
def test_category_update_status_patches_the_status_path() -> None:
    # Arrange
    route = respx.patch(f"{CATEGORIES_URL}/{CATEGORY_ID}/status").mock(
        return_value=Response(200, json={**CATEGORY_PAYLOAD, "archived": True})
    )
    client = _client()
    # Act
    category = client.workspace(WORKSPACE_ID).expense_categories.update_status(
        CATEGORY_ID, ExpenseCategoryStatusUpdate(archived=True)
    )
    # Assert
    assert json.loads(route.calls[0].request.content) == {"archived": True}
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    assert category.archived is True
    client.close()


@respx.mock
def test_category_delete_removes_it() -> None:
    # Arrange
    route = respx.delete(f"{CATEGORIES_URL}/{CATEGORY_ID}").mock(return_value=Response(204))
    client = _client()
    # Act
    result = client.workspace(WORKSPACE_ID).expense_categories.delete(CATEGORY_ID)
    # Assert
    assert route.call_count == 1
    assert result is None
    client.close()


def test_category_get_is_not_supported() -> None:
    # Arrange
    client = _client()
    # Act
    # Assert
    with pytest.raises(NotImplementedError, match="no endpoint to read one expense category"):
        client.workspace(WORKSPACE_ID).expense_categories.get(CATEGORY_ID)
    client.close()


@respx.mock
async def test_async_list_page_unwraps_and_sends_the_filter() -> None:
    # Arrange
    route = respx.get(EXPENSES_URL).mock(return_value=Response(200, json=LIST_PAYLOAD))
    client = _async_client()
    # Act
    page = await client.workspace(WORKSPACE_ID).expenses.list_page(user_id="u1", page_size=5)
    # Assert
    assert route.calls[0].request.url.params.multi_items() == [("user-id", "u1"), ("page", "1"), ("page-size", "5")]
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    assert [item.model_dump(by_alias=True, exclude_unset=True) for item in page.items] == [DETAILS_PAYLOAD]
    await client.aclose()


@respx.mock
async def test_async_list_auto_paginates() -> None:
    # Arrange
    route = respx.get(EXPENSES_URL).mock(
        side_effect=[
            Response(200, json={"expenses": {"expenses": [DETAILS_PAYLOAD] * 2}}),
            Response(200, json={"expenses": {"expenses": [DETAILS_PAYLOAD]}}),
        ]
    )
    config = ClientConfig(api_key="dummy", base_url=BASE_URL, reports_base_url=BASE_URL, retry=NO_RETRY)
    transport = AsyncTransport(config, BASE_URL, ApiKeyAuth("dummy"))
    resource = AsyncExpensesResource(transport, WORKSPACE_ID, page_size=2)
    # Act
    items = [item async for item in resource.list()]
    # Assert
    assert len(items) == 3
    assert route.call_count == 2
    await transport.aclose()


@respx.mock
async def test_async_get_create_update_delete() -> None:
    # Arrange
    get_route = respx.get(f"{EXPENSES_URL}/{EXPENSE_ID}").mock(return_value=Response(200, json=EXPENSE_PAYLOAD))
    create_route = respx.post(EXPENSES_URL).mock(return_value=Response(201, json=EXPENSE_PAYLOAD))
    update_route = respx.put(f"{EXPENSES_URL}/{EXPENSE_ID}").mock(return_value=Response(200, json=EXPENSE_PAYLOAD))
    delete_route = respx.delete(f"{EXPENSES_URL}/{EXPENSE_ID}").mock(return_value=Response(200))
    client = _async_client()
    expenses = client.workspace(WORKSPACE_ID).expenses
    # Act
    got = await expenses.get(EXPENSE_ID)
    created = await expenses.create(CREATE)
    updated = await expenses.update(EXPENSE_ID, UPDATE)
    deleted = await expenses.delete(EXPENSE_ID)
    # Assert
    kinds = [call.request.extensions.get("clockify_cqs") for call in respx.calls]
    assert kinds == [
        CqsKind.QUERY,
        CqsKind.NON_IDEMPOTENT_COMMAND,
        CqsKind.IDEMPOTENT_COMMAND,
        CqsKind.IDEMPOTENT_COMMAND,
    ]
    assert get_route.call_count == 1
    assert _parts(create_route.calls[0].request) == CREATE_PARTS
    assert _parts(update_route.calls[0].request) == UPDATE_PARTS
    assert delete_route.call_count == 1
    assert [got.id, created.id, updated.id, deleted] == [EXPENSE_ID, EXPENSE_ID, EXPENSE_ID, None]
    await client.aclose()


@respx.mock
async def test_async_categories_cover_the_json_endpoints() -> None:
    # Arrange
    respx.get(CATEGORIES_URL).mock(return_value=Response(200, json={"categories": [CATEGORY_PAYLOAD], "count": 1}))
    create_route = respx.post(CATEGORIES_URL).mock(return_value=Response(201, json=CATEGORY_PAYLOAD))
    update_route = respx.put(f"{CATEGORIES_URL}/{CATEGORY_ID}").mock(return_value=Response(200, json=CATEGORY_PAYLOAD))
    status_route = respx.patch(f"{CATEGORIES_URL}/{CATEGORY_ID}/status").mock(
        return_value=Response(200, json=CATEGORY_PAYLOAD)
    )
    delete_route = respx.delete(f"{CATEGORIES_URL}/{CATEGORY_ID}").mock(return_value=Response(204))
    client = _async_client()
    categories = client.workspace(WORKSPACE_ID).expense_categories
    # Act
    page = await categories.list_page(category_filter=ExpenseCategoryFilter(name="travel"), page_size=50)
    await categories.create(ExpenseCategoryCreate(name="Travel"))
    await categories.update(CATEGORY_ID, ExpenseCategoryUpdate(name="Trips"))
    await categories.update_status(CATEGORY_ID, ExpenseCategoryStatusUpdate(archived=True))
    await categories.delete(CATEGORY_ID)
    # Assert
    assert respx.calls[0].request.url.params.multi_items() == [("name", "travel"), ("page", "1"), ("page-size", "50")]
    assert [call.request.extensions.get("clockify_cqs") for call in respx.calls] == [
        CqsKind.QUERY,
        CqsKind.NON_IDEMPOTENT_COMMAND,
        CqsKind.IDEMPOTENT_COMMAND,
        CqsKind.IDEMPOTENT_COMMAND,
        CqsKind.IDEMPOTENT_COMMAND,
    ]
    assert json.loads(create_route.calls[0].request.content) == {"name": "Travel"}
    assert json.loads(update_route.calls[0].request.content) == {"name": "Trips"}
    assert json.loads(status_route.calls[0].request.content) == {"archived": True}
    assert delete_route.call_count == 1
    assert [item.id for item in page.items] == [CATEGORY_ID]
    await client.aclose()


@respx.mock
async def test_async_category_list_auto_paginates_and_get_is_not_supported() -> None:
    # Arrange
    route = respx.get(CATEGORIES_URL).mock(
        side_effect=[
            Response(200, json={"categories": [CATEGORY_PAYLOAD] * 2}),
            Response(200, json={"categories": [CATEGORY_PAYLOAD]}),
        ]
    )
    config = ClientConfig(api_key="dummy", base_url=BASE_URL, reports_base_url=BASE_URL, retry=NO_RETRY)
    transport = AsyncTransport(config, BASE_URL, ApiKeyAuth("dummy"))
    resource = AsyncExpenseCategoriesResource(transport, WORKSPACE_ID, page_size=2)
    # Act
    items = [item async for item in resource.list()]
    # Assert
    assert len(items) == 3
    assert route.call_count == 2
    with pytest.raises(NotImplementedError, match="no endpoint to read one expense category"):
        await resource.get(CATEGORY_ID)
    await transport.aclose()


FILE_ID: Final = "66a1f0000000000000000099"
RECEIPT_BYTES: Final = b"%PDF-1.7\n\x00\xff binary receipt"


@respx.mock
def test_download_file_gets_the_receipt_bytes_as_a_query() -> None:
    # Arrange
    route = respx.get(f"{EXPENSES_URL}/{EXPENSE_ID}/files/{FILE_ID}").mock(
        return_value=Response(200, content=RECEIPT_BYTES, headers={"Content-Type": "application/pdf"})
    )
    client = _client()
    # Act
    data = client.workspace(WORKSPACE_ID).expenses.download_file(EXPENSE_ID, FILE_ID)
    # Assert
    assert data == RECEIPT_BYTES
    assert route.call_count == 1
    assert not route.calls[0].request.url.params
    assert not route.calls[0].request.content
    assert route.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    client.close()


@respx.mock
async def test_async_download_file_gets_the_receipt_bytes_as_a_query() -> None:
    # Arrange
    route = respx.get(f"{EXPENSES_URL}/{EXPENSE_ID}/files/{FILE_ID}").mock(
        return_value=Response(200, content=RECEIPT_BYTES, headers={"Content-Type": "application/pdf"})
    )
    client = _async_client()
    # Act
    data = await client.workspace(WORKSPACE_ID).expenses.download_file(EXPENSE_ID, FILE_ID)
    # Assert
    assert data == RECEIPT_BYTES
    assert route.call_count == 1
    assert route.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    await client.aclose()


@respx.mock
def test_download_file_retries_a_5xx_because_it_is_a_query() -> None:
    # Arrange
    route = respx.get(f"{EXPENSES_URL}/{EXPENSE_ID}/files/{FILE_ID}").mock(
        side_effect=[Response(503), Response(200, content=RECEIPT_BYTES)]
    )
    retry = RetryPolicy(max_attempts=2, backoff_base=0.0, random_source=lambda: 0.0)
    client = ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=retry))
    # Act
    data = client.workspace(WORKSPACE_ID).expenses.download_file(EXPENSE_ID, FILE_ID)
    # Assert
    assert route.call_count == 2
    assert data == RECEIPT_BYTES
    client.close()
