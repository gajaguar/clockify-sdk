from __future__ import annotations

import datetime
import json
from typing import Final

import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import ApprovalSortOrder
from clockify import AsyncClockifyClient
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import CqsKind
from clockify import CreatedInvoice
from clockify import Invoice
from clockify import InvoiceApplyTaxes
from clockify import InvoiceCreate
from clockify import InvoiceDefaultsUpdate
from clockify import InvoiceDetails
from clockify import InvoiceFilter
from clockify import InvoiceFilterContains
from clockify import InvoiceFilterStatus
from clockify import InvoiceIdFilter
from clockify import InvoiceImportExpenseGroupBy
from clockify import InvoiceImportGroupType
from clockify import InvoiceImportTimeGroupType
from clockify import InvoiceInfo
from clockify import InvoiceIssueDateRange
from clockify import InvoiceItem
from clockify import InvoiceItemCreate
from clockify import InvoiceItemsImport
from clockify import InvoiceLabelsUpdate
from clockify import InvoicePayment
from clockify import InvoicePaymentCreate
from clockify import InvoiceSearch
from clockify import InvoiceSettings
from clockify import InvoiceSettingsUpdate
from clockify import InvoiceSortColumn
from clockify import InvoiceStatus
from clockify import InvoiceStatusUpdate
from clockify import InvoiceTaxType
from clockify import InvoiceUpdate
from clockify import InvoiceVisibleZeroField
from clockify._auth import ApiKeyAuth  # ruff: ignore[import-private-name]
from clockify._transport import AsyncTransport  # ruff: ignore[import-private-name]
from clockify._transport import Transport  # ruff: ignore[import-private-name]
from clockify.config import ClientConfig
from clockify.ids import ClientId
from clockify.ids import WorkspaceId
from clockify.resources.invoices import AsyncInvoiceItemsResource
from clockify.resources.invoices import AsyncInvoicePaymentsResource
from clockify.resources.invoices import AsyncInvoicesResource
from clockify.resources.invoices import InvoicePaymentsResource
from clockify.resources.invoices import InvoicesResource

BASE_URL: Final = "https://fake.clockify.test/api/v1"
WORKSPACE_ID: Final = WorkspaceId("64a1f0000000000000000001")
INVOICES_URL: Final = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/invoices"
INVOICE_ID: Final = "66b1f0000000000000000010"
ITEM_URL: Final = f"{INVOICES_URL}/{INVOICE_ID}"
CLIENT_ID: Final = ClientId("66b1f0000000000000000020")
PAYMENT_ID: Final = "66b1f0000000000000000030"
CQS: Final = "clockify_cqs"
ISSUED: Final = datetime.datetime(2026, 3, 1, tzinfo=datetime.UTC)
DUE: Final = datetime.datetime(2026, 3, 31, tzinfo=datetime.UTC)

