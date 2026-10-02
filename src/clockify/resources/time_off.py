from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import cast
from typing import override

from clockify._pagination import Page
from clockify._pagination import apaginate
from clockify._pagination import paginate
from clockify.models.time_off import TimeOffBalance
from clockify.models.time_off import TimeOffBalanceAssignment
from clockify.models.time_off import TimeOffBalanceList
from clockify.models.time_off import TimeOffPolicy
from clockify.models.time_off import TimeOffPolicyCreate
from clockify.models.time_off import TimeOffPolicyUpdate
from clockify.models.time_off import TimeOffRequest
from clockify.models.time_off import TimeOffRequestDetails
from clockify.models.time_off import TimeOffRequestList
from clockify.resources.base import AsyncWorkspaceResource
from clockify.resources.base import WorkspaceResource
from clockify.retry import CqsKind

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from collections.abc import Iterator

    from pydantic import BaseModel

    from clockify._transport import AsyncTransport
    from clockify._transport import Transport
    from clockify.ids import TimeOffBalanceAssignmentId
    from clockify.ids import TimeOffPolicyId
    from clockify.ids import TimeOffRequestId
    from clockify.ids import UserId
    from clockify.ids import WorkspaceId
    from clockify.models.time_off import TimeOffBalanceAssignmentCreate
    from clockify.models.time_off import TimeOffBalanceAssignmentDelete
    from clockify.models.time_off import TimeOffBalanceAssignmentUpdate
    from clockify.models.time_off import TimeOffBalanceFilter
    from clockify.models.time_off import TimeOffBalanceUpdate
    from clockify.models.time_off import TimeOffPolicyFilter
    from clockify.models.time_off import TimeOffPolicyStatusUpdate
    from clockify.models.time_off import TimeOffRequestCreate
    from clockify.models.time_off import TimeOffRequestFilter
    from clockify.models.time_off import TimeOffRequestStatusUpdate


def _time_view_params(time_view_mode: str | None) -> dict[str, str] | None:
    return None if time_view_mode is None else {"timeViewMode": time_view_mode}


def _body(payload: BaseModel) -> dict[str, Any]:
    return payload.model_dump(mode="json", by_alias=True, exclude_unset=True)


def _items[T](model: type[T], data: object) -> list[T]:
    validate = cast("Any", model).model_validate
    return [validate(item) for item in cast("list[dict[str, Any]]", data)]


def _policy_params(policy_filter: TimeOffPolicyFilter | None, page: int, page_size: int) -> dict[str, Any]:
    params: dict[str, Any] = dict(policy_filter.as_params()) if policy_filter is not None else {}
    params["page"] = page
    params["page-size"] = page_size
    return params


class TimeOffPoliciesResource(WorkspaceResource[TimeOffPolicy, TimeOffPolicyCreate, TimeOffPolicyUpdate]):
    _path = "/time-off/policies"
    _read_model = TimeOffPolicy

    # GET {path} (auto-paginating)
    @override
    def list(self, *, policy_filter: TimeOffPolicyFilter | None = None) -> Iterator[TimeOffPolicy]:
        return paginate(lambda page: self.list_page(policy_filter=policy_filter, page=page))

    # GET {path}
    @override
    def list_page(
        self, *, policy_filter: TimeOffPolicyFilter | None = None, page: int = 1, page_size: int | None = None
    ) -> Page[TimeOffPolicy]:
        size = self._page_size if page_size is None else page_size
        params = _policy_params(policy_filter, page, size)
        data = self._transport.request("GET", self._collection_path(), kind=CqsKind.QUERY, params=params)
        return Page(items=_items(TimeOffPolicy, data), page=page, page_size=size)

    # PATCH {path}/{id}
    def update_status(self, policy_id: TimeOffPolicyId | str, payload: TimeOffPolicyStatusUpdate) -> TimeOffPolicy:
        data = self._transport.request(
            "PATCH", self._item_path(policy_id), kind=CqsKind.IDEMPOTENT_COMMAND, json=_body(payload)
        )
        return TimeOffPolicy.model_validate(data)


