from __future__ import annotations

from enum import StrEnum
from typing import Any

from clockify.ids import CustomFieldId
from clockify.ids import WorkspaceId
from clockify.models.base import ClockifyModel


class CustomFieldType(StrEnum):
    TXT = "TXT"
    NUMBER = "NUMBER"
    DROPDOWN_SINGLE = "DROPDOWN_SINGLE"
    DROPDOWN_MULTIPLE = "DROPDOWN_MULTIPLE"
    CHECKBOX = "CHECKBOX"
    LINK = "LINK"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> CustomFieldType:
        del value
        return cls.UNKNOWN


class CustomFieldEntityType(StrEnum):
    TIMEENTRY = "TIMEENTRY"
    USER = "USER"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> CustomFieldEntityType:
        del value
        return cls.UNKNOWN


class CustomFieldStatus(StrEnum):
    INACTIVE = "INACTIVE"
    VISIBLE = "VISIBLE"
    INVISIBLE = "INVISIBLE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> CustomFieldStatus:
        del value
        return cls.UNKNOWN


class CustomField(ClockifyModel):
    id: CustomFieldId
    name: str
    type: CustomFieldType
    entity_type: CustomFieldEntityType
    status: CustomFieldStatus
    workspace_id: WorkspaceId
    allowed_values: list[str] | None = None
    workspace_default_value: Any | None = None
    placeholder: str | None = None
    description: str | None = None
    required: bool = False
    only_admin_can_edit: bool = False


class CustomFieldCreate(ClockifyModel):
    name: str
    type: CustomFieldType
    entity_type: CustomFieldEntityType | None = None
    allowed_values: list[str] | None = None
    workspace_default_value: Any | None = None
    placeholder: str | None = None
    description: str | None = None
    status: CustomFieldStatus | None = None
    only_admin_can_edit: bool | None = None


class CustomFieldUpdate(ClockifyModel):
    name: str | None = None
    allowed_values: list[str] | None = None
    workspace_default_value: Any | None = None
    placeholder: str | None = None
    description: str | None = None
    status: CustomFieldStatus | None = None
    required: bool | None = None
    only_admin_can_edit: bool | None = None
