from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import cast

from clockify._pagination import Page
from clockify._pagination import apaginate
from clockify._pagination import paginate
from clockify._time import format_instant
from clockify.models.time_entry import TimeEntry
from clockify.models.time_entry import TimeEntryCreate
from clockify.models.time_entry import TimeEntryUpdate
from clockify.retry import CqsKind

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from collections.abc import Iterator
    from typing import Any

    from clockify._transport import AsyncTransport
    from clockify._transport import JSONValue
    from clockify._transport import Transport
    from clockify.ids import TimeEntryId
    from clockify.ids import UserId
    from clockify.ids import WorkspaceId
    from clockify.models.time_entry import TimeEntryFilter


@dataclass(slots=True, kw_only=True)
class _TimeEntryPaths:
    _workspace_id: WorkspaceId
    _page_size: int

    def _collection_path(self) -> str:
        return f"/workspaces/{self._workspace_id}/time-entries"

    def _item_path(self, time_entry_id: TimeEntryId | str) -> str:
        return f"{self._collection_path()}/{time_entry_id}"

    def _user_path(self, user_id: UserId | str) -> str:
        return f"/workspaces/{self._workspace_id}/user/{user_id}/time-entries"


class TimeEntriesResource(_TimeEntryPaths):
    # Time entries are read/listed under a user (.../user/{userId}/time-entries) but
    # get/update/delete operate on the entry directly (.../time-entries/{id}), so —
    # like TasksResource — this is hand-written rather than a WorkspaceResource
    # subclass: the base's uniform {path}/{id} shape does not fit both path families.
    def __init__(self, transport: Transport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # POST .../time-entries
    def create(self, payload: TimeEntryCreate) -> TimeEntry:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = self._transport.request("POST", self._collection_path(), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=body)
        return TimeEntry.model_validate(data)

    # DELETE .../time-entries/{id}
    def delete(self, time_entry_id: TimeEntryId | str) -> None:
        self._transport.request("DELETE", self._item_path(time_entry_id), kind=CqsKind.IDEMPOTENT_COMMAND)

    # GET .../time-entries/{id}
    def get(self, time_entry_id: TimeEntryId | str) -> TimeEntry:
        data = self._transport.request("GET", self._item_path(time_entry_id), kind=CqsKind.QUERY)
        return TimeEntry.model_validate(data)

    # GET .../user/{userId}/time-entries (auto-paginating)
    def list(self, user_id: UserId | str, *, entry_filter: TimeEntryFilter | None = None) -> Iterator[TimeEntry]:
        return paginate(lambda page: self.list_page(user_id, entry_filter=entry_filter, page=page))

    # GET .../user/{userId}/time-entries
    def list_page(
        self,
        user_id: UserId | str,
        *,
        entry_filter: TimeEntryFilter | None = None,
        page: int = 1,
        page_size: int | None = None,
    ) -> Page[TimeEntry]:
        resolved_page_size = self._page_size if page_size is None else page_size
        params: dict[str, Any] = dict(entry_filter.as_params()) if entry_filter is not None else {}
        params["page"] = page
        params["page-size"] = resolved_page_size
        data = self._transport.request("GET", self._user_path(user_id), kind=CqsKind.QUERY, params=params)
        items = [TimeEntry.model_validate(item) for item in cast("list[dict[str, Any]]", data)]
        return Page(items=items, page=page, page_size=resolved_page_size)

    # POST .../user/{userId}/time-entries
    def start(self, user_id: UserId | str, payload: TimeEntryCreate) -> TimeEntry:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = self._transport.request(
            "POST", self._user_path(user_id), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=body
        )
        return TimeEntry.model_validate(data)

    # PATCH .../user/{userId}/time-entries
    def stop(self, user_id: UserId | str, *, end: datetime.datetime | None = None) -> TimeEntry:
        # Classified non-idempotent, not idempotent, despite the PATCH verb: a retried
        # stop against a stale in-flight timer could end a different entry than the one
        # the caller intended (see retry.py's CQS-aware retry rule).
        resolved_end = end if end is not None else datetime.datetime.now(datetime.UTC)
        body: dict[str, JSONValue] = {"end": format_instant(resolved_end)}
        data = self._transport.request(
            "PATCH", self._user_path(user_id), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=body
        )
        return TimeEntry.model_validate(data)

    # PUT .../time-entries/{id}
    def update(self, time_entry_id: TimeEntryId | str, payload: TimeEntryUpdate) -> TimeEntry:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = self._transport.request(
            "PUT", self._item_path(time_entry_id), kind=CqsKind.IDEMPOTENT_COMMAND, json=body
        )
        return TimeEntry.model_validate(data)


class AsyncTimeEntriesResource(_TimeEntryPaths):
    def __init__(self, transport: AsyncTransport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # POST .../time-entries
    async def create(self, payload: TimeEntryCreate) -> TimeEntry:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = await self._transport.request(
            "POST", self._collection_path(), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=body
        )
        return TimeEntry.model_validate(data)

    # DELETE .../time-entries/{id}
    async def delete(self, time_entry_id: TimeEntryId | str) -> None:
        await self._transport.request("DELETE", self._item_path(time_entry_id), kind=CqsKind.IDEMPOTENT_COMMAND)

    # GET .../time-entries/{id}
    async def get(self, time_entry_id: TimeEntryId | str) -> TimeEntry:
        data = await self._transport.request("GET", self._item_path(time_entry_id), kind=CqsKind.QUERY)
        return TimeEntry.model_validate(data)

    # GET .../user/{userId}/time-entries (auto-paginating)
    def list(self, user_id: UserId | str, *, entry_filter: TimeEntryFilter | None = None) -> AsyncIterator[TimeEntry]:
        return apaginate(lambda page: self.list_page(user_id, entry_filter=entry_filter, page=page))

    # GET .../user/{userId}/time-entries
    async def list_page(
        self,
        user_id: UserId | str,
        *,
        entry_filter: TimeEntryFilter | None = None,
        page: int = 1,
        page_size: int | None = None,
    ) -> Page[TimeEntry]:
        resolved_page_size = self._page_size if page_size is None else page_size
        params: dict[str, Any] = dict(entry_filter.as_params()) if entry_filter is not None else {}
        params["page"] = page
        params["page-size"] = resolved_page_size
        data = await self._transport.request("GET", self._user_path(user_id), kind=CqsKind.QUERY, params=params)
        items = [TimeEntry.model_validate(item) for item in cast("list[dict[str, Any]]", data)]
        return Page(items=items, page=page, page_size=resolved_page_size)

    # POST .../user/{userId}/time-entries
    async def start(self, user_id: UserId | str, payload: TimeEntryCreate) -> TimeEntry:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = await self._transport.request(
            "POST", self._user_path(user_id), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=body
        )
        return TimeEntry.model_validate(data)

    # PATCH .../user/{userId}/time-entries
    async def stop(self, user_id: UserId | str, *, end: datetime.datetime | None = None) -> TimeEntry:
        # Non-idempotent despite the PATCH verb, same as the sync client (see retry.py).
        resolved_end = end if end is not None else datetime.datetime.now(datetime.UTC)
        body: dict[str, JSONValue] = {"end": format_instant(resolved_end)}
        data = await self._transport.request(
            "PATCH", self._user_path(user_id), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=body
        )
        return TimeEntry.model_validate(data)

    # PUT .../time-entries/{id}
    async def update(self, time_entry_id: TimeEntryId | str, payload: TimeEntryUpdate) -> TimeEntry:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = await self._transport.request(
            "PUT", self._item_path(time_entry_id), kind=CqsKind.IDEMPOTENT_COMMAND, json=body
        )
        return TimeEntry.model_validate(data)