class AsyncTimeOffPoliciesResource(AsyncWorkspaceResource[TimeOffPolicy, TimeOffPolicyCreate, TimeOffPolicyUpdate]):
    _path = "/time-off/policies"
    _read_model = TimeOffPolicy

    # GET {path} (auto-paginating)
    @override
    def list(self, *, policy_filter: TimeOffPolicyFilter | None = None) -> AsyncIterator[TimeOffPolicy]:
        return apaginate(lambda page: self.list_page(policy_filter=policy_filter, page=page))

    # GET {path}
    @override
    async def list_page(
        self, *, policy_filter: TimeOffPolicyFilter | None = None, page: int = 1, page_size: int | None = None
    ) -> Page[TimeOffPolicy]:
        size = self._page_size if page_size is None else page_size
        params = _policy_params(policy_filter, page, size)
        data = await self._transport.request("GET", self._collection_path(), kind=CqsKind.QUERY, params=params)
        return Page(items=_items(TimeOffPolicy, data), page=page, page_size=size)

    # PATCH {path}/{id}
    async def update_status(
        self, policy_id: TimeOffPolicyId | str, payload: TimeOffPolicyStatusUpdate
    ) -> TimeOffPolicy:
        data = await self._transport.request(
            "PATCH", self._item_path(policy_id), kind=CqsKind.IDEMPOTENT_COMMAND, json=_body(payload)
        )
        return TimeOffPolicy.model_validate(data)


@dataclass(slots=True, kw_only=True)
class _TimeOffRequestPaths:
    _workspace_id: WorkspaceId
    _page_size: int

    def _time_off_path(self) -> str:
        return f"/workspaces/{self._workspace_id}/time-off"

    def _list_path(self) -> str:
        return f"{self._time_off_path()}/requests"

    def _policy_path(self, policy_id: TimeOffPolicyId | str) -> str:
        return f"{self._time_off_path()}/policies/{policy_id}/requests"

    def _for_user_path(self, policy_id: TimeOffPolicyId | str, user_id: UserId | str) -> str:
        return f"{self._time_off_path()}/policies/{policy_id}/users/{user_id}/requests"

    def _item_path(self, policy_id: TimeOffPolicyId | str, request_id: TimeOffRequestId | str) -> str:
        return f"{self._policy_path(policy_id)}/{request_id}"

    def _list_body(
        self, request_filter: TimeOffRequestFilter | None, page: int, page_size: int | None
    ) -> dict[str, Any]:
        body: dict[str, Any] = request_filter.as_body() if request_filter is not None else {}
        body["page"] = page
        body["pageSize"] = self._page_size if page_size is None else page_size
        return body