INVOICE_PAYLOAD: Final = {
    "id": INVOICE_ID,
    "number": "INV-1",
    "status": "PARTIALLY_PAID",
    "clientId": str(CLIENT_ID),
    "clientName": "Acme",
    "currency": "USD",
    "amount": 12000,
    "balance": 2000,
    "paid": 10000,
    "issuedDate": "2026-03-01T00:00:00Z",
    "dueDate": "2026-03-31T00:00:00Z",
}
INVOICE: Final = Invoice(
    id=INVOICE_ID,
    number="INV-1",
    status=InvoiceStatus.PARTIALLY_PAID,
    client_id=CLIENT_ID,
    client_name="Acme",
    currency="USD",
    amount=12000,
    balance=2000,
    paid=10000,
    issued_date=ISSUED,
    due_date=DUE,
)
INFO_PAYLOAD: Final = {**INVOICE_PAYLOAD, "billFrom": "Me Inc", "daysOverdue": 4}
INFO: Final = InvoiceInfo(
    id=INVOICE_ID,
    number="INV-1",
    status=InvoiceStatus.PARTIALLY_PAID,
    client_id=CLIENT_ID,
    client_name="Acme",
    bill_from="Me Inc",
    currency="USD",
    amount=12000,
    balance=2000,
    paid=10000,
    days_overdue=4,
    issued_date=ISSUED,
    due_date=DUE,
)
DETAILS_PAYLOAD: Final = {
    "id": INVOICE_ID,
    "number": "INV-1",
    "status": "UNSENT",
    "currency": "USD",
    "amount": 12000,
    "discount": 10.5,
    "taxType": "SIMPLE",
    "items": [
        {
            "order": 1,
            "description": "Work",
            "itemType": "Service",
            "quantity": 2,
            "unitPrice": 6000,
            "amount": 12000,
            "applyTaxes": "NONE",
            "importType": "NOT_IMPORTED",
        }
    ],
}
DETAILS: Final = InvoiceDetails(
    id=INVOICE_ID,
    number="INV-1",
    status=InvoiceStatus.UNSENT,
    currency="USD",
    amount=12000,
    discount=10.5,
    tax_type=InvoiceTaxType.SIMPLE,
    items=[
        InvoiceItem(
            order=1,
            description="Work",
            item_type="Service",
            quantity=2,
            unit_price=6000,
            amount=12000,
            apply_taxes=InvoiceApplyTaxes.NONE,
            import_type="NOT_IMPORTED",
        )
    ],
)
PAYMENT_PAYLOAD: Final = {
    "id": PAYMENT_ID,
    "amount": 5000,
    "author": "Ada",
    "date": "2026-03-10T00:00:00Z",
    "note": "wire",
}
PAYMENT: Final = InvoicePayment(
    id=PAYMENT_ID,
    amount=5000,
    author="Ada",
    date=datetime.datetime(2026, 3, 10, tzinfo=datetime.UTC),
    note="wire",
)
LABEL_NAMES: Final = (
    "amount",
    "bill_from",
    "bill_to",
    "description",
    "discount",
    "due_date",
    "issue_date",
    "item_type",
    "notes",
    "paid",
    "quantity",
    "subtotal",
    "tax",
    "tax2",
    "total",
    "total_amount_due",
    "unit_price",
)
LABELS: Final = InvoiceLabelsUpdate.model_validate(dict(zip(LABEL_NAMES, map(str.upper, LABEL_NAMES), strict=True)))
LABELS_BODY: Final = {
    "amount": "AMOUNT",
    "billFrom": "BILL_FROM",
    "billTo": "BILL_TO",
    "description": "DESCRIPTION",
    "discount": "DISCOUNT",
    "dueDate": "DUE_DATE",
    "issueDate": "ISSUE_DATE",
    "itemType": "ITEM_TYPE",
    "notes": "NOTES",
    "paid": "PAID",
    "quantity": "QUANTITY",
    "subtotal": "SUBTOTAL",
    "tax": "TAX",
    "tax2": "TAX2",
    "total": "TOTAL",
    "totalAmountDue": "TOTAL_AMOUNT_DUE",
    "unitPrice": "UNIT_PRICE",
}
SETTINGS_PAYLOAD: Final = {
    "defaults": {"dueDays": 30, "taxType": "COMPOUND", "taxPercent": 7.5},
    "exportFields": {"quantity": True, "rtl": False},
    "labels": {"amount": "Amount", "totalAmount": "Total"},
}


def _client() -> ClockifyClient:
    return ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


def _async_client() -> AsyncClockifyClient:
    return AsyncClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


def _config() -> ClientConfig:
    return ClientConfig(api_key="dummy", base_url=BASE_URL, reports_base_url=BASE_URL, retry=NO_RETRY)


def _cqs(route: respx.Route) -> object:
    return route.calls[0].request.extensions.get(CQS)


# --- invoices -------------------------------------------------------------------------


