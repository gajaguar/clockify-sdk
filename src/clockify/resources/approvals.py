from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import cast

from clockify._pagination import Page
from clockify._pagination import apaginate
from clockify._pagination import paginate
from clockify.models.approval import ApprovalDetails
from clockify.models.approval import ApprovalRequest
from clockify.retry import CqsKind

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from collections.abc import Iterator
    from typing import Any

    from clockify._transport import AsyncTransport
    from clockify._transport import Transport
    from clockify.ids import ApprovalRequestId
    from clockify.ids import UserId
    from clockify.ids import WorkspaceId
    from clockify.models.approval import ApprovalRequestCreate
    from clockify.models.approval import ApprovalRequestFilter
    from clockify.models.approval import ApprovalRequestResubmit
    from clockify.models.approval import ApprovalRequestType
    from clockify.models.approval import ApprovalRequestUpdate


def _time_view_params(time_view_mode: str | None) -> dict[str, str] | None:
    return None if time_view_mode is None else {"timeViewMode": time_view_mode}


@dataclass(slots=True, kw_only=True)
class _ApprovalPaths:
    _workspace_id: WorkspaceId
    _page_size: int

    def _collection_path(self) -> str:
        return f"/workspaces/{self._workspace_id}/approval-requests"

    def _item_path(self, approval_request_id: ApprovalRequestId | str) -> str:
        return f"{self._collection_path()}/{approval_request_id}"

    def _type_path(self, approval_type: ApprovalRequestType | str) -> str:
        return f"{self._collection_path()}/{approval_type}"

    def _user_type_path(self, user_id: UserId | str, approval_type: ApprovalRequestType | str) -> str:
        return f"{self._collection_path()}/users/{user_id}/{approval_type}"

    def _resubmit_path(self) -> str:
        return f"{self._collection_path()}/resubmit-entries-for-approval"

    def _list_params(
        self, request_filter: ApprovalRequestFilter | None, page: int, page_size: int | None
    ) -> dict[str, Any]:
        params: dict[str, Any] = dict(request_filter.as_params()) if request_filter is not None else {}
        params["page"] = page
        params["page-size"] = self._page_size if page_size is None else page_size
        return params


