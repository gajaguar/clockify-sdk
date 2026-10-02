from __future__ import annotations

import datetime
from dataclasses import dataclass
from enum import StrEnum

from pydantic import Field

from clockify._time import ClockifyInstant
from clockify.ids import ClientId
from clockify.ids import InvoiceId
from clockify.ids import InvoicePaymentId
from clockify.ids import UserId
from clockify.models.approval import ApprovalSortOrder
from clockify.models.base import ClockifyModel

# None of these models has been checked against a real Clockify response: Invoices is a
# Standard-plan feature and the account used to build the SDK is on the Free plan. They
# follow the OpenAPI spec, with every doubtful field optional. Two shapes are doubtful:
# the spec renders `taxType`, `applyTaxes` and `calculationType` as objects but every
# request and the settings use a plain string, so they are typed as string enums; and
# `visibleZeroFields` is left as an extra field because the spec disagrees with itself
# about whether it is one value or a list.

# Money is an integer count of the currency's minor unit (cents), as the spec's int64.


class InvoiceStatus(StrEnum):
    UNSENT = "UNSENT"
    SENT = "SENT"
    PAID = "PAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    VOID = "VOID"
    OVERDUE = "OVERDUE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> InvoiceStatus:
        del value
        return cls.UNKNOWN


class InvoiceTaxType(StrEnum):
    COMPOUND = "COMPOUND"
    SIMPLE = "SIMPLE"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> InvoiceTaxType:
        del value
        return cls.UNKNOWN


class InvoiceApplyTaxes(StrEnum):
    TAX1 = "TAX1"
    TAX2 = "TAX2"
    TAX1TAX2 = "TAX1TAX2"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> InvoiceApplyTaxes:
        del value
        return cls.UNKNOWN


class InvoiceCalculationType(StrEnum):
    INVOICE_BASED = "INVOICE_BASED"
    ITEM_BASED = "ITEM_BASED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> InvoiceCalculationType:
        del value
        return cls.UNKNOWN


class InvoiceImportType(StrEnum):
    NOT_IMPORTED = "NOT_IMPORTED"
    TIME_ENTRY_IMPORT = "TIME_ENTRY_IMPORT"
    EXPENSE_IMPORT = "EXPENSE_IMPORT"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> InvoiceImportType:
        del value
        return cls.UNKNOWN


class InvoiceSortColumn(StrEnum):
    ID = "ID"
    CLIENT = "CLIENT"
    DUE_ON = "DUE_ON"
    ISSUE_DATE = "ISSUE_DATE"
    AMOUNT = "AMOUNT"
    BALANCE = "BALANCE"


class InvoiceVisibleZeroField(StrEnum):
    TAX = "TAX"
    TAX_2 = "TAX_2"
    DISCOUNT = "DISCOUNT"


class InvoiceFilterContains(StrEnum):
    CONTAINS = "CONTAINS"
    DOES_NOT_CONTAIN = "DOES_NOT_CONTAIN"
    CONTAINS_ONLY = "CONTAINS_ONLY"