@respx.mock
def test_list_page_sends_the_filter_and_page_params_and_unwraps_the_envelope() -> None:
    # Arrange
    route = respx.get(INVOICES_URL).mock(return_value=Response(200, json={"invoices": [INVOICE_PAYLOAD], "total": 1}))
    client = _client()
    invoice_filter = InvoiceFilter(
        statuses=[InvoiceStatus.UNSENT, InvoiceStatus.PAID],
        sort_column=InvoiceSortColumn.DUE_ON,
        sort_order=ApprovalSortOrder.DESCENDING,
    )
    # Act
    page = client.workspace(WORKSPACE_ID).invoices.list_page(invoice_filter=invoice_filter, page=2, page_size=10)
    # Assert
    assert route.calls[0].request.url.params.multi_items() == [
        ("statuses", "UNSENT"),
        ("statuses", "PAID"),
        ("sort-column", "DUE_ON"),
        ("sort-order", "DESCENDING"),
        ("page", "2"),
        ("page-size", "10"),
    ]
    assert _cqs(route) == CqsKind.QUERY
    assert page.items == [INVOICE]
    client.close()


@respx.mock
def test_list_auto_paginates_and_tolerates_an_empty_envelope() -> None:
    # Arrange
    route = respx.get(INVOICES_URL).mock(
        side_effect=[
            Response(200, json={"invoices": [INVOICE_PAYLOAD, INVOICE_PAYLOAD], "total": 3}),
            Response(200, json={}),
        ]
    )
    transport = Transport(_config(), BASE_URL, ApiKeyAuth("dummy"))
    # Act
    invoices = list(InvoicesResource(transport, WORKSPACE_ID, page_size=2).list())
    # Assert
    assert invoices == [INVOICE, INVOICE]
    assert [call.request.url.params.multi_items() for call in route.calls] == [
        [("page", "1"), ("page-size", "2")],
        [("page", "2"), ("page-size", "2")],
    ]
    transport.close()


@respx.mock
def test_search_page_posts_the_filter_and_the_page_in_the_body_as_a_query() -> None:
    # Arrange
    route = respx.post(f"{INVOICES_URL}/info").mock(
        return_value=Response(200, json={"invoices": [INFO_PAYLOAD], "total": 1})
    )
    client = _client()
    search = InvoiceSearch(
        clients=InvoiceIdFilter(
            contains=InvoiceFilterContains.CONTAINS, ids=[str(CLIENT_ID)], status=InvoiceFilterStatus.ALL
        ),
        invoice_number="INV",
        issue_date=InvoiceIssueDateRange(start=datetime.date(2026, 3, 1), end=datetime.date(2026, 3, 31)),
        greater_than_amount=100,
        statuses=[InvoiceStatus.OVERDUE],
        sort_column=InvoiceSortColumn.AMOUNT,
        sort_order=ApprovalSortOrder.ASCENDING,
        strict_search=True,
    )
    # Act
    page = client.workspace(WORKSPACE_ID).invoices.search_page(search, page=2, page_size=20)
    # Assert
    assert not route.calls[0].request.url.params
    assert json.loads(route.calls[0].request.content) == {
        "clients": {"contains": "CONTAINS", "ids": [str(CLIENT_ID)], "status": "ALL"},
        "invoiceNumber": "INV",
        "issueDate": {"issue-date-start": "2026-03-01", "issue-date-end": "2026-03-31"},
        "greaterThanAmount": 100,
        "statuses": ["OVERDUE"],
        "sortColumn": "AMOUNT",
        "sortOrder": "ASCENDING",
        "strictSearch": True,
        "page": 2,
        "pageSize": 20,
    }
    assert _cqs(route) == CqsKind.QUERY
    assert page.items == [INFO]
    client.close()


@respx.mock
def test_search_without_a_filter_auto_paginates() -> None:
    # Arrange
    route = respx.post(f"{INVOICES_URL}/info").mock(
        side_effect=[
            Response(200, json={"invoices": [INFO_PAYLOAD, INFO_PAYLOAD]}),
            Response(200, json={"invoices": []}),
        ]
    )
    transport = Transport(_config(), BASE_URL, ApiKeyAuth("dummy"))
    # Act
    found = list(InvoicesResource(transport, WORKSPACE_ID, page_size=2).search())
    # Assert
    assert found == [INFO, INFO]
    assert [json.loads(call.request.content) for call in route.calls] == [
        {"page": 1, "pageSize": 2},
        {"page": 2, "pageSize": 2},
    ]
    transport.close()