class ApprovalsResource(_ApprovalPaths):
    # Hand-written rather than a WorkspaceResource subclass: approvals have no get or
    # delete, and submit/resubmit are verbs the base's uniform CRUD shape does not cover.
    def __init__(self, transport: Transport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # GET .../approval-requests (auto-paginating)
    def list(self, *, request_filter: ApprovalRequestFilter | None = None) -> Iterator[ApprovalDetails]:
        return paginate(lambda page: self.list_page(request_filter=request_filter, page=page))

    # GET .../approval-requests
    def list_page(
        self, *, request_filter: ApprovalRequestFilter | None = None, page: int = 1, page_size: int | None = None
    ) -> Page[ApprovalDetails]:
        params = self._list_params(request_filter, page, page_size)
        data = self._transport.request("GET", self._collection_path(), kind=CqsKind.QUERY, params=params)
        items = [ApprovalDetails.model_validate(item) for item in cast("list[dict[str, Any]]", data)]
        return Page(items=items, page=page, page_size=params["page-size"])

    # POST .../approval-requests/{type}
    def submit(
        self,
        approval_type: ApprovalRequestType | str,
        payload: ApprovalRequestCreate,
        *,
        time_view_mode: str | None = None,
    ) -> ApprovalRequest:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = self._transport.request(
            "POST",
            self._type_path(approval_type),
            kind=CqsKind.NON_IDEMPOTENT_COMMAND,
            params=_time_view_params(time_view_mode),
            json=body,
        )
        return ApprovalRequest.model_validate(data)

    # POST .../approval-requests/users/{userId}/{type}
    def submit_for_user(
        self,
        user_id: UserId | str,
        approval_type: ApprovalRequestType | str,
        payload: ApprovalRequestCreate,
        *,
        time_view_mode: str | None = None,
    ) -> ApprovalRequest:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = self._transport.request(
            "POST",
            self._user_type_path(user_id, approval_type),
            kind=CqsKind.NON_IDEMPOTENT_COMMAND,
            params=_time_view_params(time_view_mode),
            json=body,
        )
        return ApprovalRequest.model_validate(data)

    # PATCH .../approval-requests/{id}
    def update(self, approval_request_id: ApprovalRequestId | str, payload: ApprovalRequestUpdate) -> ApprovalRequest:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = self._transport.request(
            "PATCH", self._item_path(approval_request_id), kind=CqsKind.IDEMPOTENT_COMMAND, json=body
        )
        return ApprovalRequest.model_validate(data)

    # POST .../approval-requests/resubmit-entries-for-approval
    def resubmit(self, payload: ApprovalRequestResubmit, *, time_view_mode: str | None = None) -> ApprovalRequest:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = self._transport.request(
            "POST",
            self._resubmit_path(),
            kind=CqsKind.NON_IDEMPOTENT_COMMAND,
            params=_time_view_params(time_view_mode),
            json=body,
        )
        return ApprovalRequest.model_validate(data)


class AsyncApprovalsResource(_ApprovalPaths):
    def __init__(self, transport: AsyncTransport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # GET .../approval-requests (auto-paginating)
    def list(self, *, request_filter: ApprovalRequestFilter | None = None) -> AsyncIterator[ApprovalDetails]:
        return apaginate(lambda page: self.list_page(request_filter=request_filter, page=page))

    # GET .../approval-requests
    async def list_page(
        self, *, request_filter: ApprovalRequestFilter | None = None, page: int = 1, page_size: int | None = None
    ) -> Page[ApprovalDetails]:
        params = self._list_params(request_filter, page, page_size)
        data = await self._transport.request("GET", self._collection_path(), kind=CqsKind.QUERY, params=params)
        items = [ApprovalDetails.model_validate(item) for item in cast("list[dict[str, Any]]", data)]
        return Page(items=items, page=page, page_size=params["page-size"])

    # POST .../approval-requests/{type}
    async def submit(
        self,
        approval_type: ApprovalRequestType | str,
        payload: ApprovalRequestCreate,
        *,
        time_view_mode: str | None = None,
    ) -> ApprovalRequest:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = await self._transport.request(
            "POST",
            self._type_path(approval_type),
            kind=CqsKind.NON_IDEMPOTENT_COMMAND,
            params=_time_view_params(time_view_mode),
            json=body,
        )
        return ApprovalRequest.model_validate(data)

    # POST .../approval-requests/users/{userId}/{type}
    async def submit_for_user(
        self,
        user_id: UserId | str,
        approval_type: ApprovalRequestType | str,
        payload: ApprovalRequestCreate,
        *,
        time_view_mode: str | None = None,
    ) -> ApprovalRequest:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = await self._transport.request(
            "POST",
            self._user_type_path(user_id, approval_type),
            kind=CqsKind.NON_IDEMPOTENT_COMMAND,
            params=_time_view_params(time_view_mode),
            json=body,
        )
        return ApprovalRequest.model_validate(data)

    # PATCH .../approval-requests/{id}
    async def update(
        self, approval_request_id: ApprovalRequestId | str, payload: ApprovalRequestUpdate
    ) -> ApprovalRequest:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = await self._transport.request(
            "PATCH", self._item_path(approval_request_id), kind=CqsKind.IDEMPOTENT_COMMAND, json=body
        )
        return ApprovalRequest.model_validate(data)

    # POST .../approval-requests/resubmit-entries-for-approval
    async def resubmit(
        self, payload: ApprovalRequestResubmit, *, time_view_mode: str | None = None
    ) -> ApprovalRequest:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = await self._transport.request(
            "POST",
            self._resubmit_path(),
            kind=CqsKind.NON_IDEMPOTENT_COMMAND,
            params=_time_view_params(time_view_mode),
            json=body,
        )
        return ApprovalRequest.model_validate(data)
