from __future__ import annotations

import datetime
import json
from typing import Final

import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import AsyncClockifyClient
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import CqsKind
from clockify import TimeOffAccrualPeriod
from clockify import TimeOffAutomaticAccrualRequest
from clockify import TimeOffBalance
from clockify import TimeOffBalanceAssignment
from clockify import TimeOffBalanceAssignmentCreate
from clockify import TimeOffBalanceAssignmentDelete
from clockify import TimeOffBalanceAssignmentUpdate
from clockify import TimeOffBalanceDateRange
from clockify import TimeOffBalanceFilter
from clockify import TimeOffBalanceSortColumn
from clockify import TimeOffBalanceUpdate
from clockify import TimeOffHalfDayPeriod
from clockify import TimeOffPeriod
from clockify import TimeOffPeriodRequest
from clockify import TimeOffPolicy
from clockify import TimeOffPolicyApproval
from clockify import TimeOffPolicyCreate
from clockify import TimeOffPolicyFilter
from clockify import TimeOffPolicyIcon
from clockify import TimeOffPolicyStatus
from clockify import TimeOffPolicyStatusUpdate
from clockify import TimeOffPolicyUpdate
from clockify import TimeOffRequest
from clockify import TimeOffRequestCreate
from clockify import TimeOffRequestDecision
from clockify import TimeOffRequestDetails
from clockify import TimeOffRequestFilter
from clockify import TimeOffRequestPeriod
from clockify import TimeOffRequestPeriodRequest
from clockify import TimeOffRequestStatus
from clockify import TimeOffRequestStatusType
from clockify import TimeOffRequestStatusUpdate
from clockify import TimeOffUnit
from clockify._auth import ApiKeyAuth  # ruff: ignore[import-private-name]
from clockify._transport import AsyncTransport  # ruff: ignore[import-private-name]
from clockify._transport import Transport  # ruff: ignore[import-private-name]
from clockify.config import ClientConfig
from clockify.ids import TimeOffPolicyId
from clockify.ids import UserId
from clockify.ids import WorkspaceId
from clockify.models import ApprovalSortOrder
from clockify.resources.time_off import AsyncTimeOffBalancesResource
from clockify.resources.time_off import AsyncTimeOffPoliciesResource
from clockify.resources.time_off import AsyncTimeOffRequestsResource
from clockify.resources.time_off import TimeOffBalancesResource
from clockify.resources.time_off import TimeOffPoliciesResource
from clockify.resources.time_off import TimeOffRequestsResource

BASE_URL: Final = "https://fake.clockify.test/api/v1"
WORKSPACE_ID: Final = WorkspaceId("64a1f0000000000000000001")
TIME_OFF_URL: Final = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/time-off"
POLICIES_URL: Final = f"{TIME_OFF_URL}/policies"
BALANCE_URL: Final = f"{TIME_OFF_URL}/balance"
POLICY_ID: Final = TimeOffPolicyId("66a1f0000000000000000010")
REQUEST_ID: Final = "66a1f0000000000000000020"
ASSIGNMENT_ID: Final = "66a1f0000000000000000030"
USER_ID: Final = UserId("5a0ab5acb07987125438b60f")
CQS: Final = "clockify_cqs"

POLICY_PAYLOAD: Final = {
    "id": str(POLICY_ID),
    "workspaceId": str(WORKSPACE_ID),
    "name": "Vacation",
    "archived": False,
    "icon": "PLANE",
    "timeUnit": "DAYS",
    "approve": {"requiresApproval": True, "teamManagers": True},
}
POLICY: Final = TimeOffPolicy(
    id=POLICY_ID,
    workspace_id=WORKSPACE_ID,
    name="Vacation",
    archived=False,
    icon=TimeOffPolicyIcon.PLANE,
    time_unit=TimeOffUnit.DAYS,
    approve=TimeOffPolicyApproval(requires_approval=True, team_managers=True),
)
APPROVAL: Final = TimeOffPolicyApproval(requires_approval=True, team_managers=True)
APPROVAL_BODY: Final = {"requiresApproval": True, "teamManagers": True}