@respx.mock
def test_get_create_update_delete_duplicate_status_and_export() -> None:
    # Arrange
    get_route = respx.get(ITEM_URL).mock(return_value=Response(200, json=DETAILS_PAYLOAD))
    create_route = respx.post(INVOICES_URL).mock(
        return_value=Response(201, json={"id": INVOICE_ID, "number": "INV-1", "clientId": str(CLIENT_ID)})
    )
    put_route = respx.put(ITEM_URL).mock(return_value=Response(200, json=DETAILS_PAYLOAD))
    delete_route = respx.delete(ITEM_URL).mock(return_value=Response(200))
    duplicate_route = respx.post(f"{ITEM_URL}/duplicate").mock(return_value=Response(201, json=DETAILS_PAYLOAD))
    status_route = respx.patch(f"{ITEM_URL}/status").mock(return_value=Response(200))
    export_route = respx.get(f"{ITEM_URL}/export").mock(return_value=Response(200, content=b"%PDF\x00\xff"))
    invoices = _client().workspace(WORKSPACE_ID).invoices
    create = InvoiceCreate(client_id=CLIENT_ID, currency="USD", number="INV-1", issued_date=ISSUED, due_date=DUE)
    update = InvoiceUpdate(
        currency="USD",
        number="INV-1",
        issued_date=ISSUED,
        due_date=DUE,
        discount_percent=10.0,
        tax_percent=7.5,
        tax2_percent=0.0,
        tax_type=InvoiceTaxType.COMPOUND,
        visible_zero_fields=InvoiceVisibleZeroField.TAX_2,
    )
    # Act
    results = (
        invoices.get(INVOICE_ID),
        invoices.create(create),
        invoices.update(INVOICE_ID, update),
        invoices.delete(INVOICE_ID),
        invoices.duplicate(INVOICE_ID),
        invoices.update_status(INVOICE_ID, InvoiceStatusUpdate(invoice_status=InvoiceStatus.SENT)),
        invoices.export(INVOICE_ID, user_locale="en"),
    )
    # Assert
    assert results == (
        DETAILS,
        CreatedInvoice(id=INVOICE_ID, number="INV-1", client_id=CLIENT_ID),
        DETAILS,
        None,
        DETAILS,
        None,
        b"%PDF\x00\xff",
    )
    assert json.loads(create_route.calls[0].request.content) == {
        "clientId": str(CLIENT_ID),
        "currency": "USD",
        "number": "INV-1",
        "issuedDate": "2026-03-01T00:00:00Z",
        "dueDate": "2026-03-31T00:00:00Z",
    }
    assert json.loads(put_route.calls[0].request.content) == {
        "currency": "USD",
        "number": "INV-1",
        "issuedDate": "2026-03-01T00:00:00Z",
        "dueDate": "2026-03-31T00:00:00Z",
        "discountPercent": 10.0,
        "taxPercent": 7.5,
        "tax2Percent": 0.0,
        "taxType": "COMPOUND",
        "visibleZeroFields": "TAX_2",
    }
    assert json.loads(status_route.calls[0].request.content) == {"invoiceStatus": "SENT"}
    assert export_route.calls[0].request.url.params.multi_items() == [("userLocale", "en")]
    assert [
        _cqs(r)
        for r in (get_route, create_route, put_route, delete_route, duplicate_route, status_route, export_route)
    ] == [
        CqsKind.QUERY,
        CqsKind.NON_IDEMPOTENT_COMMAND,
        CqsKind.IDEMPOTENT_COMMAND,
        CqsKind.IDEMPOTENT_COMMAND,
        CqsKind.NON_IDEMPOTENT_COMMAND,
        CqsKind.IDEMPOTENT_COMMAND,
        CqsKind.QUERY,
    ]


