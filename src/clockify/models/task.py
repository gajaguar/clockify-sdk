from __future__ import annotations

from enum import StrEnum

from clockify.ids import ProjectId
from clockify.ids import TaskId
from clockify.ids import UserId
from clockify.models.base import ClockifyModel
from clockify.models.workspace import Rate


class TaskStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DONE = "DONE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> TaskStatus:
        del value
        return cls.UNKNOWN


class Task(ClockifyModel):
    id: TaskId
    name: str
    project_id: ProjectId
    assignee_ids: list[UserId] | None = None
    estimate: str | None = None
    status: TaskStatus
    duration: str | None = None
    hourly_rate: Rate | None = None
    cost_rate: Rate | None = None


class TaskCreate(ClockifyModel):
    name: str
    assignee_ids: list[UserId] | None = None
    estimate: str | None = None
    status: TaskStatus | None = None


class TaskUpdate(ClockifyModel):
    name: str | None = None
    assignee_ids: list[UserId] | None = None
    estimate: str | None = None
    status: TaskStatus | None = None