STATUS_PAYLOAD: Final = {"statusType": "APPROVED", "note": "enjoy", "changedAt": "2026-03-01T10:00:00Z"}
STATUS: Final = TimeOffRequestStatus(
    status_type=TimeOffRequestStatusType.APPROVED,
    note="enjoy",
    changed_at=datetime.datetime(2026, 3, 1, 10, 0, tzinfo=datetime.UTC),
)
PERIOD_PAYLOAD: Final = {"period": {"start": "2026-03-02T00:00:00Z", "end": "2026-03-03T00:00:00Z"}, "halfDay": False}
PERIOD: Final = TimeOffRequestPeriod(
    period=TimeOffPeriod(
        start=datetime.datetime(2026, 3, 2, tzinfo=datetime.UTC),
        end=datetime.datetime(2026, 3, 3, tzinfo=datetime.UTC),
    ),
    half_day=False,
)
REQUEST_PAYLOAD: Final = {
    "id": REQUEST_ID,
    "policyId": str(POLICY_ID),
    "userId": str(USER_ID),
    "balanceDiff": -2.0,
    "status": STATUS_PAYLOAD,
    "timeOffPeriod": PERIOD_PAYLOAD,
}
REQUEST: Final = TimeOffRequest(
    id=REQUEST_ID, policy_id=POLICY_ID, user_id=USER_ID, balance_diff=-2.0, status=STATUS, time_off_period=PERIOD
)
DETAILS_PAYLOAD: Final = {**REQUEST_PAYLOAD, "policyName": "Vacation", "timeUnit": "DAYS"}
DETAILS: Final = TimeOffRequestDetails(
    id=REQUEST_ID,
    policy_id=POLICY_ID,
    policy_name="Vacation",
    user_id=USER_ID,
    balance_diff=-2.0,
    time_unit=TimeOffUnit.DAYS,
    status=STATUS,
    time_off_period=PERIOD,
)
REQUEST_CREATE: Final = TimeOffRequestCreate(
    time_off_period=TimeOffRequestPeriodRequest(
        period=TimeOffPeriodRequest(start=datetime.date(2026, 3, 2), end=datetime.date(2026, 3, 3)),
        is_half_day=False,
        half_day_period=TimeOffHalfDayPeriod.NOT_DEFINED,
    ),
    note="trip",
)
REQUEST_CREATE_BODY: Final = {
    "timeOffPeriod": {
        "period": {"start": "2026-03-02", "end": "2026-03-03"},
        "isHalfDay": False,
        "halfDayPeriod": "NOT_DEFINED",
    },
    "note": "trip",
}
BALANCE_PAYLOAD: Final = {
    "id": "bal-1",
    "userId": str(USER_ID),
    "policyId": str(POLICY_ID),
    "policyTimeUnit": "HOURS",
    "balance": 12.5,
    "used": 3.0,
    "total": 15.5,
}
BALANCE: Final = TimeOffBalance(
    id="bal-1",
    user_id=USER_ID,
    policy_id=POLICY_ID,
    policy_time_unit=TimeOffUnit.HOURS,
    balance=12.5,
    used=3.0,
    total=15.5,
)
ASSIGNMENT_PAYLOAD: Final = {
    "id": ASSIGNMENT_ID,
    "userId": str(USER_ID),
    "policyId": str(POLICY_ID),
    "balance": 5.0,
    "accrued": 1.0,
    "dateRange": {"start": "2026-01-01T00:00:00Z", "end": "2026-12-31T00:00:00Z"},
}
ASSIGNMENT: Final = TimeOffBalanceAssignment(
    id=ASSIGNMENT_ID,
    user_id=USER_ID,
    policy_id=POLICY_ID,
    balance=5.0,
    accrued=1.0,
    date_range=TimeOffPeriod(
        start=datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC),
        end=datetime.datetime(2026, 12, 31, tzinfo=datetime.UTC),
    ),
)
DATE_RANGE: Final = TimeOffBalanceDateRange(start=datetime.date(2026, 1, 1), end=datetime.date(2026, 12, 31))
DATE_RANGE_BODY: Final = {"start": "2026-01-01", "end": "2026-12-31"}


def _client() -> ClockifyClient:
    return ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


