from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from clockify._pagination import Page
from clockify._pagination import apaginate
from clockify._pagination import paginate
from clockify.models.invoice import CreatedInvoice
from clockify.models.invoice import Invoice
from clockify.models.invoice import InvoiceDetails
from clockify.models.invoice import InvoiceInfo
from clockify.models.invoice import InvoiceInfoList
from clockify.models.invoice import InvoiceList
from clockify.models.invoice import InvoicePayment
from clockify.models.invoice import InvoiceSettings
from clockify.retry import CqsKind

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from collections.abc import Iterator

    from pydantic import BaseModel

    from clockify._transport import AsyncTransport
    from clockify._transport import Transport
    from clockify.ids import InvoiceId
    from clockify.ids import InvoicePaymentId
    from clockify.ids import WorkspaceId
    from clockify.models.invoice import InvoiceCreate
    from clockify.models.invoice import InvoiceFilter
    from clockify.models.invoice import InvoiceItemCreate
    from clockify.models.invoice import InvoiceItemsImport
    from clockify.models.invoice import InvoicePaymentCreate
    from clockify.models.invoice import InvoiceSearch
    from clockify.models.invoice import InvoiceSettingsUpdate
    from clockify.models.invoice import InvoiceStatusUpdate
    from clockify.models.invoice import InvoiceUpdate


def _body(payload: BaseModel) -> dict[str, Any]:
    return payload.model_dump(mode="json", by_alias=True, exclude_unset=True)


def _invoices(data: object) -> list[Invoice]:
    return InvoiceList.model_validate(data).invoices or []


def _infos(data: object) -> list[InvoiceInfo]:
    return InvoiceInfoList.model_validate(data).invoices or []


def _payments(data: object) -> list[InvoicePayment]:
    return [InvoicePayment.model_validate(item) for item in cast("list[dict[str, Any]]", data)]


@dataclass(slots=True, kw_only=True)
class _InvoicePaths:
    _workspace_id: WorkspaceId
    _page_size: int

    def _collection_path(self) -> str:
        return f"/workspaces/{self._workspace_id}/invoices"

    def _item_path(self, invoice_id: InvoiceId | str) -> str:
        return f"{self._collection_path()}/{invoice_id}"

    def _search_path(self) -> str:
        return f"{self._collection_path()}/info"

    def _settings_path(self) -> str:
        return f"{self._collection_path()}/settings"

    def _items_path(self, invoice_id: InvoiceId | str) -> str:
        return f"{self._item_path(invoice_id)}/items"

    def _payments_path(self, invoice_id: InvoiceId | str) -> str:
        return f"{self._item_path(invoice_id)}/payments"

    def _list_params(self, invoice_filter: InvoiceFilter | None, page: int, page_size: int | None) -> dict[str, Any]:
        params: dict[str, Any] = dict(invoice_filter.as_params()) if invoice_filter is not None else {}
        params["page"] = page
        params["page-size"] = self._page_size if page_size is None else page_size
        return params

    def _page_params(self, page: int, page_size: int | None) -> dict[str, Any]:
        return {"page": page, "page-size": self._page_size if page_size is None else page_size}

    def _search_body(self, search: InvoiceSearch | None, page: int, page_size: int | None) -> dict[str, Any]:
        body: dict[str, Any] = _body(search) if search is not None else {}
        body["page"] = page
        body["pageSize"] = self._page_size if page_size is None else page_size
        return body


