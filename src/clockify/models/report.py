from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING
from typing import Any

from pydantic import ConfigDict
from pydantic import Field

from clockify._time import ClockifyInstant
from clockify._time import format_instant
from clockify.models.base import ClockifyModel

if TYPE_CHECKING:
    import datetime


class ReportSortOrder(StrEnum):
    ASCENDING = "ASCENDING"
    DESCENDING = "DESCENDING"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> ReportSortOrder:
        del value
        return cls.UNKNOWN


class ReportGroup(StrEnum):
    USER = "USER"
    PROJECT = "PROJECT"
    TIMEENTRY = "TIMEENTRY"
    TAG = "TAG"
    CLIENT = "CLIENT"
    TASK = "TASK"
    USER_GROUP = "USER_GROUP"
    DATE = "DATE"
    MONTH = "MONTH"
    WEEK = "WEEK"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> ReportGroup:
        del value
        return cls.UNKNOWN


class ReportFilterContains(StrEnum):
    CONTAINS = "CONTAINS"
    DOES_NOT_CONTAIN = "DOES_NOT_CONTAIN"
    CONTAINS_ONLY = "CONTAINS_ONLY"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> ReportFilterContains:
        del value
        return cls.UNKNOWN


class ReportFilterStatus(StrEnum):
    ALL = "ALL"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> ReportFilterStatus:
        del value
        return cls.UNKNOWN


class ReportEntityFilter(ClockifyModel):
    ids: list[str] | None = None
    contains: ReportFilterContains | None = None
    status: ReportFilterStatus | None = None


class SummaryFilter(ClockifyModel):
    groups: list[ReportGroup]
    sort_column: str | None = None


class DetailedFilter(ClockifyModel):
    page: int = 1
    page_size: int = 50
    sort_column: str | None = None


class WeeklySubgroup(StrEnum):
    TIME = "TIME"
    EARNINGS = "EARNINGS"


class WeeklyFilter(ClockifyModel):
    group: ReportGroup
    # Unlike group, the API only accepts TIME or EARNINGS here and rejects every
    # ReportGroup value with "Invalid sub group name".
    subgroup: WeeklySubgroup | None = None


class _ReportRequest(ClockifyModel):
    date_range_start: ClockifyInstant
    date_range_end: ClockifyInstant
    sort_order: ReportSortOrder | None = None
    users: ReportEntityFilter | None = None
    clients: ReportEntityFilter | None = None
    projects: ReportEntityFilter | None = None
    tasks: ReportEntityFilter | None = None
    tags: ReportEntityFilter | None = None
    billable: bool | None = None
    description: str | None = None
    time_zone: str | None = None
    amount_shown: str | None = None


class SummaryReportRequest(_ReportRequest):
    summary_filter: SummaryFilter


class DetailedReportRequest(_ReportRequest):
    detailed_filter: DetailedFilter = Field(default_factory=DetailedFilter)


class WeeklyReportRequest(_ReportRequest):
    weekly_filter: WeeklyFilter


class ReportTotals(ClockifyModel):
    total_time: int | None = None
    total_billable_time: int | None = None
    entries_count: int | None = None


class ReportGroupRow(ClockifyModel):
    id: str | None = Field(default=None, alias="_id")
    name: str | None = None
    duration: int | None = None
    children: list[ReportGroupRow] | None = None


class SummaryReport(ClockifyModel):
    totals: list[ReportTotals] | None = None
    group_one: list[ReportGroupRow] | None = None


class WeeklyReport(ClockifyModel):
    totals: list[ReportTotals] | None = None
    group_one: list[ReportGroupRow] | None = None


class DetailedReport(ClockifyModel):
    # The wire key is all-lowercase, which to_camel does not produce from time_entries.
    model_config = ConfigDict(populate_by_name=True)

    totals: list[ReportTotals] | None = None
    time_entries: list[dict[str, Any]] = Field(default_factory=list, alias="timeentries")


class SharedReport(ClockifyModel):
    # The shape depends on the kind of report that was shared, so only extras are exposed.
    pass


@dataclass(frozen=True, slots=True)
class SharedReportQuery:
    # Parameter Object grouping the optional GET /shared-reports/{id} query parameters.
    date_range_start: datetime.datetime | None = None
    date_range_end: datetime.datetime | None = None
    sort_order: ReportSortOrder | None = None
    sort_column: str | None = None
    page: int | None = None
    page_size: int | None = None

    def as_params(self) -> dict[str, str | int]:
        params: dict[str, str | int] = {}
        if self.date_range_start is not None:
            params["dateRangeStart"] = format_instant(self.date_range_start)
        if self.date_range_end is not None:
            params["dateRangeEnd"] = format_instant(self.date_range_end)
        if self.sort_order is not None:
            params["sortOrder"] = str(self.sort_order)
        if self.sort_column is not None:
            params["sortColumn"] = self.sort_column
        if self.page is not None:
            params["page"] = self.page
        if self.page_size is not None:
            params["pageSize"] = self.page_size
        return params