def _async_client() -> AsyncClockifyClient:
    return AsyncClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


def _config() -> ClientConfig:
    return ClientConfig(api_key="dummy", base_url=BASE_URL, reports_base_url=BASE_URL, retry=NO_RETRY)


def _last_cqs() -> object:
    return respx.calls[0].request.extensions.get(CQS)


# --- policies -------------------------------------------------------------------------


@respx.mock
def test_policies_list_page_sends_the_filter_and_page_params() -> None:
    # Arrange
    route = respx.get(POLICIES_URL).mock(return_value=Response(200, json=[POLICY_PAYLOAD]))
    client = _client()
    policy_filter = TimeOffPolicyFilter(
        name="Vac", status=TimeOffPolicyStatus.ACTIVE, sort_column="NAME", sort_order=ApprovalSortOrder.DESCENDING
    )
    # Act
    page = client.workspace(WORKSPACE_ID).time_off_policies.list_page(
        policy_filter=policy_filter, page=2, page_size=10
    )
    # Assert
    assert route.calls[0].request.url.params.multi_items() == [
        ("name", "Vac"),
        ("status", "ACTIVE"),
        ("sort-column", "NAME"),
        ("sort-order", "DESCENDING"),
        ("page", "2"),
        ("page-size", "10"),
    ]
    assert _last_cqs() == CqsKind.QUERY
    assert page.items == [POLICY]
    client.close()


@respx.mock
def test_policies_list_auto_paginates_without_a_filter() -> None:
    # Arrange
    route = respx.get(POLICIES_URL).mock(
        side_effect=[Response(200, json=[POLICY_PAYLOAD, POLICY_PAYLOAD]), Response(200, json=[POLICY_PAYLOAD])]
    )
    transport = Transport(_config(), BASE_URL, ApiKeyAuth("dummy"))
    # Act
    policies = list(TimeOffPoliciesResource(transport, WORKSPACE_ID, page_size=2).list())
    # Assert
    assert policies == [POLICY, POLICY, POLICY]
    assert [call.request.url.params.multi_items() for call in route.calls] == [
        [("page", "1"), ("page-size", "2")],
        [("page", "2"), ("page-size", "2")],
    ]
    transport.close()


@respx.mock
def test_policies_get_create_update_status_and_delete() -> None:
    # Arrange
    item_url = f"{POLICIES_URL}/{POLICY_ID}"
    get_route = respx.get(item_url).mock(return_value=Response(200, json=POLICY_PAYLOAD))
    create_route = respx.post(POLICIES_URL).mock(return_value=Response(201, json=POLICY_PAYLOAD))
    put_route = respx.put(item_url).mock(return_value=Response(200, json=POLICY_PAYLOAD))
    patch_route = respx.patch(item_url).mock(return_value=Response(200, json=POLICY_PAYLOAD))
    delete_route = respx.delete(item_url).mock(return_value=Response(200))
    policies = _client().workspace(WORKSPACE_ID).time_off_policies
    create = TimeOffPolicyCreate(
        name="Vacation",
        approve=APPROVAL,
        time_unit=TimeOffUnit.DAYS,
        automatic_accrual=TimeOffAutomaticAccrualRequest(amount=1.5, period=TimeOffAccrualPeriod.MONTH),
    )
    update = TimeOffPolicyUpdate(
        name="Vacation",
        approve=APPROVAL,
        allow_half_day=True,
        allow_negative_balance=False,
        archived=False,
        everyone_including_new=True,
        has_expiration=False,
    )
    # Act
    results = (
        policies.get(POLICY_ID),
        policies.create(create),
        policies.update(POLICY_ID, update),
        policies.update_status(POLICY_ID, TimeOffPolicyStatusUpdate(status=TimeOffPolicyStatus.ARCHIVED)),
        policies.delete(POLICY_ID),
    )
    # Assert
    assert results == (POLICY, POLICY, POLICY, POLICY, None)
    assert json.loads(create_route.calls[0].request.content) == {
        "name": "Vacation",
        "approve": APPROVAL_BODY,
        "timeUnit": "DAYS",
        "automaticAccrual": {"amount": 1.5, "period": "MONTH"},
    }
    assert json.loads(put_route.calls[0].request.content) == {
        "name": "Vacation",
        "approve": APPROVAL_BODY,
        "allowHalfDay": True,
        "allowNegativeBalance": False,
        "archived": False,
        "everyoneIncludingNew": True,
        "hasExpiration": False,
    }
    assert json.loads(patch_route.calls[0].request.content) == {"status": "ARCHIVED"}
    assert [
        r.calls[0].request.extensions.get(CQS) for r in (get_route, create_route, put_route, patch_route, delete_route)
    ] == [
        CqsKind.QUERY,
        CqsKind.NON_IDEMPOTENT_COMMAND,
        CqsKind.IDEMPOTENT_COMMAND,
        CqsKind.IDEMPOTENT_COMMAND,
        CqsKind.IDEMPOTENT_COMMAND,
    ]


