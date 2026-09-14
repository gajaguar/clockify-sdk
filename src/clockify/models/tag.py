from __future__ import annotations

from clockify.ids import TagId
from clockify.ids import WorkspaceId
from clockify.models.base import ClockifyModel


class Tag(ClockifyModel):
    id: TagId
    name: str
    workspace_id: WorkspaceId
    archived: bool = False


class TagCreate(ClockifyModel):
    name: str


class TagUpdate(ClockifyModel):
    name: str | None = None
    archived: bool | None = None
