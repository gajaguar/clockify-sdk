from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Final
from typing import override

from clockify._pagination import Page
from clockify._pagination import apaginate
from clockify._pagination import paginate
from clockify._transport import Multipart
from clockify.models.expense import Expense
from clockify.models.expense import ExpenseCategory
from clockify.models.expense import ExpenseCategoryCreate
from clockify.models.expense import ExpenseCategoryList
from clockify.models.expense import ExpenseCategoryUpdate
from clockify.models.expense import ExpenseDetails
from clockify.models.expense import ExpenseList
from clockify.resources.base import AsyncWorkspaceResource
from clockify.resources.base import WorkspaceResource
from clockify.retry import CqsKind

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from collections.abc import Iterator

    from clockify._transport import AsyncTransport
    from clockify._transport import MultipartPart
    from clockify._transport import Transport
    from clockify.ids import ExpenseCategoryId
    from clockify.ids import ExpenseId
    from clockify.ids import UserId
    from clockify.ids import WorkspaceId
    from clockify.models.expense import ExpenseCategoryFilter
    from clockify.models.expense import ExpenseCategoryStatusUpdate
    from clockify.models.expense import ExpenseCreate
    from clockify.models.expense import ExpenseUpdate

_NO_CATEGORY_GET: Final = "Clockify has no endpoint to read one expense category; use list()."


def _form_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _form_parts(payload: ExpenseCreate | ExpenseUpdate) -> Multipart:
    fields = payload.model_dump(mode="json", by_alias=True, exclude_unset=True, exclude={"file"})
    parts: list[tuple[str, MultipartPart]] = []
    for name, value in fields.items():
        # A list becomes one part per item, which is how a multipart form repeats a field.
        values = value if isinstance(value, list) else [value]
        parts.extend((name, (None, _form_value(item).encode(), None)) for item in values)
    if payload.file is not None:
        parts.append(("file", (payload.file.filename, payload.file.content, payload.file.content_type)))
    return Multipart(tuple(parts))


@dataclass(slots=True, kw_only=True)
class _ExpensePaths:
    _workspace_id: WorkspaceId
    _page_size: int

    def _collection_path(self) -> str:
        return f"/workspaces/{self._workspace_id}/expenses"

    def _item_path(self, expense_id: ExpenseId | str) -> str:
        return f"{self._collection_path()}/{expense_id}"

    def _list_params(self, user_id: UserId | str | None, page: int, page_size: int | None) -> dict[str, Any]:
        params: dict[str, Any] = {} if user_id is None else {"user-id": str(user_id)}
        params["page"] = page
        params["page-size"] = self._page_size if page_size is None else page_size
        return params


def _details(data: object) -> list[ExpenseDetails]:
    wrapper = ExpenseList.model_validate(data).expenses
    return [] if wrapper is None or wrapper.expenses is None else wrapper.expenses