async def test_async_policies_list_page_update_status_and_auto_pagination() -> None:
    # Arrange
    with respx.mock:
        list_route = respx.get(POLICIES_URL).mock(
            side_effect=[Response(200, json=[POLICY_PAYLOAD, POLICY_PAYLOAD]), Response(200, json=[POLICY_PAYLOAD])]
        )
        patch_route = respx.patch(f"{POLICIES_URL}/{POLICY_ID}").mock(return_value=Response(200, json=POLICY_PAYLOAD))
        transport = AsyncTransport(_config(), BASE_URL, ApiKeyAuth("dummy"))
        policies = AsyncTimeOffPoliciesResource(transport, WORKSPACE_ID, page_size=2)
        # Act
        listed = [policy async for policy in policies.list(policy_filter=TimeOffPolicyFilter(name="Vac"))]
        updated = await policies.update_status(POLICY_ID, TimeOffPolicyStatusUpdate(status=TimeOffPolicyStatus.ACTIVE))
        # Assert
        assert listed == [POLICY, POLICY, POLICY]
        assert list_route.calls[0].request.url.params.multi_items() == [
            ("name", "Vac"),
            ("page", "1"),
            ("page-size", "2"),
        ]
        assert updated == POLICY
        assert json.loads(patch_route.calls[0].request.content) == {"status": "ACTIVE"}
        await transport.aclose()


# --- requests -------------------------------------------------------------------------


@respx.mock
def test_requests_list_page_posts_the_filter_and_page_in_the_body_as_a_query() -> None:
    # Arrange
    route = respx.post(f"{TIME_OFF_URL}/requests").mock(
        return_value=Response(200, json={"count": 1, "requests": [DETAILS_PAYLOAD]})
    )
    client = _client()
    request_filter = TimeOffRequestFilter(
        start=datetime.datetime(2026, 3, 1, tzinfo=datetime.UTC),
        end=datetime.datetime(2026, 4, 1, tzinfo=datetime.UTC),
        statuses=[TimeOffRequestStatusType.PENDING, TimeOffRequestStatusType.APPROVED],
        users=[USER_ID],
        user_groups=[],
    )
    # Act
    page = client.workspace(WORKSPACE_ID).time_off_requests.list_page(
        request_filter=request_filter, page=3, page_size=20
    )
    # Assert
    assert not route.calls[0].request.url.params
    assert json.loads(route.calls[0].request.content) == {
        "start": "2026-03-01T00:00:00Z",
        "end": "2026-04-01T00:00:00Z",
        "statuses": ["PENDING", "APPROVED"],
        "users": [str(USER_ID)],
        "userGroups": [],
        "page": 3,
        "pageSize": 20,
    }
    assert _last_cqs() == CqsKind.QUERY
    assert page.items == [DETAILS]
    assert (page.page, page.page_size) == (3, 20)
    client.close()


@respx.mock
def test_requests_list_auto_paginates_and_tolerates_an_empty_envelope() -> None:
    # Arrange
    route = respx.post(f"{TIME_OFF_URL}/requests").mock(
        side_effect=[
            Response(200, json={"count": 3, "requests": [DETAILS_PAYLOAD, DETAILS_PAYLOAD]}),
            Response(200, json={}),
        ]
    )
    transport = Transport(_config(), BASE_URL, ApiKeyAuth("dummy"))
    # Act
    requests = list(TimeOffRequestsResource(transport, WORKSPACE_ID, page_size=2).list())
    # Assert
    assert requests == [DETAILS, DETAILS]
    assert [json.loads(call.request.content) for call in route.calls] == [
        {"page": 1, "pageSize": 2},
        {"page": 2, "pageSize": 2},
    ]
    transport.close()


