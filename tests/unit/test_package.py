from __future__ import annotations

from typing import Final

import clockify

# Kept as one string rather than a list literal so it does not duplicate the __all__
# block in clockify/__init__.py (pylint duplicate-code).
EXPECTED_EXPORTS: Final = (  # ruff: ignore[split-static-string]
    "NO_RETRY AuthenticationError Client ClientCreate ClientId ClientOptions ClientUpdate ClockifyAPIError "
    "ClockifyClient ClockifyError ConfigurationError ConflictError CqsKind Currency CustomField "
    "CustomFieldCreate CustomFieldEntityType CustomFieldId CustomFieldStatus CustomFieldType CustomFieldUpdate "
    "CustomFieldValue EstimateType ForbiddenError Membership MembershipStatus MembershipType "
    "MissingCredentialsError NotFoundError Project ProjectCreate ProjectId ProjectUpdate Rate RateLimitError "
    "Region RetryPolicy ServerError Tag TagCreate TagId TagUpdate Task TaskCreate TaskId TaskStatus TaskUpdate "
    "TimeEntry TimeEntryCreate TimeEntryFilter TimeEntryId TimeEntryType TimeEntryUpdate TimeInterval "
    "TransportError User UserGroup UserGroupCreate UserGroupId UserGroupUpdate UserId UserRedacted "
    "ValidationError Workspace WorkspaceClient WorkspaceId WorkspaceSettings WorkspaceSubdomain __version__"
).split()


def test_version_is_exported() -> None:
    # Arrange
    # Act
    version = clockify.__version__
    # Assert
    assert version == "0.1.0"


def test_public_import_surface() -> None:
    # Arrange
    # Act
    exported = clockify.__all__
    # Assert
    assert exported == EXPECTED_EXPORTS
    assert all(hasattr(clockify, name) for name in exported)
