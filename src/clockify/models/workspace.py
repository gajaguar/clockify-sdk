from __future__ import annotations

from enum import StrEnum

from clockify.ids import UserId
from clockify.ids import WorkspaceId
from clockify.models.base import ClockifyModel


class MembershipType(StrEnum):
    WORKSPACE = "WORKSPACE"
    PROJECT = "PROJECT"
    USERGROUP = "USERGROUP"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> MembershipType:
        del value
        return cls.UNKNOWN


class MembershipStatus(StrEnum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    DECLINED = "DECLINED"
    INACTIVE = "INACTIVE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> MembershipStatus:
        del value
        return cls.UNKNOWN


class Rate(ClockifyModel):
    amount: int | None = None
    currency: str | None = None


class Currency(ClockifyModel):
    id: str
    code: str
    is_default: bool = False


class WorkspaceSubdomain(ClockifyModel):
    enabled: bool = False
    name: str | None = None


class WorkspaceSettings(ClockifyModel):
    # Clockify's workspace settings payload carries dozens of fields (kiosk, rounding,
    # approvals, ...) that no current SDK surface reads or writes. ClockifyModel's
    # extra="allow" round-trips them without requiring each to be declared here.
    pass


class Membership(ClockifyModel):
    user_id: UserId
    target_id: str
    membership_type: MembershipType
    membership_status: MembershipStatus
    hourly_rate: Rate | None = None
    cost_rate: Rate | None = None


class Workspace(ClockifyModel):
    id: WorkspaceId
    name: str
    image_url: str | None = None
    hourly_rate: Rate | None = None
    cost_rate: Rate | None = None
    currencies: list[Currency] | None = None
    memberships: list[Membership] | None = None
    subdomain: WorkspaceSubdomain | None = None
    workspace_settings: WorkspaceSettings | None = None