class InvoicesResource(_InvoicePaths):
    # Hand-written rather than a WorkspaceResource subclass: the list is wrapped with a
    # total, items and payments hang off an invoice, and the export is a file.
    def __init__(self, transport: Transport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # GET .../invoices (auto-paginating)
    def list(self, *, invoice_filter: InvoiceFilter | None = None) -> Iterator[Invoice]:
        return paginate(lambda page: self.list_page(invoice_filter=invoice_filter, page=page))

    # GET .../invoices
    def list_page(
        self, *, invoice_filter: InvoiceFilter | None = None, page: int = 1, page_size: int | None = None
    ) -> Page[Invoice]:
        params = self._list_params(invoice_filter, page, page_size)
        data = self._transport.request("GET", self._collection_path(), kind=CqsKind.QUERY, params=params)
        return Page(items=_invoices(data), page=page, page_size=params["page-size"])

    # POST .../invoices/info (auto-paginating; a query despite the verb)
    def search(self, search: InvoiceSearch | None = None) -> Iterator[InvoiceInfo]:
        return paginate(lambda page: self.search_page(search, page=page))

    # POST .../invoices/info
    def search_page(
        self, search: InvoiceSearch | None = None, *, page: int = 1, page_size: int | None = None
    ) -> Page[InvoiceInfo]:
        body = self._search_body(search, page, page_size)
        data = self._transport.request("POST", self._search_path(), kind=CqsKind.QUERY, json=body)
        return Page(items=_infos(data), page=page, page_size=body["pageSize"])

    # GET .../invoices/{id}
    def get(self, invoice_id: InvoiceId | str) -> InvoiceDetails:
        data = self._transport.request("GET", self._item_path(invoice_id), kind=CqsKind.QUERY)
        return InvoiceDetails.model_validate(data)

    # POST .../invoices
    def create(self, payload: InvoiceCreate) -> CreatedInvoice:
        data = self._transport.request(
            "POST", self._collection_path(), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=_body(payload)
        )
        return CreatedInvoice.model_validate(data)

    # PUT .../invoices/{id}
    def update(self, invoice_id: InvoiceId | str, payload: InvoiceUpdate) -> InvoiceDetails:
        data = self._transport.request(
            "PUT", self._item_path(invoice_id), kind=CqsKind.IDEMPOTENT_COMMAND, json=_body(payload)
        )
        return InvoiceDetails.model_validate(data)

    # DELETE .../invoices/{id}
    def delete(self, invoice_id: InvoiceId | str) -> None:
        self._transport.request("DELETE", self._item_path(invoice_id), kind=CqsKind.IDEMPOTENT_COMMAND)

    # POST .../invoices/{id}/duplicate
    def duplicate(self, invoice_id: InvoiceId | str) -> InvoiceDetails:
        data = self._transport.request(
            "POST", f"{self._item_path(invoice_id)}/duplicate", kind=CqsKind.NON_IDEMPOTENT_COMMAND
        )
        return InvoiceDetails.model_validate(data)

    # GET .../invoices/{id}/export (the file, as raw bytes)
    def export(self, invoice_id: InvoiceId | str, *, user_locale: str) -> bytes:
        return self._transport.request_bytes(
            "GET",
            f"{self._item_path(invoice_id)}/export",
            kind=CqsKind.QUERY,
            params={"userLocale": user_locale},
        )

    # PATCH .../invoices/{id}/status
    def update_status(self, invoice_id: InvoiceId | str, payload: InvoiceStatusUpdate) -> None:
        self._transport.request(
            "PATCH", f"{self._item_path(invoice_id)}/status", kind=CqsKind.IDEMPOTENT_COMMAND, json=_body(payload)
        )

    # GET .../invoices/settings
    def get_settings(self) -> InvoiceSettings:
        data = self._transport.request("GET", self._settings_path(), kind=CqsKind.QUERY)
        return InvoiceSettings.model_validate(data)

    # PUT .../invoices/settings
    def update_settings(self, payload: InvoiceSettingsUpdate) -> InvoiceSettings:
        data = self._transport.request(
            "PUT", self._settings_path(), kind=CqsKind.IDEMPOTENT_COMMAND, json=_body(payload)
        )
        return InvoiceSettings.model_validate(data)


class InvoiceItemsResource(_InvoicePaths):
    def __init__(self, transport: Transport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # POST .../invoices/{id}/items
    def add(self, invoice_id: InvoiceId | str, payload: InvoiceItemCreate) -> InvoiceDetails:
        data = self._transport.request(
            "POST", self._items_path(invoice_id), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=_body(payload)
        )
        return InvoiceDetails.model_validate(data)

    # POST .../invoices/{id}/items/import
    def import_entries(self, invoice_id: InvoiceId | str, payload: InvoiceItemsImport) -> InvoiceDetails:
        data = self._transport.request(
            "POST", f"{self._items_path(invoice_id)}/import", kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=_body(payload)
        )
        return InvoiceDetails.model_validate(data)

    # DELETE .../invoices/{id}/items/{order} (items are renumbered, so a repeat deletes another)
    def delete(self, invoice_id: InvoiceId | str, order: int) -> InvoiceDetails:
        data = self._transport.request(
            "DELETE", f"{self._items_path(invoice_id)}/{order}", kind=CqsKind.NON_IDEMPOTENT_COMMAND
        )
        return InvoiceDetails.model_validate(data)


class InvoicePaymentsResource(_InvoicePaths):
    def __init__(self, transport: Transport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # GET .../invoices/{id}/payments (auto-paginating)
    def list(self, invoice_id: InvoiceId | str) -> Iterator[InvoicePayment]:
        return paginate(lambda page: self.list_page(invoice_id, page=page))

    # GET .../invoices/{id}/payments
    def list_page(
        self, invoice_id: InvoiceId | str, *, page: int = 1, page_size: int | None = None
    ) -> Page[InvoicePayment]:
        params = self._page_params(page, page_size)
        data = self._transport.request("GET", self._payments_path(invoice_id), kind=CqsKind.QUERY, params=params)
        return Page(items=_payments(data), page=page, page_size=params["page-size"])

    # POST .../invoices/{id}/payments
    def add(self, invoice_id: InvoiceId | str, payload: InvoicePaymentCreate) -> InvoiceDetails:
        data = self._transport.request(
            "POST", self._payments_path(invoice_id), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=_body(payload)
        )
        return InvoiceDetails.model_validate(data)

    # DELETE .../invoices/{id}/payments/{paymentId}
    def delete(self, invoice_id: InvoiceId | str, payment_id: InvoicePaymentId | str) -> InvoiceDetails:
        data = self._transport.request(
            "DELETE", f"{self._payments_path(invoice_id)}/{payment_id}", kind=CqsKind.IDEMPOTENT_COMMAND
        )
        return InvoiceDetails.model_validate(data)


class AsyncInvoicesResource(_InvoicePaths):
    def __init__(self, transport: AsyncTransport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # GET .../invoices (auto-paginating)
    def list(self, *, invoice_filter: InvoiceFilter | None = None) -> AsyncIterator[Invoice]:
        return apaginate(lambda page: self.list_page(invoice_filter=invoice_filter, page=page))

    # GET .../invoices
    async def list_page(
        self, *, invoice_filter: InvoiceFilter | None = None, page: int = 1, page_size: int | None = None
    ) -> Page[Invoice]:
        params = self._list_params(invoice_filter, page, page_size)
        data = await self._transport.request("GET", self._collection_path(), kind=CqsKind.QUERY, params=params)
        return Page(items=_invoices(data), page=page, page_size=params["page-size"])

    # POST .../invoices/info (auto-paginating; a query despite the verb)
    def search(self, search: InvoiceSearch | None = None) -> AsyncIterator[InvoiceInfo]:
        return apaginate(lambda page: self.search_page(search, page=page))

    # POST .../invoices/info
    async def search_page(
        self, search: InvoiceSearch | None = None, *, page: int = 1, page_size: int | None = None
    ) -> Page[InvoiceInfo]:
        body = self._search_body(search, page, page_size)
        data = await self._transport.request("POST", self._search_path(), kind=CqsKind.QUERY, json=body)
        return Page(items=_infos(data), page=page, page_size=body["pageSize"])

    # GET .../invoices/{id}
    async def get(self, invoice_id: InvoiceId | str) -> InvoiceDetails:
        data = await self._transport.request("GET", self._item_path(invoice_id), kind=CqsKind.QUERY)
        return InvoiceDetails.model_validate(data)

    # POST .../invoices
    async def create(self, payload: InvoiceCreate) -> CreatedInvoice:
        data = await self._transport.request(
            "POST", self._collection_path(), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=_body(payload)
        )
        return CreatedInvoice.model_validate(data)

    # PUT .../invoices/{id}
    async def update(self, invoice_id: InvoiceId | str, payload: InvoiceUpdate) -> InvoiceDetails:
        data = await self._transport.request(
            "PUT", self._item_path(invoice_id), kind=CqsKind.IDEMPOTENT_COMMAND, json=_body(payload)
        )
        return InvoiceDetails.model_validate(data)

    # DELETE .../invoices/{id}
    async def delete(self, invoice_id: InvoiceId | str) -> None:
        await self._transport.request("DELETE", self._item_path(invoice_id), kind=CqsKind.IDEMPOTENT_COMMAND)

    # POST .../invoices/{id}/duplicate
    async def duplicate(self, invoice_id: InvoiceId | str) -> InvoiceDetails:
        data = await self._transport.request(
            "POST", f"{self._item_path(invoice_id)}/duplicate", kind=CqsKind.NON_IDEMPOTENT_COMMAND
        )
        return InvoiceDetails.model_validate(data)

    # GET .../invoices/{id}/export (the file, as raw bytes)
    async def export(self, invoice_id: InvoiceId | str, *, user_locale: str) -> bytes:
        return await self._transport.request_bytes(
            "GET",
            f"{self._item_path(invoice_id)}/export",
            kind=CqsKind.QUERY,
            params={"userLocale": user_locale},
        )

    # PATCH .../invoices/{id}/status
    async def update_status(self, invoice_id: InvoiceId | str, payload: InvoiceStatusUpdate) -> None:
        await self._transport.request(
            "PATCH", f"{self._item_path(invoice_id)}/status", kind=CqsKind.IDEMPOTENT_COMMAND, json=_body(payload)
        )

    # GET .../invoices/settings
    async def get_settings(self) -> InvoiceSettings:
        data = await self._transport.request("GET", self._settings_path(), kind=CqsKind.QUERY)
        return InvoiceSettings.model_validate(data)

    # PUT .../invoices/settings
    async def update_settings(self, payload: InvoiceSettingsUpdate) -> InvoiceSettings:
        data = await self._transport.request(
            "PUT", self._settings_path(), kind=CqsKind.IDEMPOTENT_COMMAND, json=_body(payload)
        )
        return InvoiceSettings.model_validate(data)


class AsyncInvoiceItemsResource(_InvoicePaths):
    def __init__(self, transport: AsyncTransport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # POST .../invoices/{id}/items
    async def add(self, invoice_id: InvoiceId | str, payload: InvoiceItemCreate) -> InvoiceDetails:
        data = await self._transport.request(
            "POST", self._items_path(invoice_id), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=_body(payload)
        )
        return InvoiceDetails.model_validate(data)

    # POST .../invoices/{id}/items/import
    async def import_entries(self, invoice_id: InvoiceId | str, payload: InvoiceItemsImport) -> InvoiceDetails:
        data = await self._transport.request(
            "POST", f"{self._items_path(invoice_id)}/import", kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=_body(payload)
        )
        return InvoiceDetails.model_validate(data)

    # DELETE .../invoices/{id}/items/{order} (items are renumbered, so a repeat deletes another)
    async def delete(self, invoice_id: InvoiceId | str, order: int) -> InvoiceDetails:
        data = await self._transport.request(
            "DELETE", f"{self._items_path(invoice_id)}/{order}", kind=CqsKind.NON_IDEMPOTENT_COMMAND
        )
        return InvoiceDetails.model_validate(data)


class AsyncInvoicePaymentsResource(_InvoicePaths):
    def __init__(self, transport: AsyncTransport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # GET .../invoices/{id}/payments (auto-paginating)
    def list(self, invoice_id: InvoiceId | str) -> AsyncIterator[InvoicePayment]:
        return apaginate(lambda page: self.list_page(invoice_id, page=page))

    # GET .../invoices/{id}/payments
    async def list_page(
        self, invoice_id: InvoiceId | str, *, page: int = 1, page_size: int | None = None
    ) -> Page[InvoicePayment]:
        params = self._page_params(page, page_size)
        data = await self._transport.request("GET", self._payments_path(invoice_id), kind=CqsKind.QUERY, params=params)
        return Page(items=_payments(data), page=page, page_size=params["page-size"])

    # POST .../invoices/{id}/payments
    async def add(self, invoice_id: InvoiceId | str, payload: InvoicePaymentCreate) -> InvoiceDetails:
        data = await self._transport.request(
            "POST", self._payments_path(invoice_id), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=_body(payload)
        )
        return InvoiceDetails.model_validate(data)

    # DELETE .../invoices/{id}/payments/{paymentId}
    async def delete(self, invoice_id: InvoiceId | str, payment_id: InvoicePaymentId | str) -> InvoiceDetails:
        data = await self._transport.request(
            "DELETE", f"{self._payments_path(invoice_id)}/{payment_id}", kind=CqsKind.IDEMPOTENT_COMMAND
        )
        return InvoiceDetails.model_validate(data)