@respx.mock
def test_settings_are_read_and_replaced() -> None:
    # Arrange
    get_route = respx.get(f"{INVOICES_URL}/settings").mock(return_value=Response(200, json=SETTINGS_PAYLOAD))
    put_route = respx.put(f"{INVOICES_URL}/settings").mock(return_value=Response(200, json=SETTINGS_PAYLOAD))
    invoices = _client().workspace(WORKSPACE_ID).invoices
    update = InvoiceSettingsUpdate(labels=LABELS, defaults=InvoiceDefaultsUpdate(notes="n", subject="s", due_days=14))
    # Act
    read = invoices.get_settings()
    replaced = invoices.update_settings(update)
    # Assert
    assert read.defaults is not None
    assert (read.defaults.due_days, read.defaults.tax_type, read.defaults.tax_percent) == (
        30,
        InvoiceTaxType.COMPOUND,
        7.5,
    )
    assert replaced == read
    assert isinstance(read, InvoiceSettings)
    assert json.loads(put_route.calls[0].request.content) == {
        "labels": LABELS_BODY,
        "defaults": {"notes": "n", "subject": "s", "dueDays": 14},
    }
    assert (_cqs(get_route), _cqs(put_route)) == (CqsKind.QUERY, CqsKind.IDEMPOTENT_COMMAND)


async def test_async_invoices_list_search_and_get() -> None:
    # Arrange
    with respx.mock:
        list_route = respx.get(INVOICES_URL).mock(
            side_effect=[
                Response(200, json={"invoices": [INVOICE_PAYLOAD, INVOICE_PAYLOAD]}),
                Response(200, json={"invoices": []}),
            ]
        )
        search_route = respx.post(f"{INVOICES_URL}/info").mock(
            return_value=Response(200, json={"invoices": [INFO_PAYLOAD]})
        )
        get_route = respx.get(ITEM_URL).mock(return_value=Response(200, json=DETAILS_PAYLOAD))
        transport = AsyncTransport(_config(), BASE_URL, ApiKeyAuth("dummy"))
        invoices = AsyncInvoicesResource(transport, WORKSPACE_ID, page_size=2)
        invoice_filter = InvoiceFilter(statuses=[InvoiceStatus.VOID])
        # Act
        listed = [invoice async for invoice in invoices.list(invoice_filter=invoice_filter)]
        found = [info async for info in invoices.search(InvoiceSearch(invoice_number="INV"))]
        got = await invoices.get(INVOICE_ID)
        # Assert
        assert listed == [INVOICE, INVOICE]
        assert list_route.calls[0].request.url.params.multi_items() == [
            ("statuses", "VOID"),
            ("page", "1"),
            ("page-size", "2"),
        ]
        assert found == [INFO]
        assert json.loads(search_route.calls[0].request.content) == {"invoiceNumber": "INV", "page": 1, "pageSize": 2}
        assert got == DETAILS
        assert [_cqs(r) for r in (list_route, search_route, get_route)] == [CqsKind.QUERY] * 3
        await transport.aclose()


async def test_async_invoices_write_and_export() -> None:
    # Arrange
    with respx.mock:
        create_route = respx.post(INVOICES_URL).mock(return_value=Response(201, json={"id": INVOICE_ID}))
        put_route = respx.put(ITEM_URL).mock(return_value=Response(200, json=DETAILS_PAYLOAD))
        delete_route = respx.delete(ITEM_URL).mock(return_value=Response(200))
        duplicate_route = respx.post(f"{ITEM_URL}/duplicate").mock(return_value=Response(201, json=DETAILS_PAYLOAD))
        status_route = respx.patch(f"{ITEM_URL}/status").mock(return_value=Response(200))
        export_route = respx.get(f"{ITEM_URL}/export").mock(return_value=Response(200, content=b"\x00bytes"))
        transport = AsyncTransport(_config(), BASE_URL, ApiKeyAuth("dummy"))
        invoices = AsyncInvoicesResource(transport, WORKSPACE_ID)
        create = InvoiceCreate(client_id=CLIENT_ID, currency="USD", number="INV-1", issued_date=ISSUED, due_date=DUE)
        update = InvoiceUpdate(
            currency="USD",
            number="INV-1",
            issued_date=ISSUED,
            due_date=DUE,
            discount_percent=0.0,
            tax_percent=0.0,
            tax2_percent=0.0,
        )
        # Act
        results = (
            await invoices.create(create),
            await invoices.update(INVOICE_ID, update),
            await invoices.delete(INVOICE_ID),
            await invoices.duplicate(INVOICE_ID),
            await invoices.update_status(INVOICE_ID, InvoiceStatusUpdate(invoice_status=InvoiceStatus.VOID)),
            await invoices.export(INVOICE_ID, user_locale="es"),
        )
        # Assert
        assert results == (CreatedInvoice(id=INVOICE_ID), DETAILS, None, DETAILS, None, b"\x00bytes")
        assert json.loads(status_route.calls[0].request.content) == {"invoiceStatus": "VOID"}
        assert export_route.calls[0].request.url.params["userLocale"] == "es"
        assert [
            _cqs(r) for r in (create_route, put_route, delete_route, duplicate_route, status_route, export_route)
        ] == [
            CqsKind.NON_IDEMPOTENT_COMMAND,
            CqsKind.IDEMPOTENT_COMMAND,
            CqsKind.IDEMPOTENT_COMMAND,
            CqsKind.NON_IDEMPOTENT_COMMAND,
            CqsKind.IDEMPOTENT_COMMAND,
            CqsKind.QUERY,
        ]
        await transport.aclose()


