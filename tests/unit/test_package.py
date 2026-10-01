from __future__ import annotations

from typing import Final

import clockify

# Kept as one string rather than a list literal so it does not duplicate the __all__
# block in clockify/__init__.py (pylint duplicate-code).
EXPECTED_EXPORTS: Final = (  # ruff: ignore[split-static-string]
    "ADDON_TOKEN_ENV_VAR API_KEY_ENV_VAR EVENT_TYPE_HEADER NO_RETRY SIGNATURE_HEADER AddonTokenProvider "
    "ApiKeyProvider AsyncClockifyClient "
    "AsyncWorkspaceClient AuthenticationError Client ClientCreate ClientId ClientOptions ClientUpdate "
    "ClockifyAPIError ClockifyClient ClockifyError ConfigurationError ConflictError CqsKind Currency CustomField "
    "CustomFieldCreate CustomFieldEntityType CustomFieldId CustomFieldStatus CustomFieldType CustomFieldUpdate "
    "CustomFieldValue DetailedFilter DetailedReport DetailedReportRequest EstimateType ForbiddenError Membership "
    "MembershipStatus MembershipType MissingCredentialsError NotFoundError Project ProjectCreate ProjectId "
    "ProjectUpdate Rate RateLimitError Region ReportEntityFilter ReportFilterContains ReportFilterStatus "
    "ReportGroup ReportGroupRow ReportSortOrder ReportTotals RetryPolicy ServerError SharedReport "
    "SharedReportQuery SummaryFilter SummaryReport SummaryReportRequest Tag TagCreate TagId TagUpdate Task "
    "TaskCreate TaskId TaskStatus TaskUpdate TimeEntry TimeEntryCreate TimeEntryFilter TimeEntryId TimeEntryType "
    "TimeEntryUpdate TimeInterval TransportError User UserGroup UserGroupCreate UserGroupId UserGroupUpdate "
    "UserId UserRedacted ValidationError Webhook WebhookCreate WebhookEvent WebhookId WebhookList "
    "WebhookTriggerSourceType WebhookType WebhookUpdate WeeklyFilter WeeklyReport WeeklyReportRequest "
    "WeeklySubgroup Workspace WorkspaceClient WorkspaceId WorkspaceSettings WorkspaceSubdomain __version__ "
    "verify_signature"
).split()


def test_version_is_exported() -> None:
    # Arrange
    # Act
    version = clockify.__version__
    # Assert
    assert version == "1.4.0"


def test_public_import_surface() -> None:
    # Arrange
    # Act
    exported = clockify.__all__
    # Assert
    assert exported == EXPECTED_EXPORTS
    assert all(hasattr(clockify, name) for name in exported)