class ExpensesResource(_ExpensePaths):
    # Hand-written rather than a WorkspaceResource subclass: the list is wrapped with
    # totals and carries a different model than get/create/update, and the writes are
    # multipart rather than JSON.
    def __init__(self, transport: Transport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # GET .../expenses (auto-paginating)
    def list(self, *, user_id: UserId | str | None = None) -> Iterator[ExpenseDetails]:
        return paginate(lambda page: self.list_page(user_id=user_id, page=page))

    # GET .../expenses
    def list_page(
        self, *, user_id: UserId | str | None = None, page: int = 1, page_size: int | None = None
    ) -> Page[ExpenseDetails]:
        params = self._list_params(user_id, page, page_size)
        data = self._transport.request("GET", self._collection_path(), kind=CqsKind.QUERY, params=params)
        return Page(items=_details(data), page=page, page_size=params["page-size"])

    # GET .../expenses/{id}
    def get(self, expense_id: ExpenseId | str) -> Expense:
        data = self._transport.request("GET", self._item_path(expense_id), kind=CqsKind.QUERY)
        return Expense.model_validate(data)

    # POST .../expenses (multipart/form-data)
    def create(self, payload: ExpenseCreate) -> Expense:
        data = self._transport.request(
            "POST", self._collection_path(), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=_form_parts(payload)
        )
        return Expense.model_validate(data)

    # PUT .../expenses/{id} (multipart/form-data)
    def update(self, expense_id: ExpenseId | str, payload: ExpenseUpdate) -> Expense:
        data = self._transport.request(
            "PUT", self._item_path(expense_id), kind=CqsKind.IDEMPOTENT_COMMAND, json=_form_parts(payload)
        )
        return Expense.model_validate(data)

    # DELETE .../expenses/{id}
    def delete(self, expense_id: ExpenseId | str) -> None:
        self._transport.request("DELETE", self._item_path(expense_id), kind=CqsKind.IDEMPOTENT_COMMAND)


class AsyncExpensesResource(_ExpensePaths):
    def __init__(self, transport: AsyncTransport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # GET .../expenses (auto-paginating)
    def list(self, *, user_id: UserId | str | None = None) -> AsyncIterator[ExpenseDetails]:
        return apaginate(lambda page: self.list_page(user_id=user_id, page=page))

    # GET .../expenses
    async def list_page(
        self, *, user_id: UserId | str | None = None, page: int = 1, page_size: int | None = None
    ) -> Page[ExpenseDetails]:
        params = self._list_params(user_id, page, page_size)
        data = await self._transport.request("GET", self._collection_path(), kind=CqsKind.QUERY, params=params)
        return Page(items=_details(data), page=page, page_size=params["page-size"])

    # GET .../expenses/{id}
    async def get(self, expense_id: ExpenseId | str) -> Expense:
        data = await self._transport.request("GET", self._item_path(expense_id), kind=CqsKind.QUERY)
        return Expense.model_validate(data)

    # POST .../expenses (multipart/form-data)
    async def create(self, payload: ExpenseCreate) -> Expense:
        data = await self._transport.request(
            "POST", self._collection_path(), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=_form_parts(payload)
        )
        return Expense.model_validate(data)

    # PUT .../expenses/{id} (multipart/form-data)
    async def update(self, expense_id: ExpenseId | str, payload: ExpenseUpdate) -> Expense:
        data = await self._transport.request(
            "PUT", self._item_path(expense_id), kind=CqsKind.IDEMPOTENT_COMMAND, json=_form_parts(payload)
        )
        return Expense.model_validate(data)

    # DELETE .../expenses/{id}
    async def delete(self, expense_id: ExpenseId | str) -> None:
        await self._transport.request("DELETE", self._item_path(expense_id), kind=CqsKind.IDEMPOTENT_COMMAND)


def _category_params(category_filter: ExpenseCategoryFilter | None, page: int, page_size: int) -> dict[str, Any]:
    params: dict[str, Any] = dict(category_filter.as_params()) if category_filter is not None else {}
    params["page"] = page
    params["page-size"] = page_size
    return params


def _categories(data: object) -> list[ExpenseCategory]:
    return ExpenseCategoryList.model_validate(data).categories or []


class ExpenseCategoriesResource(WorkspaceResource[ExpenseCategory, ExpenseCategoryCreate, ExpenseCategoryUpdate]):
    _path = "/expenses/categories"
    _read_model = ExpenseCategory

    # GET {path} (auto-paginating)
    @override
    def list(self, *, category_filter: ExpenseCategoryFilter | None = None) -> Iterator[ExpenseCategory]:
        return paginate(lambda page: self.list_page(category_filter=category_filter, page=page))

    # GET {path}
    @override
    def list_page(
        self, *, category_filter: ExpenseCategoryFilter | None = None, page: int = 1, page_size: int | None = None
    ) -> Page[ExpenseCategory]:
        resolved_page_size = self._page_size if page_size is None else page_size
        params = _category_params(category_filter, page, resolved_page_size)
        data = self._transport.request("GET", self._collection_path(), kind=CqsKind.QUERY, params=params)
        return Page(items=_categories(data), page=page, page_size=resolved_page_size)

    # Clockify has no GET for a single category.
    @override
    def get(self, item_id: str) -> ExpenseCategory:
        del item_id
        raise NotImplementedError(_NO_CATEGORY_GET)

    # PATCH {path}/{id}/status
    def update_status(
        self, category_id: ExpenseCategoryId | str, payload: ExpenseCategoryStatusUpdate
    ) -> ExpenseCategory:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = self._transport.request(
            "PATCH", f"{self._item_path(category_id)}/status", kind=CqsKind.IDEMPOTENT_COMMAND, json=body
        )
        return ExpenseCategory.model_validate(data)


class AsyncExpenseCategoriesResource(
    AsyncWorkspaceResource[ExpenseCategory, ExpenseCategoryCreate, ExpenseCategoryUpdate]
):
    _path = "/expenses/categories"
    _read_model = ExpenseCategory

    # GET {path} (auto-paginating)
    @override
    def list(self, *, category_filter: ExpenseCategoryFilter | None = None) -> AsyncIterator[ExpenseCategory]:
        return apaginate(lambda page: self.list_page(category_filter=category_filter, page=page))

    # GET {path}
    @override
    async def list_page(
        self, *, category_filter: ExpenseCategoryFilter | None = None, page: int = 1, page_size: int | None = None
    ) -> Page[ExpenseCategory]:
        resolved_page_size = self._page_size if page_size is None else page_size
        params = _category_params(category_filter, page, resolved_page_size)
        data = await self._transport.request("GET", self._collection_path(), kind=CqsKind.QUERY, params=params)
        return Page(items=_categories(data), page=page, page_size=resolved_page_size)

    # Clockify has no GET for a single category.
    @override
    async def get(self, item_id: str) -> ExpenseCategory:
        del item_id
        raise NotImplementedError(_NO_CATEGORY_GET)

    # PATCH {path}/{id}/status
    async def update_status(
        self, category_id: ExpenseCategoryId | str, payload: ExpenseCategoryStatusUpdate
    ) -> ExpenseCategory:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = await self._transport.request(
            "PATCH", f"{self._item_path(category_id)}/status", kind=CqsKind.IDEMPOTENT_COMMAND, json=body
        )
        return ExpenseCategory.model_validate(data)
