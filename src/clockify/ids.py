from __future__ import annotations

from typing import NewType

WorkspaceId = NewType("WorkspaceId", str)  # pylint: disable=app-module-const-naming,app-require-final
ProjectId = NewType("ProjectId", str)  # pylint: disable=app-module-const-naming,app-require-final
TaskId = NewType("TaskId", str)  # pylint: disable=app-module-const-naming,app-require-final
UserId = NewType("UserId", str)  # pylint: disable=app-module-const-naming,app-require-final
ClientId = NewType("ClientId", str)  # pylint: disable=app-module-const-naming,app-require-final
TagId = NewType("TagId", str)  # pylint: disable=app-module-const-naming,app-require-final
TimeEntryId = NewType("TimeEntryId", str)  # pylint: disable=app-module-const-naming,app-require-final
UserGroupId = NewType("UserGroupId", str)  # pylint: disable=app-module-const-naming,app-require-final
CustomFieldId = NewType("CustomFieldId", str)  # pylint: disable=app-module-const-naming,app-require-final
