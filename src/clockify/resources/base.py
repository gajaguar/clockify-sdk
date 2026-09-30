from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import ClassVar
from typing import cast

from pydantic import BaseModel

from clockify._pagination import Page
from clockify._pagination import apaginate
from clockify._pagination import paginate
from clockify.models.base import ClockifyModel
from clockify.retry import CqsKind

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from collections.abc import Iterator
    from typing import Any

    from clockify._transport import AsyncTransport
    from clockify._transport import Transport
    from clockify.ids import WorkspaceId


@dataclass(slots=True, kw_only=True)
class _WorkspacePaths:
    _path: ClassVar[str]

    _workspace_id: WorkspaceId
    _page_size: int

    def _collection_path(self) -> str:
        return f"/workspaces/{self._workspace_id}{self._path}"

    def _item_path(self, item_id: str) -> str:
        return f"{self._collection_path()}/{item_id}"


class WorkspaceResource[ReadT: ClockifyModel, CreateT: BaseModel, UpdateT: BaseModel](_WorkspacePaths):
    _read_model: type[ReadT]

    def __init__(self, transport: Transport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # POST {path}
    def create(self, payload: CreateT) -> ReadT:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = self._transport.request("POST", self._collection_path(), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=body)
        return self._read_model.model_validate(data)

    # DELETE {path}/{id}
    def delete(self, item_id: str) -> None:
        self._transport.request("DELETE", self._item_path(item_id), kind=CqsKind.IDEMPOTENT_COMMAND)

    # GET {path}/{id}
    def get(self, item_id: str) -> ReadT:
        data = self._transport.request("GET", self._item_path(item_id), kind=CqsKind.QUERY)
        return self._read_model.model_validate(data)

    # GET {path} (auto-paginating)
    def list(self) -> Iterator[ReadT]:
        return paginate(lambda page: self.list_page(page=page))

    # GET {path}
    def list_page(self, *, page: int = 1, page_size: int | None = None) -> Page[ReadT]:
        resolved_page_size = self._page_size if page_size is None else page_size
        data = self._transport.request(
            "GET",
            self._collection_path(),
            kind=CqsKind.QUERY,
            params={"page": page, "page-size": resolved_page_size},
        )
        items = [self._read_model.model_validate(item) for item in cast("list[dict[str, Any]]", data)]
        return Page(items=items, page=page, page_size=resolved_page_size)

    # PUT {path}/{id}
    def update(self, item_id: str, payload: UpdateT) -> ReadT:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = self._transport.request("PUT", self._item_path(item_id), kind=CqsKind.IDEMPOTENT_COMMAND, json=body)
        return self._read_model.model_validate(data)


class AsyncWorkspaceResource[ReadT: ClockifyModel, CreateT: BaseModel, UpdateT: BaseModel](_WorkspacePaths):
    _read_model: type[ReadT]

    def __init__(self, transport: AsyncTransport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # POST {path}
    async def create(self, payload: CreateT) -> ReadT:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = await self._transport.request(
            "POST", self._collection_path(), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=body
        )
        return self._read_model.model_validate(data)

    # DELETE {path}/{id}
    async def delete(self, item_id: str) -> None:
        await self._transport.request("DELETE", self._item_path(item_id), kind=CqsKind.IDEMPOTENT_COMMAND)

    # GET {path}/{id}
    async def get(self, item_id: str) -> ReadT:
        data = await self._transport.request("GET", self._item_path(item_id), kind=CqsKind.QUERY)
        return self._read_model.model_validate(data)

    # GET {path} (auto-paginating)
    def list(self) -> AsyncIterator[ReadT]:
        return apaginate(lambda page: self.list_page(page=page))

    # GET {path}
    async def list_page(self, *, page: int = 1, page_size: int | None = None) -> Page[ReadT]:
        resolved_page_size = self._page_size if page_size is None else page_size
        data = await self._transport.request(
            "GET",
            self._collection_path(),
            kind=CqsKind.QUERY,
            params={"page": page, "page-size": resolved_page_size},
        )
        items = [self._read_model.model_validate(item) for item in cast("list[dict[str, Any]]", data)]
        return Page(items=items, page=page, page_size=resolved_page_size)

    # PUT {path}/{id}
    async def update(self, item_id: str, payload: UpdateT) -> ReadT:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = await self._transport.request(
            "PUT", self._item_path(item_id), kind=CqsKind.IDEMPOTENT_COMMAND, json=body
        )
        return self._read_model.model_validate(data)
