from __future__ import annotations

from typing import NewType

WorkspaceId = NewType("WorkspaceId", str)  # pylint: disable=gajaguar-module-const-naming,gajaguar-require-final
ProjectId = NewType("ProjectId", str)  # pylint: disable=gajaguar-module-const-naming,gajaguar-require-final
TaskId = NewType("TaskId", str)  # pylint: disable=gajaguar-module-const-naming,gajaguar-require-final
UserId = NewType("UserId", str)  # pylint: disable=gajaguar-module-const-naming,gajaguar-require-final
ClientId = NewType("ClientId", str)  # pylint: disable=gajaguar-module-const-naming,gajaguar-require-final
TagId = NewType("TagId", str)  # pylint: disable=gajaguar-module-const-naming,gajaguar-require-final
TimeEntryId = NewType("TimeEntryId", str)  # pylint: disable=gajaguar-module-const-naming,gajaguar-require-final
UserGroupId = NewType("UserGroupId", str)  # pylint: disable=gajaguar-module-const-naming,gajaguar-require-final
CustomFieldId = NewType("CustomFieldId", str)  # pylint: disable=gajaguar-module-const-naming,gajaguar-require-final
WebhookId = NewType("WebhookId", str)  # pylint: disable=gajaguar-module-const-naming,gajaguar-require-final
ApprovalRequestId = NewType("ApprovalRequestId", str)  # pylint: disable=gajaguar-module-const-naming,gajaguar-require-final