@respx.mock
def test_requests_create_create_for_user_update_status_and_delete() -> None:
    # Arrange
    requests_url = f"{POLICIES_URL}/{POLICY_ID}/requests"
    create_route = respx.post(requests_url).mock(return_value=Response(200, json=DETAILS_PAYLOAD))
    for_user_route = respx.post(f"{POLICIES_URL}/{POLICY_ID}/users/{USER_ID}/requests").mock(
        return_value=Response(200, json=DETAILS_PAYLOAD)
    )
    patch_route = respx.patch(f"{requests_url}/{REQUEST_ID}").mock(return_value=Response(200, json=REQUEST_PAYLOAD))
    delete_route = respx.delete(f"{requests_url}/{REQUEST_ID}").mock(return_value=Response(200, json=REQUEST_PAYLOAD))
    requests = _client().workspace(WORKSPACE_ID).time_off_requests
    decision = TimeOffRequestStatusUpdate(status=TimeOffRequestDecision.APPROVED, note="enjoy")
    # Act
    results = (
        requests.create(POLICY_ID, REQUEST_CREATE, time_view_mode="AGGREGATED_TIME_VIEW"),
        requests.create_for_user(POLICY_ID, USER_ID, REQUEST_CREATE),
        requests.update_status(POLICY_ID, REQUEST_ID, decision, time_view_mode="TIME_SENSITIVE_VIEW"),
        requests.delete(POLICY_ID, REQUEST_ID),
    )
    # Assert
    assert results == (DETAILS, DETAILS, REQUEST, REQUEST)
    assert dict(create_route.calls[0].request.url.params) == {"timeViewMode": "AGGREGATED_TIME_VIEW"}
    assert json.loads(create_route.calls[0].request.content) == REQUEST_CREATE_BODY
    assert not for_user_route.calls[0].request.url.params
    assert json.loads(for_user_route.calls[0].request.content) == REQUEST_CREATE_BODY
    assert dict(patch_route.calls[0].request.url.params) == {"timeViewMode": "TIME_SENSITIVE_VIEW"}
    assert json.loads(patch_route.calls[0].request.content) == {"status": "APPROVED", "note": "enjoy"}
    assert not delete_route.calls[0].request.content
    assert [
        r.calls[0].request.extensions.get(CQS) for r in (create_route, for_user_route, patch_route, delete_route)
    ] == [
        CqsKind.NON_IDEMPOTENT_COMMAND,
        CqsKind.NON_IDEMPOTENT_COMMAND,
        CqsKind.IDEMPOTENT_COMMAND,
        CqsKind.IDEMPOTENT_COMMAND,
    ]


