from __future__ import annotations

from enum import StrEnum

from clockify.ids import UserId
from clockify.ids import WorkspaceId
from clockify.models.base import ClockifyModel


class UserStatus(StrEnum):
    ACTIVE = "ACTIVE"
    PENDING_EMAIL_VERIFICATION = "PENDING_EMAIL_VERIFICATION"
    DELETED = "DELETED"
    INACTIVE = "INACTIVE"
    NOT_REGISTERED = "NOT_REGISTERED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> UserStatus:
        del value
        return cls.UNKNOWN


class User(ClockifyModel):
    id: UserId
    email: str
    name: str
    active_workspace: WorkspaceId | None = None
    default_workspace: WorkspaceId | None = None
    status: UserStatus
