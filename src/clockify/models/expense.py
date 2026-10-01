from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from clockify._time import ClockifyInstant
from clockify.ids import ExpenseCategoryId
from clockify.ids import ExpenseId
from clockify.ids import ProjectId
from clockify.ids import TaskId
from clockify.ids import UserId
from clockify.ids import WorkspaceId
from clockify.models.approval import ApprovalProjectInfo
from clockify.models.approval import ApprovalSortOrder
from clockify.models.approval import ApprovalTaskInfo
from clockify.models.base import ClockifyModel

# None of these models has been checked against a real Clockify response: Expenses is a
# Pro-plan feature and the account used to build the SDK is on the Free plan. They follow
# the OpenAPI spec, with every doubtful field optional.


class ExpenseCategorySortColumn(StrEnum):
    NAME = "NAME"


class ExpenseChangeField(StrEnum):
    USER = "USER"
    DATE = "DATE"
    PROJECT = "PROJECT"
    TASK = "TASK"
    CATEGORY = "CATEGORY"
    NOTES = "NOTES"
    AMOUNT = "AMOUNT"
    BILLABLE = "BILLABLE"
    FILE = "FILE"


class ExpenseCategory(ClockifyModel):
    id: ExpenseCategoryId
    workspace_id: WorkspaceId | None = None
    name: str | None = None
    archived: bool | None = None
    has_unit_price: bool | None = None
    price_in_cents: int | None = None
    unit: str | None = None


class ExpenseCategoryList(ClockifyModel):
    categories: list[ExpenseCategory] | None = None
    count: int | None = None


class ExpenseCategoryCreate(ClockifyModel):
    name: str
    has_unit_price: bool | None = None
    price_in_cents: int | None = None
    unit: str | None = None


class ExpenseCategoryUpdate(ClockifyModel):
    name: str
    has_unit_price: bool | None = None
    price_in_cents: int | None = None
    unit: str | None = None


class ExpenseCategoryStatusUpdate(ClockifyModel):
    archived: bool


@dataclass(frozen=True, slots=True)
class ExpenseCategoryFilter:
    # Parameter Object for the .../expenses/categories query filters; a dataclass for the
    # same reason as ApprovalRequestFilter (kebab-case wire names).
    archived: bool | None = None
    name: str | None = None
    sort_column: ExpenseCategorySortColumn | None = None
    sort_order: ApprovalSortOrder | None = None

    def as_params(self) -> dict[str, str | bool]:
        params: dict[str, str | bool] = {}
        if self.archived is not None:
            params["archived"] = self.archived
        if self.name is not None:
            params["name"] = self.name
        if self.sort_column is not None:
            params["sort-column"] = str(self.sort_column)
        if self.sort_order is not None:
            params["sort-order"] = str(self.sort_order)
        return params


class Expense(ClockifyModel):
    id: ExpenseId
    workspace_id: WorkspaceId | None = None
    user_id: UserId | None = None
    category_id: ExpenseCategoryId | None = None
    project_id: ProjectId | None = None
    task_id: TaskId | None = None
    date: str | None = None
    total: float | None = None
    quantity: float | None = None
    billable: bool | None = None
    locked: bool | None = None
    notes: str | None = None
    file_id: str | None = None


class ExpenseDetails(ClockifyModel):
    id: ExpenseId
    workspace_id: WorkspaceId | None = None
    user_id: UserId | None = None
    category: ExpenseCategory | None = None
    project: ApprovalProjectInfo | None = None
    task: ApprovalTaskInfo | None = None
    date: str | None = None
    total: float | None = None
    quantity: float | None = None
    billable: bool | None = None
    locked: bool | None = None
    notes: str | None = None
    file_id: str | None = None
    file_name: str | None = None


class ExpensesWithCount(ClockifyModel):
    count: int | None = None
    expenses: list[ExpenseDetails] | None = None


class ExpenseDailyTotal(ClockifyModel):
    date: str | None = None
    date_as_instant: ClockifyInstant | None = None
    total: float | None = None


class ExpenseWeeklyTotal(ClockifyModel):
    date: str | None = None
    total: float | None = None


class ExpenseList(ClockifyModel):
    expenses: ExpensesWithCount | None = None
    daily_totals: list[ExpenseDailyTotal] | None = None
    weekly_totals: list[ExpenseWeeklyTotal] | None = None


@dataclass(frozen=True, slots=True)
class ExpenseFile:
    # Bytes, not a stream: the retry transport resends the same request after a 429 or a
    # 5xx, and a consumed stream cannot be replayed.
    filename: str
    content: bytes
    content_type: str | None = None


class ExpenseCreate(ClockifyModel):
    user_id: UserId
    category_id: ExpenseCategoryId
    project_id: ProjectId
    date: ClockifyInstant
    amount: float
    task_id: TaskId | None = None
    billable: bool | None = None
    notes: str | None = None
    # The spec marks the file required; kept optional because it cannot be checked live.
    file: ExpenseFile | None = None


class ExpenseUpdate(ClockifyModel):
    user_id: UserId
    category_id: ExpenseCategoryId
    date: ClockifyInstant
    amount: float
    change_fields: list[ExpenseChangeField]
    project_id: ProjectId | None = None
    task_id: TaskId | None = None
    billable: bool | None = None
    notes: str | None = None
    file: ExpenseFile | None = None