class InvoiceFilterStatus(StrEnum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    ALL = "ALL"


class InvoiceImportGroupType(StrEnum):
    GROUPED = "GROUPED"
    DETAILED = "DETAILED"


class InvoiceImportExpenseGroupBy(StrEnum):
    CATEGORY = "CATEGORY"
    PROJECT = "PROJECT"
    USER = "USER"


class InvoiceImportExpenseField(StrEnum):
    PROJECT = "PROJECT"
    TASK = "TASK"
    CATEGORY = "CATEGORY"
    NOTE = "NOTE"
    DATE = "DATE"
    USER = "USER"


class InvoiceImportTimeGroupType(StrEnum):
    SINGLE_ITEM = "SINGLE_ITEM"
    GROUPED = "GROUPED"
    DETAILED = "DETAILED"


class InvoiceImportTimeField(StrEnum):
    PROJECT = "PROJECT"
    TASK = "TASK"
    TAGS = "TAGS"
    DESCRIPTION = "DESCRIPTION"
    DATE = "DATE"
    USER = "USER"


class InvoiceImportPrimaryGroupBy(StrEnum):
    USER = "USER"
    PROJECT = "PROJECT"
    DATE = "DATE"


class InvoiceImportSecondaryGroupBy(StrEnum):
    PROJECT = "PROJECT"
    USER = "USER"
    TASK = "TASK"
    DATE = "DATE"
    DESCRIPTION = "DESCRIPTION"
    NONE = "NONE"


class Invoice(ClockifyModel):
    id: InvoiceId
    number: str | None = None
    status: InvoiceStatus | None = None
    client_id: ClientId | None = None
    client_name: str | None = None
    currency: str | None = None
    amount: int | None = None
    balance: int | None = None
    paid: int | None = None
    issued_date: ClockifyInstant | None = None
    due_date: ClockifyInstant | None = None


class InvoiceList(ClockifyModel):
    invoices: list[Invoice] | None = None
    total: int | None = None


class InvoiceInfo(ClockifyModel):
    id: InvoiceId
    number: str | None = None
    status: InvoiceStatus | None = None
    client_id: ClientId | None = None
    client_name: str | None = None
    bill_from: str | None = None
    currency: str | None = None
    amount: int | None = None
    balance: int | None = None
    paid: int | None = None
    days_overdue: int | None = None
    issued_date: ClockifyInstant | None = None
    due_date: ClockifyInstant | None = None


class InvoiceInfoList(ClockifyModel):
    invoices: list[InvoiceInfo] | None = None
    total: int | None = None


class InvoiceItem(ClockifyModel):
    order: int | None = None
    description: str | None = None
    item_type: str | None = None
    quantity: int | None = None
    unit_price: int | None = None
    amount: int | None = None
    apply_taxes: InvoiceApplyTaxes | None = None
    import_type: InvoiceImportType | None = None
    time_entry_ids: list[str] | None = None
    expense_ids: list[str] | None = None


class InvoiceDetails(ClockifyModel):
    id: InvoiceId
    number: str | None = None
    status: InvoiceStatus | None = None
    subject: str | None = None
    note: str | None = None
    user_id: UserId | None = None
    company_id: str | None = None
    client_id: ClientId | None = None
    client_name: str | None = None
    client_address: str | None = None
    bill_from: str | None = None
    currency: str | None = None
    issued_date: ClockifyInstant | None = None
    due_date: ClockifyInstant | None = None
    items: list[InvoiceItem] | None = None
    subtotal: int | None = None
    amount: int | None = None
    balance: int | None = None
    paid: int | None = None
    discount: float | None = None
    discount_amount: int | None = None
    tax: float | None = None
    tax_amount: int | None = None
    tax2: float | None = None
    tax2_amount: int | None = None
    tax_type: InvoiceTaxType | None = None
    calculation_type: InvoiceCalculationType | None = None
    contains_imported_expenses: bool | None = None
    contains_imported_times: bool | None = None


class CreatedInvoice(ClockifyModel):
    id: InvoiceId
    number: str | None = None
    client_id: ClientId | None = None
    bill_from: str | None = None
    currency: str | None = None
    issued_date: ClockifyInstant | None = None
    due_date: ClockifyInstant | None = None


class InvoicePayment(ClockifyModel):
    id: InvoicePaymentId
    amount: int | None = None
    author: str | None = None
    date: ClockifyInstant | None = None
    note: str | None = None


class InvoiceDefaults(ClockifyModel):
    company_id: str | None = None
    due_days: int | None = None
    item_type: str | None = None
    item_type_id: str | None = None
    default_import_time_item_type_id: str | None = None
    default_import_expense_item_type_id: str | None = None
    notes: str | None = None
    subject: str | None = None
    tax: int | None = None
    tax2: int | None = None
    tax_percent: float | None = None
    tax2_percent: float | None = None
    tax_type: InvoiceTaxType | None = None


class InvoiceExportFields(ClockifyModel):
    item_type: bool | None = None
    quantity: bool | None = None
    unit_price: bool | None = None
    tax: bool | None = None
    tax2: bool | None = None
    rtl: bool | None = None


class InvoiceLabels(ClockifyModel):
    amount: str | None = None
    bill_from: str | None = None
    bill_to: str | None = None
    description: str | None = None
    discount: str | None = None
    due_date: str | None = None
    issue_date: str | None = None
    item_type: str | None = None
    notes: str | None = None
    paid: str | None = None
    quantity: str | None = None
    subtotal: str | None = None
    tax: str | None = None
    tax2: str | None = None
    total: str | None = None
    total_amount: str | None = None
    unit_price: str | None = None


class InvoiceSettings(ClockifyModel):
    defaults: InvoiceDefaults | None = None
    export_fields: InvoiceExportFields | None = None
    labels: InvoiceLabels | None = None


class InvoiceCreate(ClockifyModel):
    client_id: ClientId
    currency: str
    number: str
    issued_date: ClockifyInstant
    due_date: ClockifyInstant
    time_view_mode: str | None = None


# A PUT replaces the invoice, so the spec requires the percentages along with the dates.
class InvoiceUpdate(ClockifyModel):
    currency: str
    number: str
    issued_date: ClockifyInstant
    due_date: ClockifyInstant
    discount_percent: float
    tax_percent: float
    tax2_percent: float
    client_id: ClientId | None = None
    company_id: str | None = None
    note: str | None = None
    subject: str | None = None
    tax_type: InvoiceTaxType | None = None
    visible_zero_fields: InvoiceVisibleZeroField | None = None


class InvoiceStatusUpdate(ClockifyModel):
    invoice_status: InvoiceStatus | None = None


class InvoiceItemCreate(ClockifyModel):
    description: str
    item_type: str
    quantity: int
    unit_price: int
    apply_taxes: InvoiceApplyTaxes


class InvoiceIdFilter(ClockifyModel):
    contains: InvoiceFilterContains | None = None
    ids: list[str] | None = None
    status: InvoiceFilterStatus | None = None


class InvoiceItemsImport(ClockifyModel):
    # `from` and `to` are keywords or too vague on their own, so only the wire names differ.
    start: ClockifyInstant = Field(alias="from")
    end: ClockifyInstant = Field(alias="to")
    import_expenses: bool
    project_filter: InvoiceIdFilter
    time_entry_group_type: InvoiceImportTimeGroupType
    expenses_group_by: InvoiceImportExpenseGroupBy | None = None
    expenses_group_type: InvoiceImportGroupType | None = None
    expense_fields_for_detailed_group: list[InvoiceImportExpenseField] | None = None
    round_time_entry_duration: bool | None = None
    time_entry_fields_for_detailed_group: list[InvoiceImportTimeField] | None = None
    time_entry_primary_group_by: InvoiceImportPrimaryGroupBy | None = None
    time_entry_secondary_group_by: InvoiceImportSecondaryGroupBy | None = None


class InvoicePaymentCreate(ClockifyModel):
    amount: int | None = None
    note: str | None = None
    payment_date: ClockifyInstant | None = None


class InvoiceIssueDateRange(ClockifyModel):
    start: datetime.date | None = Field(default=None, alias="issue-date-start")
    end: datetime.date | None = Field(default=None, alias="issue-date-end")


# `page` and `pageSize` are not fields: list_page/search_page add them to the body.
class InvoiceSearch(ClockifyModel):
    clients: InvoiceIdFilter | None = None
    companies: InvoiceIdFilter | None = None
    invoice_number: str | None = None
    issue_date: InvoiceIssueDateRange | None = None
    exact_amount: int | None = None
    exact_balance: int | None = None
    greater_than_amount: int | None = None
    greater_than_balance: int | None = None
    less_than_amount: int | None = None
    less_than_balance: int | None = None
    statuses: list[InvoiceStatus] | None = None
    sort_column: InvoiceSortColumn | None = None
    sort_order: ApprovalSortOrder | None = None
    strict_search: bool | None = None


class InvoiceDefaultsUpdate(ClockifyModel):
    notes: str
    subject: str
    company_id: str | None = None
    due_days: int | None = None
    item_type_id: str | None = None
    tax_percent: float | None = None
    tax2_percent: float | None = None
    tax_type: InvoiceTaxType | None = None


class InvoiceExportFieldsUpdate(ClockifyModel):
    item_type: bool | None = None
    quantity: bool | None = None
    unit_price: bool | None = None
    tax: bool | None = None
    tax2: bool | None = None
    rtl: bool | None = None


class InvoiceLabelsUpdate(ClockifyModel):
    amount: str
    bill_from: str
    bill_to: str
    description: str
    discount: str
    due_date: str
    issue_date: str
    item_type: str
    notes: str
    paid: str
    quantity: str
    subtotal: str
    tax: str
    tax2: str
    total: str
    total_amount_due: str
    unit_price: str


class InvoiceSettingsUpdate(ClockifyModel):
    labels: InvoiceLabelsUpdate
    defaults: InvoiceDefaultsUpdate | None = None
    export_fields: InvoiceExportFieldsUpdate | None = None


@dataclass(frozen=True, slots=True)
class InvoiceFilter:
    # Parameter Object for the .../invoices query filters; a dataclass for the same
    # reason as ApprovalRequestFilter (kebab-case wire names).
    statuses: list[InvoiceStatus] | None = None
    sort_column: InvoiceSortColumn | None = None
    sort_order: ApprovalSortOrder | None = None

    def as_params(self) -> dict[str, str | list[str]]:
        params: dict[str, str | list[str]] = {}
        if self.statuses is not None:
            params["statuses"] = [str(status) for status in self.statuses]
        if self.sort_column is not None:
            params["sort-column"] = str(self.sort_column)
        if self.sort_order is not None:
            params["sort-order"] = str(self.sort_order)
        return params
