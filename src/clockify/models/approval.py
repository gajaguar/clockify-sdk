from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from clockify._time import ClockifyDuration
from clockify._time import ClockifyInstant
from clockify.ids import ApprovalRequestId
from clockify.ids import ClientId
from clockify.ids import ProjectId
from clockify.ids import TaskId
from clockify.ids import TimeEntryId
from clockify.ids import UserId
from clockify.ids import WorkspaceId
from clockify.models.base import ClockifyModel
from clockify.models.tag import Tag
from clockify.models.time_entry import CustomFieldValue
from clockify.models.time_entry import TimeEntryType
from clockify.models.time_entry import TimeInterval
from clockify.models.workspace import Rate


class ApprovalRequestType(StrEnum):
    TIMESHEET = "TIMESHEET"
    EXPENSE = "EXPENSE"
    TIMESHEET_AND_EXPENSE = "TIMESHEET_AND_EXPENSE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> ApprovalRequestType:
        del value
        return cls.UNKNOWN


class ApprovalState(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    WITHDRAWN_SUBMISSION = "WITHDRAWN_SUBMISSION"
    WITHDRAWN_APPROVAL = "WITHDRAWN_APPROVAL"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> ApprovalState:
        del value
        return cls.UNKNOWN


class ApprovalPeriod(StrEnum):
    WEEKLY = "WEEKLY"
    SEMI_MONTHLY = "SEMI_MONTHLY"
    MONTHLY = "MONTHLY"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> ApprovalPeriod:
        del value
        return cls.UNKNOWN


class ApprovalSortColumn(StrEnum):
    ID = "ID"
    USER_ID = "USER_ID"
    START = "START"
    UPDATED_AT = "UPDATED_AT"


class ApprovalSortOrder(StrEnum):
    ASCENDING = "ASCENDING"
    DESCENDING = "DESCENDING"


class ApprovalRequestCreator(ClockifyModel):
    user_id: UserId | None = None
    user_name: str | None = None
    user_email: str | None = None


class ApprovalRequestOwner(ClockifyModel):
    user_id: UserId | None = None
    user_name: str | None = None
    time_zone: str | None = None
    start_of_week: str | None = None


class ApprovalDateRange(ClockifyModel):
    start: ClockifyInstant | None = None
    end: ClockifyInstant | None = None


class ApprovalRequestStatus(ClockifyModel):
    state: ApprovalState | None = None
    note: str | None = None
    updated_at: ClockifyInstant | None = None
    updated_by: UserId | None = None
    updated_by_user_name: str | None = None


class ApprovalRequest(ClockifyModel):
    id: ApprovalRequestId
    workspace_id: WorkspaceId | None = None
    type: ApprovalRequestType | None = None
    status: ApprovalRequestStatus | None = None
    owner: ApprovalRequestOwner | None = None
    creator: ApprovalRequestCreator | None = None
    date_range: ApprovalDateRange | None = None


class ApprovalProjectInfo(ClockifyModel):
    id: ProjectId | None = None
    name: str | None = None
    client_id: ClientId | None = None
    client_name: str | None = None
    color: str | None = None


class ApprovalTaskInfo(ClockifyModel):
    id: TaskId | None = None
    name: str | None = None


class ApprovalTimeEntry(ClockifyModel):
    id: TimeEntryId
    approval_request_id: ApprovalRequestId | None = None
    description: str | None = None
    billable: bool | None = None
    is_locked: bool | None = None
    type: TimeEntryType | None = None
    time_interval: TimeInterval | None = None
    project: ApprovalProjectInfo | None = None
    task: ApprovalTaskInfo | None = None
    tags: list[Tag] | None = None
    hourly_rate: Rate | None = None
    cost_rate: Rate | None = None
    custom_field_values: list[CustomFieldValue] | None = None


# `category` stays an extra field so its type does not change in a minor release; it has
# the shape of clockify.models.expense.ExpenseCategory and
# ExpenseCategory.model_validate(expense.model_extra["category"]) reads it.
class ApprovalExpense(ClockifyModel):
    id: str
    approval_request_id: ApprovalRequestId | None = None
    user_id: UserId | None = None
    workspace_id: WorkspaceId | None = None
    date: str | None = None
    total: float | None = None
    quantity: float | None = None
    currency: str | None = None
    billable: bool | None = None
    notes: str | None = None
    approval_status: str | None = None
    project: ApprovalProjectInfo | None = None
    task: ApprovalTaskInfo | None = None


class ApprovalDetails(ClockifyModel):
    approval_request: ApprovalRequest | None = None
    entries: list[ApprovalTimeEntry] | None = None
    expenses: list[ApprovalExpense] | None = None
    tracked_time: ClockifyDuration | None = None
    approved_time: ClockifyDuration | None = None
    pending_time: ClockifyDuration | None = None
    billable_time: ClockifyDuration | None = None
    break_time: ClockifyDuration | None = None
    billable_amount: float | None = None
    cost_amount: float | None = None
    expense_total: float | None = None


class ApprovalRequestCreate(ClockifyModel):
    period_start: ClockifyInstant
    period: ApprovalPeriod | None = None


class ApprovalRequestResubmit(ClockifyModel):
    period_start: ClockifyInstant
    period: ApprovalPeriod | None = None
    type: ApprovalRequestType | None = None


class ApprovalRequestUpdate(ClockifyModel):
    state: ApprovalState
    note: str | None = None


@dataclass(frozen=True, slots=True)
class ApprovalRequestFilter:
    # Parameter Object for the .../approval-requests query filters. A dataclass rather
    # than a pydantic model for the same reason as TimeEntryFilter: the wire names are
    # kebab-case, so ClockifyModel's camelCase alias generator does not apply.
    status: ApprovalState | None = None
    sort_column: ApprovalSortColumn | None = None
    sort_order: ApprovalSortOrder | None = None
    types: list[ApprovalRequestType] | None = None

    def as_params(self) -> dict[str, str | list[str]]:
        params: dict[str, str | list[str]] = {}
        if self.status is not None:
            params["status"] = str(self.status)
        if self.sort_column is not None:
            params["sort-column"] = str(self.sort_column)
        if self.sort_order is not None:
            params["sort-order"] = str(self.sort_order)
        if self.types is not None:
            params["types"] = [str(approval_type) for approval_type in self.types]
        return params
