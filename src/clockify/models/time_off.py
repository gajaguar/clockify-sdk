from __future__ import annotations

import datetime
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING
from typing import Any

from clockify._time import ClockifyInstant
from clockify._time import format_instant
from clockify.ids import ProjectId
from clockify.ids import TaskId
from clockify.ids import TimeOffBalanceAssignmentId
from clockify.ids import TimeOffBalanceId
from clockify.ids import TimeOffPolicyId
from clockify.ids import TimeOffRequestId
from clockify.ids import UserGroupId
from clockify.ids import UserId
from clockify.ids import WorkspaceId
from clockify.models.base import ClockifyModel

if TYPE_CHECKING:
    from clockify.models.approval import ApprovalSortOrder

# None of these models has been checked against a real Clockify response: Time off is a
# Standard-plan feature and the account used to build the SDK is on the Free plan. They
# follow the OpenAPI spec, with every doubtful field optional.


class TimeOffUnit(StrEnum):
    DAYS = "DAYS"
    HOURS = "HOURS"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> TimeOffUnit:
        del value
        return cls.UNKNOWN


class TimeOffPolicyIcon(StrEnum):
    UMBRELLA = "UMBRELLA"
    SNOWFLAKE = "SNOWFLAKE"
    FAMILY = "FAMILY"
    PLANE = "PLANE"
    STETHOSCOPE = "STETHOSCOPE"
    HEALTH_METRICS = "HEALTH_METRICS"
    CHILDCARE = "CHILDCARE"
    LUGGAGE = "LUGGAGE"
    MONETIZATION = "MONETIZATION"
    CALENDAR = "CALENDAR"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> TimeOffPolicyIcon:
        del value
        return cls.UNKNOWN


class TimeOffAccrualPeriod(StrEnum):
    MONTH = "MONTH"
    YEAR = "YEAR"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> TimeOffAccrualPeriod:
        del value
        return cls.UNKNOWN