class TimeOffRequestsResource(_TimeOffRequestPaths):
    # Hand-written rather than a WorkspaceResource subclass: requests hang off a policy,
    # the list is a POST with the page in its body, and there is no single-request GET.
    def __init__(self, transport: Transport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # POST .../time-off/requests (auto-paginating; a query despite the verb)
    def list(self, *, request_filter: TimeOffRequestFilter | None = None) -> Iterator[TimeOffRequestDetails]:
        return paginate(lambda page: self.list_page(request_filter=request_filter, page=page))

    # POST .../time-off/requests
    def list_page(
        self, *, request_filter: TimeOffRequestFilter | None = None, page: int = 1, page_size: int | None = None
    ) -> Page[TimeOffRequestDetails]:
        body = self._list_body(request_filter, page, page_size)
        data = self._transport.request("POST", self._list_path(), kind=CqsKind.QUERY, json=body)
        items = TimeOffRequestList.model_validate(data).requests or []
        return Page(items=items, page=page, page_size=body["pageSize"])

    # POST .../time-off/policies/{policyId}/requests
    def create(
        self, policy_id: TimeOffPolicyId | str, payload: TimeOffRequestCreate, *, time_view_mode: str | None = None
    ) -> TimeOffRequestDetails:
        data = self._transport.request(
            "POST",
            self._policy_path(policy_id),
            kind=CqsKind.NON_IDEMPOTENT_COMMAND,
            params=_time_view_params(time_view_mode),
            json=_body(payload),
        )
        return TimeOffRequestDetails.model_validate(data)

    # POST .../time-off/policies/{policyId}/users/{userId}/requests
    def create_for_user(
        self,
        policy_id: TimeOffPolicyId | str,
        user_id: UserId | str,
        payload: TimeOffRequestCreate,
        *,
        time_view_mode: str | None = None,
    ) -> TimeOffRequestDetails:
        data = self._transport.request(
            "POST",
            self._for_user_path(policy_id, user_id),
            kind=CqsKind.NON_IDEMPOTENT_COMMAND,
            params=_time_view_params(time_view_mode),
            json=_body(payload),
        )
        return TimeOffRequestDetails.model_validate(data)

    # PATCH .../time-off/policies/{policyId}/requests/{requestId}
    def update_status(
        self,
        policy_id: TimeOffPolicyId | str,
        request_id: TimeOffRequestId | str,
        payload: TimeOffRequestStatusUpdate,
        *,
        time_view_mode: str | None = None,
    ) -> TimeOffRequest:
        data = self._transport.request(
            "PATCH",
            self._item_path(policy_id, request_id),
            kind=CqsKind.IDEMPOTENT_COMMAND,
            params=_time_view_params(time_view_mode),
            json=_body(payload),
        )
        return TimeOffRequest.model_validate(data)

    # DELETE .../time-off/policies/{policyId}/requests/{requestId}
    def delete(
        self,
        policy_id: TimeOffPolicyId | str,
        request_id: TimeOffRequestId | str,
        *,
        time_view_mode: str | None = None,
    ) -> TimeOffRequest:
        data = self._transport.request(
            "DELETE",
            self._item_path(policy_id, request_id),
            kind=CqsKind.IDEMPOTENT_COMMAND,
            params=_time_view_params(time_view_mode),
        )
        return TimeOffRequest.model_validate(data)


class AsyncTimeOffRequestsResource(_TimeOffRequestPaths):
    def __init__(self, transport: AsyncTransport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # POST .../time-off/requests (auto-paginating; a query despite the verb)
    def list(self, *, request_filter: TimeOffRequestFilter | None = None) -> AsyncIterator[TimeOffRequestDetails]:
        return apaginate(lambda page: self.list_page(request_filter=request_filter, page=page))

    # POST .../time-off/requests
    async def list_page(
        self, *, request_filter: TimeOffRequestFilter | None = None, page: int = 1, page_size: int | None = None
    ) -> Page[TimeOffRequestDetails]:
        body = self._list_body(request_filter, page, page_size)
        data = await self._transport.request("POST", self._list_path(), kind=CqsKind.QUERY, json=body)
        items = TimeOffRequestList.model_validate(data).requests or []
        return Page(items=items, page=page, page_size=body["pageSize"])

    # POST .../time-off/policies/{policyId}/requests
    async def create(
        self, policy_id: TimeOffPolicyId | str, payload: TimeOffRequestCreate, *, time_view_mode: str | None = None
    ) -> TimeOffRequestDetails:
        data = await self._transport.request(
            "POST",
            self._policy_path(policy_id),
            kind=CqsKind.NON_IDEMPOTENT_COMMAND,
            params=_time_view_params(time_view_mode),
            json=_body(payload),
        )
        return TimeOffRequestDetails.model_validate(data)

    # POST .../time-off/policies/{policyId}/users/{userId}/requests
    async def create_for_user(
        self,
        policy_id: TimeOffPolicyId | str,
        user_id: UserId | str,
        payload: TimeOffRequestCreate,
        *,
        time_view_mode: str | None = None,
    ) -> TimeOffRequestDetails:
        data = await self._transport.request(
            "POST",
            self._for_user_path(policy_id, user_id),
            kind=CqsKind.NON_IDEMPOTENT_COMMAND,
            params=_time_view_params(time_view_mode),
            json=_body(payload),
        )
        return TimeOffRequestDetails.model_validate(data)

    # PATCH .../time-off/policies/{policyId}/requests/{requestId}
    async def update_status(
        self,
        policy_id: TimeOffPolicyId | str,
        request_id: TimeOffRequestId | str,
        payload: TimeOffRequestStatusUpdate,
        *,
        time_view_mode: str | None = None,
    ) -> TimeOffRequest:
        data = await self._transport.request(
            "PATCH",
            self._item_path(policy_id, request_id),
            kind=CqsKind.IDEMPOTENT_COMMAND,
            params=_time_view_params(time_view_mode),
            json=_body(payload),
        )
        return TimeOffRequest.model_validate(data)

    # DELETE .../time-off/policies/{policyId}/requests/{requestId}
    async def delete(
        self,
        policy_id: TimeOffPolicyId | str,
        request_id: TimeOffRequestId | str,
        *,
        time_view_mode: str | None = None,
    ) -> TimeOffRequest:
        data = await self._transport.request(
            "DELETE",
            self._item_path(policy_id, request_id),
            kind=CqsKind.IDEMPOTENT_COMMAND,
            params=_time_view_params(time_view_mode),
        )
        return TimeOffRequest.model_validate(data)


def _balance_params(balance_filter: TimeOffBalanceFilter | None, page: int, page_size: int) -> dict[str, Any]:
    params: dict[str, Any] = dict(balance_filter.as_params()) if balance_filter is not None else {}
    params["page"] = page
    params["page-size"] = page_size
    return params


def _balances(data: object) -> list[TimeOffBalance]:
    return TimeOffBalanceList.model_validate(data).balances or []


@dataclass(slots=True, kw_only=True)
class _BalancePaths:
    _workspace_id: WorkspaceId
    _page_size: int

    def _balance_path(self) -> str:
        return f"/workspaces/{self._workspace_id}/time-off/balance"

    def _policy_path(self, policy_id: TimeOffPolicyId | str) -> str:
        return f"{self._balance_path()}/policy/{policy_id}"

    def _user_path(self, user_id: UserId | str) -> str:
        return f"{self._balance_path()}/user/{user_id}"

    def _assignment_path(self) -> str:
        return f"{self._balance_path()}/assignment"

    def _user_assignments_path(self, user_id: UserId | str, policy_id: TimeOffPolicyId | str) -> str:
        return f"{self._assignment_path()}/user/{user_id}/policy/{policy_id}"

    def _assignment_item_path(
        self, assignment_id: TimeOffBalanceAssignmentId | str, user_id: UserId | str, policy_id: TimeOffPolicyId | str
    ) -> str:
        return f"{self._assignment_path()}/{assignment_id}/user/{user_id}/policy/{policy_id}"


class TimeOffBalancesResource(_BalancePaths):
    # A balance is read per policy or per user, and changed by a delta, so it does not
    # fit the uniform CRUD shape of WorkspaceResource.
    def __init__(self, transport: Transport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # GET .../time-off/balance/policy/{policyId} (auto-paginating)
    def list_for_policy(
        self, policy_id: TimeOffPolicyId | str, *, balance_filter: TimeOffBalanceFilter | None = None
    ) -> Iterator[TimeOffBalance]:
        return paginate(lambda page: self.list_for_policy_page(policy_id, balance_filter=balance_filter, page=page))

    # GET .../time-off/balance/policy/{policyId}
    def list_for_policy_page(
        self,
        policy_id: TimeOffPolicyId | str,
        *,
        balance_filter: TimeOffBalanceFilter | None = None,
        page: int = 1,
        page_size: int | None = None,
    ) -> Page[TimeOffBalance]:
        size = self._page_size if page_size is None else page_size
        params = _balance_params(balance_filter, page, size)
        data = self._transport.request("GET", self._policy_path(policy_id), kind=CqsKind.QUERY, params=params)
        return Page(items=_balances(data), page=page, page_size=size)

    # GET .../time-off/balance/user/{userId} (auto-paginating)
    def list_for_user(
        self, user_id: UserId | str, *, balance_filter: TimeOffBalanceFilter | None = None
    ) -> Iterator[TimeOffBalance]:
        return paginate(lambda page: self.list_for_user_page(user_id, balance_filter=balance_filter, page=page))

    # GET .../time-off/balance/user/{userId}
    def list_for_user_page(
        self,
        user_id: UserId | str,
        *,
        balance_filter: TimeOffBalanceFilter | None = None,
        page: int = 1,
        page_size: int | None = None,
    ) -> Page[TimeOffBalance]:
        size = self._page_size if page_size is None else page_size
        params = _balance_params(balance_filter, page, size)
        data = self._transport.request("GET", self._user_path(user_id), kind=CqsKind.QUERY, params=params)
        return Page(items=_balances(data), page=page, page_size=size)

    # PATCH .../time-off/balance/policy/{policyId} (`value` is a change, so a repeat adds it twice)
    def update(self, policy_id: TimeOffPolicyId | str, payload: TimeOffBalanceUpdate) -> None:
        self._transport.request(
            "PATCH", self._policy_path(policy_id), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=_body(payload)
        )

    # POST .../time-off/balance/assignment
    def create_assignment(self, payload: TimeOffBalanceAssignmentCreate) -> None:
        self._transport.request(
            "POST", self._assignment_path(), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=_body(payload)
        )

    # GET .../time-off/balance/assignment/user/{userId}/policy/{policyId}
    def list_assignments(
        self, user_id: UserId | str, policy_id: TimeOffPolicyId | str
    ) -> Iterator[TimeOffBalanceAssignment]:
        data = self._transport.request("GET", self._user_assignments_path(user_id, policy_id), kind=CqsKind.QUERY)
        return iter(_items(TimeOffBalanceAssignment, data))

    # PUT .../time-off/balance/assignment/{assignmentId}/user/{userId}/policy/{policyId}
    # (`balanceChange` is a change, so a repeat adds it twice)
    def update_assignment(
        self,
        assignment_id: TimeOffBalanceAssignmentId | str,
        user_id: UserId | str,
        policy_id: TimeOffPolicyId | str,
        payload: TimeOffBalanceAssignmentUpdate,
    ) -> None:
        self._transport.request(
            "PUT",
            self._assignment_item_path(assignment_id, user_id, policy_id),
            kind=CqsKind.NON_IDEMPOTENT_COMMAND,
            json=_body(payload),
        )

    # DELETE .../time-off/balance/assignment/{assignmentId}/user/{userId}/policy/{policyId}
    def delete_assignment(
        self,
        assignment_id: TimeOffBalanceAssignmentId | str,
        user_id: UserId | str,
        policy_id: TimeOffPolicyId | str,
        payload: TimeOffBalanceAssignmentDelete,
    ) -> None:
        self._transport.request(
            "DELETE",
            self._assignment_item_path(assignment_id, user_id, policy_id),
            kind=CqsKind.IDEMPOTENT_COMMAND,
            json=_body(payload),
        )


class AsyncTimeOffBalancesResource(_BalancePaths):
    def __init__(self, transport: AsyncTransport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        super().__init__(_workspace_id=workspace_id, _page_size=page_size)
        self._transport = transport

    # GET .../time-off/balance/policy/{policyId} (auto-paginating)
    def list_for_policy(
        self, policy_id: TimeOffPolicyId | str, *, balance_filter: TimeOffBalanceFilter | None = None
    ) -> AsyncIterator[TimeOffBalance]:
        return apaginate(lambda page: self.list_for_policy_page(policy_id, balance_filter=balance_filter, page=page))

    # GET .../time-off/balance/policy/{policyId}
    async def list_for_policy_page(
        self,
        policy_id: TimeOffPolicyId | str,
        *,
        balance_filter: TimeOffBalanceFilter | None = None,
        page: int = 1,
        page_size: int | None = None,
    ) -> Page[TimeOffBalance]:
        size = self._page_size if page_size is None else page_size
        params = _balance_params(balance_filter, page, size)
        data = await self._transport.request("GET", self._policy_path(policy_id), kind=CqsKind.QUERY, params=params)
        return Page(items=_balances(data), page=page, page_size=size)

    # GET .../time-off/balance/user/{userId} (auto-paginating)
    def list_for_user(
        self, user_id: UserId | str, *, balance_filter: TimeOffBalanceFilter | None = None
    ) -> AsyncIterator[TimeOffBalance]:
        return apaginate(lambda page: self.list_for_user_page(user_id, balance_filter=balance_filter, page=page))

    # GET .../time-off/balance/user/{userId}
    async def list_for_user_page(
        self,
        user_id: UserId | str,
        *,
        balance_filter: TimeOffBalanceFilter | None = None,
        page: int = 1,
        page_size: int | None = None,
    ) -> Page[TimeOffBalance]:
        size = self._page_size if page_size is None else page_size
        params = _balance_params(balance_filter, page, size)
        data = await self._transport.request("GET", self._user_path(user_id), kind=CqsKind.QUERY, params=params)
        return Page(items=_balances(data), page=page, page_size=size)

    # PATCH .../time-off/balance/policy/{policyId} (`value` is a change, so a repeat adds it twice)
    async def update(self, policy_id: TimeOffPolicyId | str, payload: TimeOffBalanceUpdate) -> None:
        await self._transport.request(
            "PATCH", self._policy_path(policy_id), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=_body(payload)
        )

    # POST .../time-off/balance/assignment
    async def create_assignment(self, payload: TimeOffBalanceAssignmentCreate) -> None:
        await self._transport.request(
            "POST", self._assignment_path(), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=_body(payload)
        )

    # GET .../time-off/balance/assignment/user/{userId}/policy/{policyId}
    async def list_assignments(
        self, user_id: UserId | str, policy_id: TimeOffPolicyId | str
    ) -> AsyncIterator[TimeOffBalanceAssignment]:
        data = await self._transport.request(
            "GET", self._user_assignments_path(user_id, policy_id), kind=CqsKind.QUERY
        )
        for assignment in _items(TimeOffBalanceAssignment, data):
            yield assignment

    # PUT .../time-off/balance/assignment/{assignmentId}/user/{userId}/policy/{policyId}
    # (`balanceChange` is a change, so a repeat adds it twice)
    async def update_assignment(
        self,
        assignment_id: TimeOffBalanceAssignmentId | str,
        user_id: UserId | str,
        policy_id: TimeOffPolicyId | str,
        payload: TimeOffBalanceAssignmentUpdate,
    ) -> None:
        await self._transport.request(
            "PUT",
            self._assignment_item_path(assignment_id, user_id, policy_id),
            kind=CqsKind.NON_IDEMPOTENT_COMMAND,
            json=_body(payload),
        )

    # DELETE .../time-off/balance/assignment/{assignmentId}/user/{userId}/policy/{policyId}
    async def delete_assignment(
        self,
        assignment_id: TimeOffBalanceAssignmentId | str,
        user_id: UserId | str,
        policy_id: TimeOffPolicyId | str,
        payload: TimeOffBalanceAssignmentDelete,
    ) -> None:
        await self._transport.request(
            "DELETE",
            self._assignment_item_path(assignment_id, user_id, policy_id),
            kind=CqsKind.IDEMPOTENT_COMMAND,
            json=_body(payload),
        )