async def test_async_requests_list_create_for_user_update_status_and_delete() -> None:
    # Arrange
    with respx.mock:
        requests_url = f"{POLICIES_URL}/{POLICY_ID}/requests"
        list_route = respx.post(f"{TIME_OFF_URL}/requests").mock(
            return_value=Response(200, json={"count": 1, "requests": [DETAILS_PAYLOAD]})
        )
        create_route = respx.post(requests_url).mock(return_value=Response(200, json=DETAILS_PAYLOAD))
        for_user_route = respx.post(f"{POLICIES_URL}/{POLICY_ID}/users/{USER_ID}/requests").mock(
            return_value=Response(200, json=DETAILS_PAYLOAD)
        )
        patch_route = respx.patch(f"{requests_url}/{REQUEST_ID}").mock(
            return_value=Response(200, json=REQUEST_PAYLOAD)
        )
        delete_route = respx.delete(f"{requests_url}/{REQUEST_ID}").mock(
            return_value=Response(200, json=REQUEST_PAYLOAD)
        )
        transport = AsyncTransport(_config(), BASE_URL, ApiKeyAuth("dummy"))
        requests = AsyncTimeOffRequestsResource(transport, WORKSPACE_ID, page_size=5)
        decision = TimeOffRequestStatusUpdate(status=TimeOffRequestDecision.REJECTED)
        # Act
        listed = [item async for item in requests.list(request_filter=TimeOffRequestFilter(users=[USER_ID]))]
        created = await requests.create(POLICY_ID, REQUEST_CREATE, time_view_mode="AGGREGATED_TIME_VIEW")
        for_user = await requests.create_for_user(POLICY_ID, USER_ID, REQUEST_CREATE)
        updated = await requests.update_status(POLICY_ID, REQUEST_ID, decision)
        deleted = await requests.delete(POLICY_ID, REQUEST_ID, time_view_mode="TIME_SENSITIVE_VIEW")
        # Assert
        assert (listed, created, for_user, updated, deleted) == ([DETAILS], DETAILS, DETAILS, REQUEST, REQUEST)
        assert json.loads(list_route.calls[0].request.content) == {"users": [str(USER_ID)], "page": 1, "pageSize": 5}
        assert list_route.calls[0].request.extensions.get(CQS) == CqsKind.QUERY
        assert dict(create_route.calls[0].request.url.params) == {"timeViewMode": "AGGREGATED_TIME_VIEW"}
        assert json.loads(for_user_route.calls[0].request.content) == REQUEST_CREATE_BODY
        assert json.loads(patch_route.calls[0].request.content) == {"status": "REJECTED"}
        assert dict(delete_route.calls[0].request.url.params) == {"timeViewMode": "TIME_SENSITIVE_VIEW"}
        await transport.aclose()


# --- balances -------------------------------------------------------------------------


@respx.mock
def test_balances_list_for_policy_and_user_page_send_sort_and_page_params() -> None:
    # Arrange
    policy_route = respx.get(f"{BALANCE_URL}/policy/{POLICY_ID}").mock(
        return_value=Response(200, json={"count": 1, "balances": [BALANCE_PAYLOAD]})
    )
    user_route = respx.get(f"{BALANCE_URL}/user/{USER_ID}").mock(return_value=Response(200, json={"count": 0}))
    balances = _client().workspace(WORKSPACE_ID).time_off_balances
    balance_filter = TimeOffBalanceFilter(
        sort_column=TimeOffBalanceSortColumn.USED, sort_order=ApprovalSortOrder.ASCENDING
    )
    # Act
    by_policy = balances.list_for_policy_page(POLICY_ID, balance_filter=balance_filter, page=2, page_size=5)
    by_user = balances.list_for_user_page(USER_ID)
    # Assert
    assert policy_route.calls[0].request.url.params.multi_items() == [
        ("sort", "USED"),
        ("sort-order", "ASCENDING"),
        ("page", "2"),
        ("page-size", "5"),
    ]
    assert by_policy.items == [BALANCE]
    assert user_route.calls[0].request.url.params.multi_items() == [("page", "1"), ("page-size", "200")]
    assert by_user.items == []
    assert policy_route.calls[0].request.extensions.get(CQS) == CqsKind.QUERY


@respx.mock
def test_balances_list_auto_paginate() -> None:
    # Arrange
    policy_route = respx.get(f"{BALANCE_URL}/policy/{POLICY_ID}").mock(
        side_effect=[
            Response(200, json={"balances": [BALANCE_PAYLOAD, BALANCE_PAYLOAD]}),
            Response(200, json={"balances": [BALANCE_PAYLOAD]}),
        ]
    )
    user_route = respx.get(f"{BALANCE_URL}/user/{USER_ID}").mock(
        return_value=Response(200, json={"balances": [BALANCE_PAYLOAD]})
    )
    transport = Transport(_config(), BASE_URL, ApiKeyAuth("dummy"))
    balances = TimeOffBalancesResource(transport, WORKSPACE_ID, page_size=2)
    # Act
    by_policy = list(balances.list_for_policy(POLICY_ID))
    by_user = list(balances.list_for_user(USER_ID))
    # Assert
    assert by_policy == [BALANCE, BALANCE, BALANCE]
    assert [call.request.url.params["page"] for call in policy_route.calls] == ["1", "2"]
    assert by_user == [BALANCE]
    assert user_route.call_count == 1
    transport.close()


