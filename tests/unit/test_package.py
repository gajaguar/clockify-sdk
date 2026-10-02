from __future__ import annotations

from typing import Final

import clockify

# Kept as one string rather than a list literal so it does not duplicate the __all__
# block in clockify/__init__.py (pylint duplicate-code).
EXPECTED_EXPORTS: Final = (  # ruff: ignore[split-static-string]
    "ADDON_TOKEN_ENV_VAR API_KEY_ENV_VAR EVENT_TYPE_HEADER NO_RETRY SIGNATURE_HEADER AddonId "
    "AddonTokenProvider ApiKeyProvider ApprovalDateRange ApprovalDetails ApprovalExpense ApprovalPeriod "
    "ApprovalProjectInfo ApprovalRequest ApprovalRequestCreate ApprovalRequestCreator ApprovalRequestFilter "
    "ApprovalRequestId ApprovalRequestOwner ApprovalRequestResubmit ApprovalRequestStatus "
    "ApprovalRequestType ApprovalRequestUpdate ApprovalSortColumn ApprovalSortOrder ApprovalState "
    "ApprovalTaskInfo ApprovalTimeEntry AsyncClockifyClient AsyncWorkspaceClient AuthenticationError Client "
    "ClientCreate ClientId ClientOptions ClientUpdate ClockifyAPIError ClockifyClient ClockifyError "
    "ConfigurationError ConflictError CqsKind CreatedInvoice Currency CustomField CustomFieldCreate "
    "CustomFieldEntityType CustomFieldId CustomFieldStatus CustomFieldType CustomFieldUpdate "
    "CustomFieldValue DetailedFilter DetailedReport DetailedReportRequest EstimateType Expense "
    "ExpenseCategory ExpenseCategoryCreate ExpenseCategoryFilter ExpenseCategoryId ExpenseCategoryList "
    "ExpenseCategorySortColumn ExpenseCategoryStatusUpdate ExpenseCategoryUpdate ExpenseChangeField "
    "ExpenseCreate ExpenseDailyTotal ExpenseDetails ExpenseFile ExpenseFileId ExpenseId ExpenseList "
    "ExpenseUpdate ExpenseWeeklyTotal ExpensesWithCount ForbiddenError Invoice InvoiceApplyTaxes "
    "InvoiceCalculationType InvoiceCreate InvoiceDefaults InvoiceDefaultsUpdate InvoiceDetails "
    "InvoiceExportFields InvoiceExportFieldsUpdate InvoiceFilter InvoiceFilterContains InvoiceFilterStatus "
    "InvoiceId InvoiceIdFilter InvoiceImportExpenseField InvoiceImportExpenseGroupBy InvoiceImportGroupType "
    "InvoiceImportPrimaryGroupBy InvoiceImportSecondaryGroupBy InvoiceImportTimeField "
    "InvoiceImportTimeGroupType InvoiceImportType InvoiceInfo InvoiceInfoList InvoiceIssueDateRange "
    "InvoiceItem InvoiceItemCreate InvoiceItemsImport InvoiceLabels InvoiceLabelsUpdate InvoiceList "
    "InvoicePayment InvoicePaymentCreate InvoicePaymentId InvoiceSearch InvoiceSettings "
    "InvoiceSettingsUpdate InvoiceSortColumn InvoiceStatus InvoiceStatusUpdate InvoiceTaxType InvoiceUpdate "
    "InvoiceVisibleZeroField Membership MembershipStatus MembershipType MissingCredentialsError "
    "NotFoundError Project ProjectCreate ProjectId ProjectUpdate Rate RateLimitError Region "
    "ReportEntityFilter ReportFilterContains ReportFilterStatus ReportGroup ReportGroupRow ReportSortOrder "
    "ReportTotals RetryPolicy ServerError SharedReport SharedReportQuery SummaryFilter SummaryReport "
    "SummaryReportRequest Tag TagCreate TagId TagUpdate Task TaskCreate TaskId TaskStatus TaskUpdate "
    "TimeEntry TimeEntryCreate TimeEntryFilter TimeEntryId TimeEntryType TimeEntryUpdate TimeInterval "
    "TimeOffAccrualPeriod TimeOffAutomaticAccrual TimeOffAutomaticAccrualRequest "
    "TimeOffAutomaticTimeEntryCreation TimeOffAutomaticTimeEntryCreationRequest TimeOffBalance "
    "TimeOffBalanceAssignment TimeOffBalanceAssignmentCreate TimeOffBalanceAssignmentDelete "
    "TimeOffBalanceAssignmentId TimeOffBalanceAssignmentUpdate TimeOffBalanceDateRange TimeOffBalanceFilter "
    "TimeOffBalanceId TimeOffBalanceList TimeOffBalanceSortColumn TimeOffBalanceUpdate "
    "TimeOffDefaultEntities TimeOffDefaultEntitiesRequest TimeOffHalfDayPeriod TimeOffMemberFilterContains "
    "TimeOffMemberFilterStatus TimeOffNegativeBalance TimeOffNegativeBalanceRequest TimeOffPeriod "
    "TimeOffPeriodRequest TimeOffPolicy TimeOffPolicyApproval TimeOffPolicyCreate TimeOffPolicyFilter "
    "TimeOffPolicyIcon TimeOffPolicyId TimeOffPolicyMemberFilter TimeOffPolicyStatus "
    "TimeOffPolicyStatusUpdate TimeOffPolicyUpdate TimeOffRequest TimeOffRequestCreate "
    "TimeOffRequestDecision TimeOffRequestDetails TimeOffRequestFilter TimeOffRequestId TimeOffRequestList "
    "TimeOffRequestPeriod TimeOffRequestPeriodRequest TimeOffRequestStatus TimeOffRequestStatusType "
    "TimeOffRequestStatusUpdate TimeOffUnit TransportError User UserGroup UserGroupCreate UserGroupId "
    "UserGroupUpdate UserId UserRedacted ValidationError Webhook WebhookCreate WebhookDeliveryStatus "
    "WebhookEvent WebhookEventStatus WebhookId WebhookList WebhookLog WebhookLogSearch WebhookLogStatus "
    "WebhookTriggerSourceType WebhookType WebhookUpdate WeeklyFilter WeeklyReport WeeklyReportRequest "
    "WeeklySubgroup Workspace WorkspaceClient WorkspaceId WorkspaceSettings WorkspaceSubdomain __version__ "
    "verify_signature"
).split()


def test_version_is_exported() -> None:
    # Arrange
    # Act
    version = clockify.__version__
    # Assert
    assert version == "1.10.0"


def test_public_import_surface() -> None:
    # Arrange
    # Act
    exported = clockify.__all__
    # Assert
    assert exported == EXPECTED_EXPORTS
    assert all(hasattr(clockify, name) for name in exported)