async def test_async_settings_are_read_and_replaced() -> None:
    # Arrange
    with respx.mock:
        get_route = respx.get(f"{INVOICES_URL}/settings").mock(return_value=Response(200, json=SETTINGS_PAYLOAD))
        put_route = respx.put(f"{INVOICES_URL}/settings").mock(return_value=Response(200, json=SETTINGS_PAYLOAD))
        transport = AsyncTransport(_config(), BASE_URL, ApiKeyAuth("dummy"))
        invoices = AsyncInvoicesResource(transport, WORKSPACE_ID)
        # Act
        settings = await invoices.get_settings()
        replaced = await invoices.update_settings(InvoiceSettingsUpdate(labels=LABELS))
        # Assert
        assert settings == replaced
        assert json.loads(put_route.calls[0].request.content) == {"labels": LABELS_BODY}
        assert (_cqs(get_route), _cqs(put_route)) == (CqsKind.QUERY, CqsKind.IDEMPOTENT_COMMAND)
        await transport.aclose()


# --- items ----------------------------------------------------------------------------


@respx.mock
def test_items_are_added_imported_and_deleted_by_order() -> None:
    # Arrange
    add_route = respx.post(f"{ITEM_URL}/items").mock(return_value=Response(200, json=DETAILS_PAYLOAD))
    import_route = respx.post(f"{ITEM_URL}/items/import").mock(return_value=Response(200, json=DETAILS_PAYLOAD))
    delete_route = respx.delete(f"{ITEM_URL}/items/2").mock(return_value=Response(200, json=DETAILS_PAYLOAD))
    items = _client().workspace(WORKSPACE_ID).invoice_items
    add = InvoiceItemCreate(
        description="Work", item_type="Service", quantity=2, unit_price=6000, apply_taxes=InvoiceApplyTaxes.TAX1TAX2
    )
    import_payload = InvoiceItemsImport(
        start=ISSUED,
        end=DUE,
        import_expenses=True,
        project_filter=InvoiceIdFilter(contains=InvoiceFilterContains.CONTAINS_ONLY, ids=["p1"]),
        time_entry_group_type=InvoiceImportTimeGroupType.GROUPED,
        expenses_group_by=InvoiceImportExpenseGroupBy.CATEGORY,
        expenses_group_type=InvoiceImportGroupType.GROUPED,
        round_time_entry_duration=False,
    )
    # Act
    results = (
        items.add(INVOICE_ID, add),
        items.import_entries(INVOICE_ID, import_payload),
        items.delete(INVOICE_ID, 2),
    )
    # Assert
    assert results == (DETAILS, DETAILS, DETAILS)
    assert json.loads(add_route.calls[0].request.content) == {
        "description": "Work",
        "itemType": "Service",
        "quantity": 2,
        "unitPrice": 6000,
        "applyTaxes": "TAX1TAX2",
    }
    assert json.loads(import_route.calls[0].request.content) == {
        "from": "2026-03-01T00:00:00Z",
        "to": "2026-03-31T00:00:00Z",
        "importExpenses": True,
        "projectFilter": {"contains": "CONTAINS_ONLY", "ids": ["p1"]},
        "timeEntryGroupType": "GROUPED",
        "expensesGroupBy": "CATEGORY",
        "expensesGroupType": "GROUPED",
        "roundTimeEntryDuration": False,
    }
    assert not delete_route.calls[0].request.content
    assert [_cqs(r) for r in (add_route, import_route, delete_route)] == [CqsKind.NON_IDEMPOTENT_COMMAND] * 3