@respx.mock
def test_balance_changes_are_non_idempotent_commands_and_send_dates_as_plain_dates() -> None:
    # Arrange
    update_route = respx.patch(f"{BALANCE_URL}/policy/{POLICY_ID}").mock(return_value=Response(204))
    create_route = respx.post(f"{BALANCE_URL}/assignment").mock(return_value=Response(201))
    item_url = f"{BALANCE_URL}/assignment/{ASSIGNMENT_ID}/user/{USER_ID}/policy/{POLICY_ID}"
    put_route = respx.put(item_url).mock(return_value=Response(204))
    delete_route = respx.delete(item_url).mock(return_value=Response(200))
    balances = _client().workspace(WORKSPACE_ID).time_off_balances
    # Act
    results = (
        balances.update(
            POLICY_ID,
            TimeOffBalanceUpdate(user_ids=[USER_ID], value=2.5, date_range=DATE_RANGE, note="bonus", sync=True),
        ),
        balances.create_assignment(
            TimeOffBalanceAssignmentCreate(
                policy_id=POLICY_ID, user_ids=[USER_ID], balance=10.0, date_range=DATE_RANGE
            )
        ),
        balances.update_assignment(
            ASSIGNMENT_ID, USER_ID, POLICY_ID, TimeOffBalanceAssignmentUpdate(balance_change=-1.0, note="fix")
        ),
        balances.delete_assignment(
            ASSIGNMENT_ID, USER_ID, POLICY_ID, TimeOffBalanceAssignmentDelete(note="wrong user")
        ),
    )
    # Assert
    assert results == (None, None, None, None)
    assert json.loads(update_route.calls[0].request.content) == {
        "userIds": [str(USER_ID)],
        "value": 2.5,
        "dateRange": DATE_RANGE_BODY,
        "note": "bonus",
        "sync": True,
    }
    assert json.loads(create_route.calls[0].request.content) == {
        "policyId": str(POLICY_ID),
        "userIds": [str(USER_ID)],
        "balance": 10.0,
        "dateRange": DATE_RANGE_BODY,
    }
    assert json.loads(put_route.calls[0].request.content) == {"balanceChange": -1.0, "note": "fix"}
    assert json.loads(delete_route.calls[0].request.content) == {"note": "wrong user"}
    assert [r.calls[0].request.extensions.get(CQS) for r in (update_route, create_route, put_route, delete_route)] == [
        CqsKind.NON_IDEMPOTENT_COMMAND,
        CqsKind.NON_IDEMPOTENT_COMMAND,
        CqsKind.NON_IDEMPOTENT_COMMAND,
        CqsKind.IDEMPOTENT_COMMAND,
    ]


@respx.mock
def test_balances_list_assignments_returns_every_assignment() -> None:
    # Arrange
    route = respx.get(f"{BALANCE_URL}/assignment/user/{USER_ID}/policy/{POLICY_ID}").mock(
        return_value=Response(200, json=[ASSIGNMENT_PAYLOAD])
    )
    client = _client()
    # Act
    assignments = list(client.workspace(WORKSPACE_ID).time_off_balances.list_assignments(USER_ID, POLICY_ID))
    # Assert
    assert not route.calls[0].request.url.params
    assert _last_cqs() == CqsKind.QUERY
    assert assignments == [ASSIGNMENT]
    client.close()


