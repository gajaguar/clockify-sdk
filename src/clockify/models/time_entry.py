from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING
from typing import Any

from clockify._time import ClockifyDuration
from clockify._time import ClockifyInstant
from clockify._time import format_instant
from clockify.ids import CustomFieldId
from clockify.ids import ProjectId
from clockify.ids import TagId
from clockify.ids import TaskId
from clockify.ids import TimeEntryId
from clockify.ids import UserId
from clockify.ids import WorkspaceId
from clockify.models.base import ClockifyModel
from clockify.models.custom_field import CustomFieldType

if TYPE_CHECKING:
    import datetime


class TimeEntryType(StrEnum):
    REGULAR = "REGULAR"
    BREAK = "BREAK"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> TimeEntryType:
        del value
        return cls.UNKNOWN


class TimeInterval(ClockifyModel):
    start: ClockifyInstant
    end: ClockifyInstant | None = None
    duration: ClockifyDuration | None = None


class CustomFieldValue(ClockifyModel):
    custom_field_id: CustomFieldId
    value: Any | None = None
    name: str | None = None
    type: CustomFieldType | None = None


class TimeEntry(ClockifyModel):
    id: TimeEntryId
    workspace_id: WorkspaceId
    user_id: UserId
    description: str | None = None
    project_id: ProjectId | None = None
    task_id: TaskId | None = None
    tag_ids: list[TagId] | None = None
    billable: bool = False
    time_interval: TimeInterval
    custom_field_values: list[CustomFieldValue] | None = None
    type: TimeEntryType | None = None
    is_locked: bool = False


class TimeEntryCreate(ClockifyModel):
    start: ClockifyInstant
    end: ClockifyInstant | None = None
    billable: bool | None = None
    description: str | None = None
    project_id: ProjectId | None = None
    task_id: TaskId | None = None
    tag_ids: list[TagId] | None = None
    custom_fields: list[CustomFieldValue] | None = None
    type: TimeEntryType | None = None


class TimeEntryUpdate(ClockifyModel):
    # Clockify's PUT replaces the entry wholesale, so `start` is required here too,
    # unlike every other *Update model in this package.
    start: ClockifyInstant
    end: ClockifyInstant | None = None
    billable: bool | None = None
    description: str | None = None
    project_id: ProjectId | None = None
    task_id: TaskId | None = None
    tag_ids: list[TagId] | None = None
    custom_fields: list[CustomFieldValue] | None = None
    type: TimeEntryType | None = None


@dataclass(frozen=True, slots=True)
class TimeEntryFilter:
    # Parameter Object grouping the .../user/{userId}/time-entries query filters.
    # A dataclass rather than a pydantic model: Clockify's wire names here are
    # kebab-case (project-required, in-progress), not camelCase, so ClockifyModel's
    # to_camel alias generator does not apply.
    description: str | None = None
    start: datetime.datetime | None = None
    end: datetime.datetime | None = None
    project: ProjectId | None = None
    task: TaskId | None = None
    tag_ids: list[TagId] | None = None
    project_required: bool | None = None
    task_required: bool | None = None
    in_progress: bool | None = None

    def as_params(self) -> dict[str, str | int | float | bool | list[str]]:
        params: dict[str, str | int | float | bool | list[str]] = {}
        if self.description is not None:
            params["description"] = self.description
        if self.start is not None:
            params["start"] = format_instant(self.start)
        if self.end is not None:
            params["end"] = format_instant(self.end)
        if self.project is not None:
            params["project"] = str(self.project)
        if self.task is not None:
            params["task"] = str(self.task)
        if self.tag_ids is not None:
            params["tags"] = [str(tag_id) for tag_id in self.tag_ids]
        if self.project_required is not None:
            params["project-required"] = self.project_required
        if self.task_required is not None:
            params["task-required"] = self.task_required
        if self.in_progress is not None:
            params["in-progress"] = self.in_progress
        return params