async def test_async_items_are_added_imported_and_deleted_by_order() -> None:
    # Arrange
    with respx.mock:
        add_route = respx.post(f"{ITEM_URL}/items").mock(return_value=Response(200, json=DETAILS_PAYLOAD))
        import_route = respx.post(f"{ITEM_URL}/items/import").mock(return_value=Response(200, json=DETAILS_PAYLOAD))
        delete_route = respx.delete(f"{ITEM_URL}/items/1").mock(return_value=Response(200, json=DETAILS_PAYLOAD))
        transport = AsyncTransport(_config(), BASE_URL, ApiKeyAuth("dummy"))
        items = AsyncInvoiceItemsResource(transport, WORKSPACE_ID)
        # Act
        added = await items.add(
            INVOICE_ID,
            InvoiceItemCreate(
                description="d", item_type="Service", quantity=1, unit_price=1, apply_taxes=InvoiceApplyTaxes.NONE
            ),
        )
        imported = await items.import_entries(
            INVOICE_ID,
            InvoiceItemsImport(
                start=ISSUED,
                end=DUE,
                import_expenses=False,
                project_filter=InvoiceIdFilter(),
                time_entry_group_type=InvoiceImportTimeGroupType.SINGLE_ITEM,
            ),
        )
        deleted = await items.delete(INVOICE_ID, 1)
        # Assert
        assert (added, imported, deleted) == (DETAILS, DETAILS, DETAILS)
        assert json.loads(import_route.calls[0].request.content) == {
            "from": "2026-03-01T00:00:00Z",
            "to": "2026-03-31T00:00:00Z",
            "importExpenses": False,
            "projectFilter": {},
            "timeEntryGroupType": "SINGLE_ITEM",
        }
        assert [_cqs(r) for r in (add_route, import_route, delete_route)] == [CqsKind.NON_IDEMPOTENT_COMMAND] * 3
        await transport.aclose()


# --- payments -------------------------------------------------------------------------


@respx.mock
def test_payments_are_listed_added_and_deleted() -> None:
    # Arrange
    list_route = respx.get(f"{ITEM_URL}/payments").mock(return_value=Response(200, json=[PAYMENT_PAYLOAD]))
    add_route = respx.post(f"{ITEM_URL}/payments").mock(return_value=Response(201, json=DETAILS_PAYLOAD))
    delete_route = respx.delete(f"{ITEM_URL}/payments/{PAYMENT_ID}").mock(
        return_value=Response(200, json=DETAILS_PAYLOAD)
    )
    payments = _client().workspace(WORKSPACE_ID).invoice_payments
    # Act
    page = payments.list_page(INVOICE_ID, page=2, page_size=5)
    added = payments.add(
        INVOICE_ID,
        InvoicePaymentCreate(
            amount=5000, note="wire", payment_date=datetime.datetime(2026, 3, 10, tzinfo=datetime.UTC)
        ),
    )
    deleted = payments.delete(INVOICE_ID, PAYMENT_ID)
    # Assert
    assert list_route.calls[0].request.url.params.multi_items() == [("page", "2"), ("page-size", "5")]
    assert page.items == [PAYMENT]
    assert (added, deleted) == (DETAILS, DETAILS)
    assert json.loads(add_route.calls[0].request.content) == {
        "amount": 5000,
        "note": "wire",
        "paymentDate": "2026-03-10T00:00:00Z",
    }
    assert [_cqs(r) for r in (list_route, add_route, delete_route)] == [
        CqsKind.QUERY,
        CqsKind.NON_IDEMPOTENT_COMMAND,
        CqsKind.IDEMPOTENT_COMMAND,
    ]


