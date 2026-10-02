from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import PlainSerializer
from pydantic import model_validator

from clockify.ids import ClientId
from clockify.ids import ProjectId
from clockify.ids import WorkspaceId
from clockify.models.base import ClockifyModel
from clockify.models.workspace import Membership
from clockify.models.workspace import Rate


class EstimateType(StrEnum):
    AUTO = "AUTO"
    MANUAL = "MANUAL"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> EstimateType:
        del value
        return cls.UNKNOWN


class Project(ClockifyModel):
    id: ProjectId
    name: str
    workspace_id: WorkspaceId
    client_id: ClientId | None = None
    archived: bool = False
    public: bool = True
    billable: bool = True
    color: str | None = None
    note: str | None = None
    estimate: str | None = None
    estimate_type: EstimateType | None = None
    hourly_rate: Rate | None = None
    cost_rate: Rate | None = None
    memberships: list[Membership] | None = None

    # The API nests the estimate as {"estimate": ..., "type": ...}; the model keeps it flat.
    @model_validator(mode="before")
    @classmethod
    def _flatten_estimate(cls, data: object) -> object:
        if not isinstance(data, dict) or not isinstance(data.get("estimate"), dict):
            return data
        nested = data["estimate"]
        flat = {**data, "estimate": nested.get("estimate") or None}
        if "estimateType" not in data and "estimate_type" not in data:
            flat["estimateType"] = nested.get("type")
        return flat


def _nest_estimate(value: str | None) -> dict[str, str] | None:
    return None if value is None else {"estimate": value, "type": EstimateType.MANUAL.value}


class ProjectCreate(ClockifyModel):
    name: str
    client_id: ClientId | None = None
    is_public: bool | None = None
    billable: bool | None = None
    color: str | None = None
    note: str | None = None
    # The API expects the nested estimate object; a caller-supplied duration is a manual estimate.
    estimate: Annotated[str | None, PlainSerializer(_nest_estimate)] = None
    hourly_rate: Rate | None = None


class ProjectUpdate(ClockifyModel):
    name: str | None = None
    client_id: ClientId | None = None
    is_public: bool | None = None
    archived: bool | None = None
    billable: bool | None = None
    color: str | None = None
    note: str | None = None
    hourly_rate: Rate | None = None
