from __future__ import annotations

import datetime
from typing import Final

import pytest

from clockify import ApprovalDetails
from clockify import ApprovalPeriod
from clockify import ApprovalRequest
from clockify import ApprovalRequestCreate
from clockify import ApprovalRequestFilter
from clockify import ApprovalRequestResubmit
from clockify import ApprovalRequestType
from clockify import ApprovalRequestUpdate
from clockify import ApprovalSortColumn
from clockify import ApprovalSortOrder
from clockify import ApprovalState

REQUEST_PAYLOAD: Final = {
    "id": "6a0000000000000000000001",
    "workspaceId": "64a1f0000000000000000001",
    "type": "TIMESHEET",
    "status": {
        "state": "PENDING",
        "note": "please review",
        "updatedAt": "2026-09-28T10:00:00Z",
        "updatedBy": "5a0ab5acb07987125438b60f",
        "updatedByUserName": "Some One",
    },
    "owner": {
        "userId": "5a0ab5acb07987125438b60f",
        "userName": "Some One",
        "timeZone": "UTC",
        "startOfWeek": "MONDAY",
    },
    "creator": {"userId": "5a0ab5acb07987125438b60f", "userName": "Some One", "userEmail": "someone@example.com"},
    "dateRange": {"start": "2026-09-28T00:00:00Z", "end": "2026-10-04T23:59:59Z"},
}
DETAILS_PAYLOAD: Final = {
    "approvalRequest": REQUEST_PAYLOAD,
    "trackedTime": "PT8H",
    "approvedTime": "PT0S",
    "billableTime": "PT7H30M",
    "billableAmount": 112.5,
    "expenseTotal": 20.0,
    "entries": [
        {
            "id": "6a0000000000000000000002",
            "description": "work",
            "billable": True,
            "isLocked": False,
            "type": "REGULAR",
            "timeInterval": {"start": "2026-09-28T09:00:00Z", "end": "2026-09-28T17:00:00Z", "duration": "PT8H"},
            "project": {"id": "6a0000000000000000000003", "name": "Apollo", "clientName": "ACME"},
            "tags": [{"id": "6a0000000000000000000004", "name": "dev", "workspaceId": "64a1f0000000000000000001"}],
        }
    ],
    "expenses": [{"id": "6a0000000000000000000005", "total": 20.0, "currency": "USD", "category": {"name": "Taxi"}}],
}


def test_approval_request_parses_nested_objects() -> None:
    # Arrange
    # Act
    request = ApprovalRequest.model_validate(REQUEST_PAYLOAD)
    # Assert
    assert request.type is ApprovalRequestType.TIMESHEET
    assert request.status is not None
    assert request.status.state is ApprovalState.PENDING
    assert request.status.updated_at == datetime.datetime(2026, 9, 28, 10, tzinfo=datetime.UTC)
    assert request.owner is not None
    assert request.owner.start_of_week == "MONDAY"
    assert request.creator is not None
    assert request.creator.user_email == "someone@example.com"
    assert request.date_range is not None
    assert request.date_range.end == datetime.datetime(2026, 10, 4, 23, 59, 59, tzinfo=datetime.UTC)


def test_approval_details_parses_durations_entries_and_expenses() -> None:
    # Arrange
    # Act
    details = ApprovalDetails.model_validate(DETAILS_PAYLOAD)
    # Assert
    assert details.approval_request is not None
    assert details.approval_request.id == "6a0000000000000000000001"
    assert details.tracked_time == datetime.timedelta(hours=8)
    assert details.billable_time == datetime.timedelta(hours=7, minutes=30)
    assert details.billable_amount == pytest.approx(112.5)
    assert details.entries is not None
    assert details.entries[0].time_interval is not None
    assert details.entries[0].time_interval.duration == datetime.timedelta(hours=8)
    assert details.entries[0].project is not None
    assert details.entries[0].project.client_name == "ACME"
    assert details.entries[0].tags is not None
    assert details.entries[0].tags[0].name == "dev"
    assert details.expenses is not None
    assert details.expenses[0].total == pytest.approx(20.0)


def test_approval_details_tolerates_an_empty_object() -> None:
    # Arrange
    # Act
    details = ApprovalDetails.model_validate({})
    # Assert
    assert details.approval_request is None
    assert details.entries is None


@pytest.mark.parametrize(
    ("enum", "value"),
    [(ApprovalState, "SOMETHING_NEW"), (ApprovalRequestType, "SOMETHING_NEW"), (ApprovalPeriod, "SOMETHING_NEW")],
)
def test_unknown_enum_value_falls_back_to_unknown(enum: type[ApprovalState], value: str) -> None:
    # Arrange
    # Act
    parsed = enum(value)
    # Assert
    assert parsed.value == "UNKNOWN"


def test_create_dumps_only_the_fields_that_were_set() -> None:
    # Arrange
    payload = ApprovalRequestCreate(
        period_start=datetime.datetime(2026, 9, 28, tzinfo=datetime.UTC), period=ApprovalPeriod.WEEKLY
    )
    # Act
    body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
    # Assert
    assert body == {"periodStart": "2026-09-28T00:00:00Z", "period": "WEEKLY"}


def test_create_without_period_omits_it() -> None:
    # Arrange
    payload = ApprovalRequestCreate(period_start=datetime.datetime(2026, 9, 28, tzinfo=datetime.UTC))
    # Act
    body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
    # Assert
    assert body == {"periodStart": "2026-09-28T00:00:00Z"}


def test_resubmit_dumps_the_type() -> None:
    # Arrange
    payload = ApprovalRequestResubmit(
        period_start=datetime.datetime(2026, 9, 28, tzinfo=datetime.UTC), type=ApprovalRequestType.EXPENSE
    )
    # Act
    body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
    # Assert
    assert body == {"periodStart": "2026-09-28T00:00:00Z", "type": "EXPENSE"}


def test_update_dumps_state_and_note() -> None:
    # Arrange
    payload = ApprovalRequestUpdate(state=ApprovalState.REJECTED, note="missing hours")
    # Act
    body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
    # Assert
    assert body == {"state": "REJECTED", "note": "missing hours"}


def test_empty_filter_has_no_params() -> None:
    # Arrange
    # Act
    params = ApprovalRequestFilter().as_params()
    # Assert
    assert params == {}


def test_full_filter_uses_the_wire_names() -> None:
    # Arrange
    request_filter = ApprovalRequestFilter(
        status=ApprovalState.PENDING,
        sort_column=ApprovalSortColumn.UPDATED_AT,
        sort_order=ApprovalSortOrder.DESCENDING,
        types=[ApprovalRequestType.TIMESHEET, ApprovalRequestType.EXPENSE],
    )
    # Act
    params = request_filter.as_params()
    # Assert
    assert params == {
        "status": "PENDING",
        "sort-column": "UPDATED_AT",
        "sort-order": "DESCENDING",
        "types": ["TIMESHEET", "EXPENSE"],
    }