@respx.mock
def test_payments_list_auto_paginates() -> None:
    # Arrange
    route = respx.get(f"{ITEM_URL}/payments").mock(
        side_effect=[Response(200, json=[PAYMENT_PAYLOAD, PAYMENT_PAYLOAD]), Response(200, json=[PAYMENT_PAYLOAD])]
    )
    transport = Transport(_config(), BASE_URL, ApiKeyAuth("dummy"))
    # Act
    payments = list(InvoicePaymentsResource(transport, WORKSPACE_ID, page_size=2).list(INVOICE_ID))
    # Assert
    assert payments == [PAYMENT, PAYMENT, PAYMENT]
    assert [call.request.url.params["page"] for call in route.calls] == ["1", "2"]
    transport.close()


async def test_async_payments_are_listed_added_and_deleted() -> None:
    # Arrange
    with respx.mock:
        list_route = respx.get(f"{ITEM_URL}/payments").mock(
            side_effect=[
                Response(200, json=[PAYMENT_PAYLOAD, PAYMENT_PAYLOAD]),
                Response(200, json=[]),
                Response(200, json=[]),
            ]
        )
        add_route = respx.post(f"{ITEM_URL}/payments").mock(return_value=Response(201, json=DETAILS_PAYLOAD))
        delete_route = respx.delete(f"{ITEM_URL}/payments/{PAYMENT_ID}").mock(
            return_value=Response(200, json=DETAILS_PAYLOAD)
        )
        transport = AsyncTransport(_config(), BASE_URL, ApiKeyAuth("dummy"))
        payments = AsyncInvoicePaymentsResource(transport, WORKSPACE_ID, page_size=2)
        # Act
        listed = [payment async for payment in payments.list(INVOICE_ID)]
        page = await payments.list_page(INVOICE_ID, page_size=1)
        added = await payments.add(INVOICE_ID, InvoicePaymentCreate(amount=1))
        deleted = await payments.delete(INVOICE_ID, PAYMENT_ID)
        # Assert
        assert listed == [PAYMENT, PAYMENT]
        assert page.items == []
        assert (added, deleted) == (DETAILS, DETAILS)
        assert json.loads(add_route.calls[0].request.content) == {"amount": 1}
        assert [_cqs(r) for r in (add_route, delete_route)] == [
            CqsKind.NON_IDEMPOTENT_COMMAND,
            CqsKind.IDEMPOTENT_COMMAND,
        ]
        assert [call.request.url.params["page-size"] for call in list_route.calls] == ["2", "2", "1"]
        await transport.aclose()


# --- models ---------------------------------------------------------------------------


def test_unknown_enum_values_fall_back_to_unknown() -> None:
    # Arrange
    payload = {
        "id": "i",
        "status": "ARCHIVED",
        "taxType": "REVERSE",
        "calculationType": "X",
        "items": [{"applyTaxes": "Y"}],
    }
    # Act
    details = InvoiceDetails.model_validate(payload)
    # Assert
    assert details.status is InvoiceStatus.UNKNOWN
    assert details.tax_type is InvoiceTaxType.UNKNOWN
    assert details.calculation_type is not None
    assert details.calculation_type.value == "UNKNOWN"
    assert details.items is not None
    assert details.items[0].apply_taxes is InvoiceApplyTaxes.UNKNOWN


async def test_async_client_exposes_the_three_invoice_resources() -> None:
    # Arrange
    client = _async_client()
    # Act
    workspace = client.workspace(WORKSPACE_ID)
    # Assert
    assert isinstance(workspace.invoices, AsyncInvoicesResource)
    assert isinstance(workspace.invoice_items, AsyncInvoiceItemsResource)
    assert isinstance(workspace.invoice_payments, AsyncInvoicePaymentsResource)
    await client.aclose()
