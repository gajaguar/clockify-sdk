from __future__ import annotations

from clockify.ids import UserGroupId
from clockify.ids import UserId
from clockify.ids import WorkspaceId
from clockify.models.base import ClockifyModel


class UserRedacted(ClockifyModel):
    id: UserId
    name: str


class UserGroup(ClockifyModel):
    id: UserGroupId
    name: str
    workspace_id: WorkspaceId
    user_ids: list[UserId] | None = None
    team_managers: list[UserRedacted] | None = None


class UserGroupCreate(ClockifyModel):
    name: str


class UserGroupUpdate(ClockifyModel):
    name: str