class TimeOffRequestStatusType(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ALL = "ALL"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> TimeOffRequestStatusType:
        del value
        return cls.UNKNOWN


class TimeOffPolicyStatus(StrEnum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    ALL = "ALL"


class TimeOffHalfDayPeriod(StrEnum):
    FIRST_HALF = "FIRST_HALF"
    SECOND_HALF = "SECOND_HALF"
    NOT_DEFINED = "NOT_DEFINED"


class TimeOffRequestDecision(StrEnum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class TimeOffBalanceSortColumn(StrEnum):
    USER = "USER"
    POLICY = "POLICY"
    USED = "USED"
    BALANCE = "BALANCE"
    TOTAL = "TOTAL"


class TimeOffMemberFilterContains(StrEnum):
    CONTAINS = "CONTAINS"
    DOES_NOT_CONTAIN = "DOES_NOT_CONTAIN"


class TimeOffMemberFilterStatus(StrEnum):
    ALL = "ALL"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class TimeOffPolicyApproval(ClockifyModel):
    requires_approval: bool | None = None
    specific_members: bool | None = None
    team_managers: bool | None = None
    user_ids: list[UserId] | None = None


class TimeOffAutomaticAccrual(ClockifyModel):
    amount: float | None = None
    period: TimeOffAccrualPeriod | None = None
    time_unit: TimeOffUnit | None = None


class TimeOffDefaultEntities(ClockifyModel):
    project_id: ProjectId | None = None
    task_id: TaskId | None = None


class TimeOffAutomaticTimeEntryCreation(ClockifyModel):
    default_entities: TimeOffDefaultEntities | None = None
    enabled: bool | None = None


# `period` and `time_unit` are plain strings here: the spec gives them no enum.
class TimeOffNegativeBalance(ClockifyModel):
    amount: float | None = None
    period: str | None = None
    should_reset: bool | None = None
    time_unit: str | None = None


class TimeOffPolicy(ClockifyModel):
    id: TimeOffPolicyId
    workspace_id: WorkspaceId | None = None
    name: str | None = None
    archived: bool | None = None
    color: str | None = None
    icon: TimeOffPolicyIcon | None = None
    time_unit: TimeOffUnit | None = None
    allow_half_day: bool | None = None
    allow_negative_balance: bool | None = None
    everyone_including_new: bool | None = None
    approve: TimeOffPolicyApproval | None = None
    automatic_accrual: TimeOffAutomaticAccrual | None = None
    automatic_time_entry_creation: TimeOffAutomaticTimeEntryCreation | None = None
    negative_balance: TimeOffNegativeBalance | None = None
    project_id: ProjectId | None = None
    user_ids: list[UserId] | None = None
    user_group_ids: list[UserGroupId] | None = None


class TimeOffAutomaticAccrualRequest(ClockifyModel):
    amount: float
    period: TimeOffAccrualPeriod | None = None


class TimeOffDefaultEntitiesRequest(ClockifyModel):
    project_id: ProjectId | None = None
    task_id: TaskId | None = None


class TimeOffAutomaticTimeEntryCreationRequest(ClockifyModel):
    default_entities: TimeOffDefaultEntitiesRequest
    enabled: bool | None = None


class TimeOffNegativeBalanceRequest(ClockifyModel):
    amount: float
    period: TimeOffAccrualPeriod | None = None
    should_reset: bool | None = None


class TimeOffPolicyMemberFilter(ClockifyModel):
    contains: TimeOffMemberFilterContains | None = None
    ids: list[str] | None = None
    status: TimeOffMemberFilterStatus | None = None


class TimeOffPolicyCreate(ClockifyModel):
    name: str
    approve: TimeOffPolicyApproval
    allow_half_day: bool | None = None
    allow_negative_balance: bool | None = None
    archived: bool | None = None
    automatic_accrual: TimeOffAutomaticAccrualRequest | None = None
    automatic_time_entry_creation: TimeOffAutomaticTimeEntryCreationRequest | None = None
    color: str | None = None
    everyone_including_new: bool | None = None
    has_expiration: bool | None = None
    icon: TimeOffPolicyIcon | None = None
    negative_balance: TimeOffNegativeBalanceRequest | None = None
    time_unit: TimeOffUnit | None = None
    user_groups: TimeOffPolicyMemberFilter | None = None
    users: TimeOffPolicyMemberFilter | None = None


# A PUT replaces the policy, so the spec requires these flags; `time_unit` cannot change.
class TimeOffPolicyUpdate(ClockifyModel):
    name: str
    approve: TimeOffPolicyApproval
    allow_half_day: bool
    allow_negative_balance: bool
    archived: bool
    everyone_including_new: bool
    has_expiration: bool
    automatic_accrual: TimeOffAutomaticAccrualRequest | None = None
    automatic_time_entry_creation: TimeOffAutomaticTimeEntryCreationRequest | None = None
    color: str | None = None
    icon: TimeOffPolicyIcon | None = None
    negative_balance: TimeOffNegativeBalanceRequest | None = None
    user_groups: TimeOffPolicyMemberFilter | None = None
    users: TimeOffPolicyMemberFilter | None = None


class TimeOffPolicyStatusUpdate(ClockifyModel):
    status: TimeOffPolicyStatus


class TimeOffPeriod(ClockifyModel):
    start: ClockifyInstant | None = None
    end: ClockifyInstant | None = None


class TimeOffRequestPeriod(ClockifyModel):
    period: TimeOffPeriod | None = None
    half_day: bool | None = None
    half_day_hours: TimeOffPeriod | None = None
    half_day_period: str | None = None


class TimeOffRequestStatus(ClockifyModel):
    status_type: TimeOffRequestStatusType | None = None
    note: str | None = None
    changed_at: ClockifyInstant | None = None
    changed_at_time_zone: str | None = None
    changed_by_user_id: UserId | None = None
    changed_by_user_name: str | None = None
    changed_for_user_name: str | None = None


class TimeOffRequest(ClockifyModel):
    id: TimeOffRequestId
    workspace_id: WorkspaceId | None = None
    policy_id: TimeOffPolicyId | None = None
    user_id: UserId | None = None
    note: str | None = None
    balance_diff: float | None = None
    created_at: ClockifyInstant | None = None
    status: TimeOffRequestStatus | None = None
    time_off_period: TimeOffRequestPeriod | None = None


class TimeOffRequestDetails(ClockifyModel):
    id: TimeOffRequestId
    workspace_id: WorkspaceId | None = None
    policy_id: TimeOffPolicyId | None = None
    policy_name: str | None = None
    user_id: UserId | None = None
    user_name: str | None = None
    user_email: str | None = None
    user_time_zone: str | None = None
    requester_user_id: UserId | None = None
    requester_user_name: str | None = None
    note: str | None = None
    balance: float | None = None
    balance_diff: float | None = None
    time_unit: TimeOffUnit | None = None
    created_at: ClockifyInstant | None = None
    status: TimeOffRequestStatus | None = None
    time_off_period: TimeOffRequestPeriod | None = None


class TimeOffRequestList(ClockifyModel):
    requests: list[TimeOffRequestDetails] | None = None
    count: int | None = None


class TimeOffPeriodRequest(ClockifyModel):
    start: datetime.date | None = None
    end: datetime.date | None = None
    days: int | None = None


class TimeOffRequestPeriodRequest(ClockifyModel):
    period: TimeOffPeriodRequest
    is_half_day: bool | None = None
    half_day_period: TimeOffHalfDayPeriod | None = None
    time_off_half_day_period: TimeOffHalfDayPeriod | None = None


class TimeOffRequestCreate(ClockifyModel):
    time_off_period: TimeOffRequestPeriodRequest
    note: str | None = None


class TimeOffRequestStatusUpdate(ClockifyModel):
    status: TimeOffRequestDecision | None = None
    note: str | None = None


class TimeOffBalance(ClockifyModel):
    id: TimeOffBalanceId | None = None
    workspace_id: WorkspaceId | None = None
    user_id: UserId | None = None
    user_name: str | None = None
    policy_id: TimeOffPolicyId | None = None
    policy_name: str | None = None
    policy_archived: bool | None = None
    policy_time_unit: TimeOffUnit | None = None
    balance: float | None = None
    total: float | None = None
    used: float | None = None
    negative_balance_amount: float | None = None
    negative_balance_limit: bool | None = None
    negative_balance_used: float | None = None


class TimeOffBalanceList(ClockifyModel):
    balances: list[TimeOffBalance] | None = None
    count: int | None = None


class TimeOffBalanceAssignment(ClockifyModel):
    id: TimeOffBalanceAssignmentId
    workspace_id: WorkspaceId | None = None
    user_id: UserId | None = None
    policy_id: TimeOffPolicyId | None = None
    balance: float | None = None
    accrued: float | None = None
    date_range: TimeOffPeriod | None = None


class TimeOffBalanceDateRange(ClockifyModel):
    start: datetime.date | None = None
    end: datetime.date | None = None


class TimeOffBalanceUpdate(ClockifyModel):
    user_ids: list[UserId]
    value: float
    date_range: TimeOffBalanceDateRange | None = None
    note: str | None = None
    sync: bool | None = None


class TimeOffBalanceAssignmentCreate(ClockifyModel):
    policy_id: TimeOffPolicyId
    user_ids: list[UserId]
    balance: float
    date_range: TimeOffBalanceDateRange | None = None
    note: str | None = None


class TimeOffBalanceAssignmentUpdate(ClockifyModel):
    balance_change: float
    date_range: TimeOffBalanceDateRange | None = None
    note: str | None = None


class TimeOffBalanceAssignmentDelete(ClockifyModel):
    note: str


@dataclass(frozen=True, slots=True)
class TimeOffPolicyFilter:
    # Parameter Object for the .../time-off/policies query filters; a dataclass for the
    # same reason as ApprovalRequestFilter (kebab-case wire names).
    name: str | None = None
    status: TimeOffPolicyStatus | None = None
    sort_column: str | None = None
    sort_order: ApprovalSortOrder | None = None

    def as_params(self) -> dict[str, str]:
        params: dict[str, str] = {}
        if self.name is not None:
            params["name"] = self.name
        if self.status is not None:
            params["status"] = str(self.status)
        if self.sort_column is not None:
            params["sort-column"] = self.sort_column
        if self.sort_order is not None:
            params["sort-order"] = str(self.sort_order)
        return params


@dataclass(frozen=True, slots=True)
class TimeOffBalanceFilter:
    sort_column: TimeOffBalanceSortColumn | None = None
    sort_order: ApprovalSortOrder | None = None

    def as_params(self) -> dict[str, str]:
        params: dict[str, str] = {}
        if self.sort_column is not None:
            params["sort"] = str(self.sort_column)
        if self.sort_order is not None:
            params["sort-order"] = str(self.sort_order)
        return params


@dataclass(frozen=True, slots=True)
class TimeOffRequestFilter:
    # Unlike the other filters this one travels in the body of `POST .../time-off/requests`,
    # which reads despite the verb, so it renders a JSON body rather than query parameters.
    start: datetime.datetime | None = None
    end: datetime.datetime | None = None
    statuses: list[TimeOffRequestStatusType] | None = None
    users: list[UserId] | None = None
    user_groups: list[UserGroupId] | None = None

    def as_body(self) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if self.start is not None:
            body["start"] = format_instant(self.start)
        if self.end is not None:
            body["end"] = format_instant(self.end)
        if self.statuses is not None:
            body["statuses"] = [str(status) for status in self.statuses]
        if self.users is not None:
            body["users"] = [str(user) for user in self.users]
        if self.user_groups is not None:
            body["userGroups"] = [str(group) for group in self.user_groups]
        return body
