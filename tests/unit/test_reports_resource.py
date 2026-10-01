from __future__ import annotations

import datetime
import json
from typing import Final

import pytest
import respx
from httpx import Response
from pydantic import ValidationError

from clockify import NO_RETRY
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import CqsKind
from clockify import DetailedReportRequest
from clockify import ReportGroup
from clockify import ReportSortOrder
from clockify import SharedReportQuery
from clockify import SummaryFilter
from clockify import SummaryReportRequest
from clockify import WeeklyFilter
from clockify import WeeklyReportRequest
from clockify import WeeklySubgroup
from clockify.ids import WorkspaceId

BASE_URL: Final = "https://fake.clockify.test/api/v1"
REPORTS_URL: Final = "https://fake.clockify.test/report/v1"
WORKSPACE_ID: Final = WorkspaceId("64a1f0000000000000000001")
START: Final = datetime.datetime(2026, 8, 1, tzinfo=datetime.UTC)
END: Final = datetime.datetime(2026, 8, 31, 23, 59, 59, tzinfo=datetime.UTC)
RANGE_BODY: Final = {"dateRangeStart": "2026-08-01T00:00:00Z", "dateRangeEnd": "2026-08-31T23:59:59Z"}
SHARED_ID: Final = "5d0f5b1f1f1f1f1f1f1f1f1f"

SUMMARY_PAYLOAD: Final = {
    "totals": [{"totalTime": 5400, "entriesCount": 2}],
    "groupOne": [{"_id": "p1", "name": "Project", "duration": 5400, "children": [{"name": "Nested", "duration": 60}]}],
}
DETAILED_PAYLOAD: Final = {
    "totals": [{"totalTime": 5400, "entriesCount": 1}],
    "timeentries": [{"_id": "e1", "description": "Build API"}],
}


def _client() -> ClockifyClient:
    options = ClientOptions(base_url=BASE_URL, reports_base_url=REPORTS_URL, retry=NO_RETRY)
    return ClockifyClient(api_key="dummy", options=options)


@respx.mock
def test_summary_posts_to_the_reports_host_as_a_json_query() -> None:
    # Arrange
    route = respx.post(f"{REPORTS_URL}/workspaces/{WORKSPACE_ID}/reports/summary").mock(
        return_value=Response(200, json=SUMMARY_PAYLOAD)
    )
    client = _client()
    request = SummaryReportRequest(
        date_range_start=START, date_range_end=END, summary_filter=SummaryFilter(groups=[ReportGroup.PROJECT])
    )
    # Act
    report = client.workspace(WORKSPACE_ID).reports.summary(request)
    # Assert
    assert route.call_count == 1
    assert json.loads(respx.calls[0].request.content) == {
        **RANGE_BODY,
        "summaryFilter": {"groups": ["PROJECT"]},
        "exportType": "JSON",
    }
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    assert report.totals is not None
    assert report.totals[0].total_time == 5400
    assert report.group_one is not None
    assert report.group_one[0].id == "p1"
    assert report.group_one[0].children is not None
    assert report.group_one[0].children[0].name == "Nested"
    client.close()


@respx.mock
def test_detailed_posts_and_parses_the_lowercase_timeentries_key() -> None:
    # Arrange
    route = respx.post(f"{REPORTS_URL}/workspaces/{WORKSPACE_ID}/reports/detailed").mock(
        return_value=Response(200, json=DETAILED_PAYLOAD)
    )
    client = _client()
    request = DetailedReportRequest(date_range_start=START, date_range_end=END, sort_order=ReportSortOrder.DESCENDING)
    # Act
    report = client.workspace(WORKSPACE_ID).reports.detailed(request)
    # Assert
    assert route.call_count == 1
    assert json.loads(respx.calls[0].request.content) == {
        **RANGE_BODY,
        "sortOrder": "DESCENDING",
        "detailedFilter": {"page": 1, "pageSize": 50},
        "exportType": "JSON",
    }
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    assert report.time_entries == [{"_id": "e1", "description": "Build API"}]
    client.close()


@respx.mock
def test_detailed_sends_the_default_filter_when_none_is_given() -> None:
    # Arrange
    respx.post(f"{REPORTS_URL}/workspaces/{WORKSPACE_ID}/reports/detailed").mock(
        return_value=Response(200, json=DETAILED_PAYLOAD)
    )
    client = _client()
    request = DetailedReportRequest(date_range_start=START, date_range_end=END)
    # Act
    client.workspace(WORKSPACE_ID).reports.detailed(request)
    # Assert
    assert json.loads(respx.calls[0].request.content) == {
        **RANGE_BODY,
        "detailedFilter": {"page": 1, "pageSize": 50},
        "exportType": "JSON",
    }
    client.close()


def test_weekly_subgroup_rejects_a_report_group() -> None:
    # Arrange
    # Act
    # Assert
    with pytest.raises(ValidationError):
        WeeklyFilter(group=ReportGroup.USER, subgroup="PROJECT")  # type: ignore[arg-type]


@respx.mock
def test_weekly_posts_group_and_subgroup() -> None:
    # Arrange
    route = respx.post(f"{REPORTS_URL}/workspaces/{WORKSPACE_ID}/reports/weekly").mock(
        return_value=Response(200, json=SUMMARY_PAYLOAD)
    )
    client = _client()
    request = WeeklyReportRequest(
        date_range_start=START,
        date_range_end=END,
        weekly_filter=WeeklyFilter(group=ReportGroup.USER, subgroup=WeeklySubgroup.TIME),
    )
    # Act
    report = client.workspace(WORKSPACE_ID).reports.weekly(request)
    # Assert
    assert route.call_count == 1
    assert json.loads(respx.calls[0].request.content) == {
        **RANGE_BODY,
        "weeklyFilter": {"group": "USER", "subgroup": "TIME"},
        "exportType": "JSON",
    }
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    assert report.totals is not None
    client.close()


@respx.mock
def test_shared_gets_by_id_with_query_params_and_keeps_unknown_fields() -> None:
    # Arrange
    route = respx.get(f"{REPORTS_URL}/shared-reports/{SHARED_ID}").mock(
        return_value=Response(200, json={"name": "Monthly", "totals": []})
    )
    client = _client()
    query = SharedReportQuery(date_range_start=START, sort_order=ReportSortOrder.ASCENDING, page=2, page_size=10)
    # Act
    report = client.workspace(WORKSPACE_ID).reports.shared(SHARED_ID, query=query)
    # Assert
    assert route.call_count == 1
    assert dict(respx.calls[0].request.url.params) == {
        "dateRangeStart": "2026-08-01T00:00:00Z",
        "sortOrder": "ASCENDING",
        "page": "2",
        "pageSize": "10",
    }
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    assert report.model_extra == {"name": "Monthly", "totals": []}
    client.close()


@respx.mock
def test_shared_without_query_sends_no_params() -> None:
    # Arrange
    route = respx.get(f"{REPORTS_URL}/shared-reports/{SHARED_ID}").mock(return_value=Response(200, json={}))
    client = _client()
    # Act
    client.workspace(WORKSPACE_ID).reports.shared(SHARED_ID)
    # Assert
    assert route.call_count == 1
    assert not respx.calls[0].request.url.params
    client.close()


def test_shared_report_query_as_params_covers_the_end_bound_and_sort_column() -> None:
    # Arrange
    query = SharedReportQuery(date_range_end=END, sort_column="DURATION")
    # Act
    params = query.as_params()
    # Assert
    assert params == {"dateRangeEnd": "2026-08-31T23:59:59Z", "sortColumn": "DURATION"}
