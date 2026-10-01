from __future__ import annotations

import datetime
from typing import Final

import pytest

from clockify import ApprovalProjectInfo
from clockify import ApprovalSortOrder
from clockify import ApprovalTaskInfo
from clockify import Expense
from clockify import ExpenseCategory
from clockify import ExpenseCategoryCreate
from clockify import ExpenseCategoryFilter
from clockify import ExpenseCategoryList
from clockify import ExpenseCategorySortColumn
from clockify import ExpenseCategoryStatusUpdate
from clockify import ExpenseChangeField
from clockify import ExpenseCreate
from clockify import ExpenseDailyTotal
from clockify import ExpenseDetails
from clockify import ExpenseFile
from clockify import ExpenseList
from clockify import ExpenseUpdate
from clockify import ExpenseWeeklyTotal
from clockify import ExpensesWithCount

CATEGORY_PAYLOAD: Final = {
    "id": "7c0000000000000000000001",
    "workspaceId": "64a1f0000000000000000001",
    "name": "Travel",
    "archived": False,
    "hasUnitPrice": True,
    "priceInCents": 250,
    "unit": "km",
}
CATEGORY: Final = ExpenseCategory(
    id="7c0000000000000000000001",
    workspace_id="64a1f0000000000000000001",
    name="Travel",
    archived=False,
    has_unit_price=True,
    price_in_cents=250,
    unit="km",
)
EXPENSE_PAYLOAD: Final = {
    "id": "8e0000000000000000000001",
    "workspaceId": "64a1f0000000000000000001",
    "userId": "5a0ab5acb07987125438b60f",
    "categoryId": "7c0000000000000000000001",
    "projectId": "6b0000000000000000000001",
    "taskId": "6d0000000000000000000001",
    "date": "2026-09-30",
    "total": 12.5,
    "quantity": 5.0,
    "billable": True,
    "locked": False,
    "notes": "taxi",
    "fileId": "9f0000000000000000000001",
}
DETAILS_PAYLOAD: Final = {
    "id": "8e0000000000000000000001",
    "workspaceId": "64a1f0000000000000000001",
    "userId": "5a0ab5acb07987125438b60f",
    "category": CATEGORY_PAYLOAD,
    "project": {"id": "6b0000000000000000000001", "name": "Apollo", "clientName": "ACME"},
    "task": {"id": "6d0000000000000000000001", "name": "Ride"},
    "date": "2026-09-30",
    "total": 12.5,
    "billable": True,
    "fileName": "receipt.pdf",
}
DETAILS: Final = ExpenseDetails(
    id="8e0000000000000000000001",
    workspace_id="64a1f0000000000000000001",
    user_id="5a0ab5acb07987125438b60f",
    category=CATEGORY,
    project=ApprovalProjectInfo(id="6b0000000000000000000001", name="Apollo", client_name="ACME"),
    task=ApprovalTaskInfo(id="6d0000000000000000000001", name="Ride"),
    date="2026-09-30",
    total=12.5,
    billable=True,
    file_name="receipt.pdf",
)


def test_expense_parses_the_flat_payload() -> None:
    # Arrange
    # Act
    expense = Expense.model_validate(EXPENSE_PAYLOAD)
    # Assert
    assert expense == Expense(
        id="8e0000000000000000000001",
        workspace_id="64a1f0000000000000000001",
        user_id="5a0ab5acb07987125438b60f",
        category_id="7c0000000000000000000001",
        project_id="6b0000000000000000000001",
        task_id="6d0000000000000000000001",
        date="2026-09-30",
        total=12.5,
        quantity=5.0,
        billable=True,
        locked=False,
        notes="taxi",
        file_id="9f0000000000000000000001",
    )


def test_expense_details_parses_the_nested_objects() -> None:
    # Arrange
    # Act
    details = ExpenseDetails.model_validate(DETAILS_PAYLOAD)
    # Assert
    assert details == DETAILS