async def test_async_balances_read_and_change() -> None:
    # Arrange
    with respx.mock:
        policy_route = respx.get(f"{BALANCE_URL}/policy/{POLICY_ID}").mock(
            side_effect=[
                Response(200, json={"balances": [BALANCE_PAYLOAD, BALANCE_PAYLOAD]}),
                Response(200, json={"balances": []}),
            ]
        )
        user_route = respx.get(f"{BALANCE_URL}/user/{USER_ID}").mock(
            return_value=Response(200, json={"balances": [BALANCE_PAYLOAD]})
        )
        assignments_route = respx.get(f"{BALANCE_URL}/assignment/user/{USER_ID}/policy/{POLICY_ID}").mock(
            return_value=Response(200, json=[ASSIGNMENT_PAYLOAD])
        )
        update_route = respx.patch(f"{BALANCE_URL}/policy/{POLICY_ID}").mock(return_value=Response(204))
        create_route = respx.post(f"{BALANCE_URL}/assignment").mock(return_value=Response(201))
        item_url = f"{BALANCE_URL}/assignment/{ASSIGNMENT_ID}/user/{USER_ID}/policy/{POLICY_ID}"
        put_route = respx.put(item_url).mock(return_value=Response(204))
        delete_route = respx.delete(item_url).mock(return_value=Response(200))
        transport = AsyncTransport(_config(), BASE_URL, ApiKeyAuth("dummy"))
        balances = AsyncTimeOffBalancesResource(transport, WORKSPACE_ID, page_size=2)
        # Act
        by_policy = [balance async for balance in balances.list_for_policy(POLICY_ID)]
        by_user = [balance async for balance in balances.list_for_user(USER_ID)]
        page = await balances.list_for_user_page(USER_ID, balance_filter=TimeOffBalanceFilter(), page_size=1)
        assignments = [item async for item in balances.list_assignments(USER_ID, POLICY_ID)]
        await balances.update(POLICY_ID, TimeOffBalanceUpdate(user_ids=[USER_ID], value=1.0))
        await balances.create_assignment(
            TimeOffBalanceAssignmentCreate(policy_id=POLICY_ID, user_ids=[USER_ID], balance=2.0)
        )
        await balances.update_assignment(
            ASSIGNMENT_ID, USER_ID, POLICY_ID, TimeOffBalanceAssignmentUpdate(balance_change=3.0)
        )
        await balances.delete_assignment(ASSIGNMENT_ID, USER_ID, POLICY_ID, TimeOffBalanceAssignmentDelete(note="x"))
        # Assert
        assert by_policy == [BALANCE, BALANCE]
        assert [call.request.url.params["page"] for call in policy_route.calls] == ["1", "2"]
        assert by_user == [BALANCE]
        assert page.items == [BALANCE]
        assert user_route.call_count == 2
        assert assignments == [ASSIGNMENT]
        assert assignments_route.calls[0].request.extensions.get(CQS) == CqsKind.QUERY
        assert json.loads(update_route.calls[0].request.content) == {"userIds": [str(USER_ID)], "value": 1.0}
        assert json.loads(create_route.calls[0].request.content) == {
            "policyId": str(POLICY_ID),
            "userIds": [str(USER_ID)],
            "balance": 2.0,
        }
        assert json.loads(put_route.calls[0].request.content) == {"balanceChange": 3.0}
        assert json.loads(delete_route.calls[0].request.content) == {"note": "x"}
        assert update_route.calls[0].request.extensions.get(CQS) == CqsKind.NON_IDEMPOTENT_COMMAND
        assert delete_route.calls[0].request.extensions.get(CQS) == CqsKind.IDEMPOTENT_COMMAND
        await transport.aclose()


# --- models ---------------------------------------------------------------------------


def test_unknown_enum_values_fall_back_to_unknown() -> None:
    # Arrange
    payload = {"id": "p", "icon": "ROCKET", "timeUnit": "WEEKS", "status": {"statusType": "ON_HOLD"}}
    # Act
    policy = TimeOffPolicy.model_validate(payload)
    status = TimeOffRequestStatus.model_validate(payload["status"])
    # Assert
    assert (policy.icon, policy.time_unit) == (TimeOffPolicyIcon.UNKNOWN, TimeOffUnit.UNKNOWN)
    assert status.status_type is TimeOffRequestStatusType.UNKNOWN


async def test_async_client_exposes_the_three_time_off_resources() -> None:
    # Arrange
    client = _async_client()
    # Act
    workspace = client.workspace(WORKSPACE_ID)
    # Assert
    assert isinstance(workspace.time_off_policies, AsyncTimeOffPoliciesResource)
    assert isinstance(workspace.time_off_requests, AsyncTimeOffRequestsResource)
    assert isinstance(workspace.time_off_balances, AsyncTimeOffBalancesResource)
    await client.aclose()
