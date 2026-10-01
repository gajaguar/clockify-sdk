from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clockify.models.report import DetailedReport
from clockify.models.report import SharedReport
from clockify.models.report import SummaryReport
from clockify.models.report import WeeklyReport
from clockify.retry import CqsKind

if TYPE_CHECKING:
    from pydantic import BaseModel

    from clockify._transport import AsyncTransport
    from clockify._transport import JSONValue
    from clockify._transport import Transport
    from clockify.ids import WorkspaceId
    from clockify.models.report import DetailedReportRequest
    from clockify.models.report import SharedReportQuery
    from clockify.models.report import SummaryReportRequest
    from clockify.models.report import WeeklyReportRequest


def _body(request: BaseModel) -> dict[str, JSONValue]:
    # Always JSON: the PDF, CSV and XLSX exports return binary bodies that the
    # transport's JSON response handling cannot parse.
    body = request.model_dump(mode="json", by_alias=True, exclude_unset=True)
    body["exportType"] = "JSON"
    return body


@dataclass(slots=True, kw_only=True)
class _ReportPaths:
    _workspace_id: WorkspaceId

    def _report_path(self, kind: str) -> str:
        return f"/workspaces/{self._workspace_id}/reports/{kind}"

    @staticmethod
    def _shared_path(shared_report_id: str) -> str:
        return f"/shared-reports/{shared_report_id}"


class ReportsResource(_ReportPaths):
    # Hand-written rather than a WorkspaceResource subclass: reports have no CRUD shape.
    # Every method is a query, even the POSTs: they read data and are safe to retry.
    def __init__(self, transport: Transport, workspace_id: WorkspaceId) -> None:
        super().__init__(_workspace_id=workspace_id)
        self._transport = transport

    # POST .../reports/summary
    def summary(self, request: SummaryReportRequest) -> SummaryReport:
        data = self._transport.request("POST", self._report_path("summary"), kind=CqsKind.QUERY, json=_body(request))
        return SummaryReport.model_validate(data)

    # POST .../reports/detailed
    def detailed(self, request: DetailedReportRequest) -> DetailedReport:
        data = self._transport.request("POST", self._report_path("detailed"), kind=CqsKind.QUERY, json=_body(request))
        return DetailedReport.model_validate(data)

    # POST .../reports/weekly
    def weekly(self, request: WeeklyReportRequest) -> WeeklyReport:
        data = self._transport.request("POST", self._report_path("weekly"), kind=CqsKind.QUERY, json=_body(request))
        return WeeklyReport.model_validate(data)

    # GET .../shared-reports/{id}
    def shared(self, shared_report_id: str, *, query: SharedReportQuery | None = None) -> SharedReport:
        params = query.as_params() if query is not None else None
        data = self._transport.request("GET", self._shared_path(shared_report_id), kind=CqsKind.QUERY, params=params)
        return SharedReport.model_validate(data)


class AsyncReportsResource(_ReportPaths):
    def __init__(self, transport: AsyncTransport, workspace_id: WorkspaceId) -> None:
        super().__init__(_workspace_id=workspace_id)
        self._transport = transport

    # POST .../reports/summary
    async def summary(self, request: SummaryReportRequest) -> SummaryReport:
        data = await self._transport.request(
            "POST", self._report_path("summary"), kind=CqsKind.QUERY, json=_body(request)
        )
        return SummaryReport.model_validate(data)

    # POST .../reports/detailed
    async def detailed(self, request: DetailedReportRequest) -> DetailedReport:
        data = await self._transport.request(
            "POST", self._report_path("detailed"), kind=CqsKind.QUERY, json=_body(request)
        )
        return DetailedReport.model_validate(data)

    # POST .../reports/weekly
    async def weekly(self, request: WeeklyReportRequest) -> WeeklyReport:
        data = await self._transport.request(
            "POST", self._report_path("weekly"), kind=CqsKind.QUERY, json=_body(request)
        )
        return WeeklyReport.model_validate(data)

    # GET .../shared-reports/{id}
    async def shared(self, shared_report_id: str, *, query: SharedReportQuery | None = None) -> SharedReport:
        params = query.as_params() if query is not None else None
        data = await self._transport.request(
            "GET", self._shared_path(shared_report_id), kind=CqsKind.QUERY, params=params
        )
        return SharedReport.model_validate(data)