def test_expense_list_parses_the_wrapper_and_totals() -> None:
    # Arrange
    payload = {
        "expenses": {"count": 1, "expenses": [DETAILS_PAYLOAD]},
        "dailyTotals": [{"date": "2026-09-30", "dateAsInstant": "2026-09-30T00:00:00Z", "total": 12.5}],
        "weeklyTotals": [{"date": "2026-09-28", "total": 12.5}],
    }
    # Act
    expense_list = ExpenseList.model_validate(payload)
    # Assert
    assert expense_list == ExpenseList(
        expenses=ExpensesWithCount(count=1, expenses=[DETAILS]),
        daily_totals=[
            ExpenseDailyTotal(
                date="2026-09-30", date_as_instant=datetime.datetime(2026, 9, 30, tzinfo=datetime.UTC), total=12.5
            )
        ],
        weekly_totals=[ExpenseWeeklyTotal(date="2026-09-28", total=12.5)],
    )


def test_category_list_parses_the_wrapper() -> None:
    # Arrange
    # Act
    category_list = ExpenseCategoryList.model_validate({"categories": [CATEGORY_PAYLOAD], "count": 1})
    # Assert
    assert category_list == ExpenseCategoryList(categories=[CATEGORY], count=1)


def test_category_create_dumps_only_the_set_fields_in_camel_case() -> None:
    # Arrange
    payload = ExpenseCategoryCreate(name="Travel", has_unit_price=True, price_in_cents=250)
    # Act
    body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
    # Assert
    assert body == {"name": "Travel", "hasUnitPrice": True, "priceInCents": 250}


def test_status_update_dumps_archived() -> None:
    # Arrange
    # Act
    body = ExpenseCategoryStatusUpdate(archived=True).model_dump(mode="json", by_alias=True, exclude_unset=True)
    # Assert
    assert body == {"archived": True}


def test_expense_create_dumps_the_form_fields_without_the_file() -> None:
    # Arrange
    payload = ExpenseCreate(
        user_id="u1",
        category_id="c1",
        project_id="p1",
        date=datetime.datetime(2026, 9, 30, tzinfo=datetime.UTC),
        amount=12.5,
        file=ExpenseFile("receipt.pdf", b"%PDF", "application/pdf"),
    )
    # Act
    body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True, exclude={"file"})
    # Assert
    assert body == {
        "userId": "u1",
        "categoryId": "c1",
        "projectId": "p1",
        "date": "2026-09-30T00:00:00Z",
        "amount": 12.5,
    }


def test_expense_update_dumps_the_change_fields() -> None:
    # Arrange
    payload = ExpenseUpdate(
        user_id="u1",
        category_id="c1",
        date=datetime.datetime(2026, 9, 30, tzinfo=datetime.UTC),
        amount=1.0,
        change_fields=[ExpenseChangeField.AMOUNT, ExpenseChangeField.NOTES],
    )
    # Act
    body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
    # Assert
    assert body == {
        "userId": "u1",
        "categoryId": "c1",
        "date": "2026-09-30T00:00:00Z",
        "amount": 1.0,
        "changeFields": ["AMOUNT", "NOTES"],
    }


@pytest.mark.parametrize(
    ("category_filter", "expected"),
    [
        (ExpenseCategoryFilter(), {}),
        (
            ExpenseCategoryFilter(
                archived=True,
                name="travel",
                sort_column=ExpenseCategorySortColumn.NAME,
                sort_order=ApprovalSortOrder.DESCENDING,
            ),
            {"archived": True, "name": "travel", "sort-column": "NAME", "sort-order": "DESCENDING"},
        ),
    ],
)
def test_category_filter_maps_to_the_wire_names(category_filter: ExpenseCategoryFilter, expected: dict) -> None:
    # Arrange
    # Act
    params = category_filter.as_params()
    # Assert
    assert params == expected
