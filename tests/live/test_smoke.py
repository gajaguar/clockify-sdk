from __future__ import annotations

import datetime
from os import environ

import pytest

from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import Region
from clockify import ReportGroup
from clockify import SummaryFilter
from clockify import SummaryReportRequest
from clockify import TimeEntryCreate
from clockify.errors import ForbiddenError
from clockify.ids import WorkspaceId


@pytest.mark.live
@pytest.mark.skipif(not environ.get("CLOCKIFY_TEST_API_KEY"), reason="CLOCKIFY_TEST_API_KEY not set")
def test_me_smoke() -> None:
    # Arrange
    client = ClockifyClient(api_key=environ["CLOCKIFY_TEST_API_KEY"])
    # Act
    user = client.user.me()
    # Assert
    assert user.email
    client.close()


@pytest.mark.live
@pytest.mark.skipif(
    not (environ.get("CLOCKIFY_TEST_API_KEY") and environ.get("CLOCKIFY_TEST_WORKSPACE_ID")),
    reason="CLOCKIFY_TEST_API_KEY / CLOCKIFY_TEST_WORKSPACE_ID not set",
)
def test_time_entry_start_stop_delete_cycle_smoke() -> None:
    # Arrange
    client = ClockifyClient(api_key=environ["CLOCKIFY_TEST_API_KEY"])
    workspace = client.workspace(WorkspaceId(environ["CLOCKIFY_TEST_WORKSPACE_ID"]))
    user = client.user.me()
    started = None
    try:
        # Act
        started = workspace.time_entries.start(user.id, TimeEntryCreate(description="clockify-sdk live smoke test"))
        stopped = workspace.time_entries.stop(user.id)
        # Assert
        assert started.id
        assert stopped.time_interval.end is not None
    finally:
        if started is not None:
            workspace.time_entries.delete(started.id)
        client.close()


@pytest.mark.live
@pytest.mark.skipif(
    not (environ.get("CLOCKIFY_TEST_API_KEY") and environ.get("CLOCKIFY_TEST_WORKSPACE_ID")),
    reason="CLOCKIFY_TEST_API_KEY / CLOCKIFY_TEST_WORKSPACE_ID not set",
)
def test_reports_summary_smoke() -> None:
    # Arrange
    region = Region(environ.get("CLOCKIFY_TEST_REGION", Region.GLOBAL))
    client = ClockifyClient(api_key=environ["CLOCKIFY_TEST_API_KEY"], options=ClientOptions(region=region))
    workspace = client.workspace(WorkspaceId(environ["CLOCKIFY_TEST_WORKSPACE_ID"]))
    end = datetime.datetime.now(datetime.UTC)
    request = SummaryReportRequest(
        date_range_start=end - datetime.timedelta(days=7),
        date_range_end=end,
        summary_filter=SummaryFilter(groups=[ReportGroup.PROJECT]),
    )
    try:
        # Act
        report = workspace.reports.summary(request)
    except ForbiddenError:
        pytest.skip("403 from the Reports API: the key authenticated but the workspace plan (e.g. FREE) lacks it")
    else:
        # Assert
        assert report is not None
    finally:
        client.close()


@pytest.mark.live
@pytest.mark.skipif(
    not (environ.get("CLOCKIFY_TEST_API_KEY") and environ.get("CLOCKIFY_TEST_WORKSPACE_ID")),
    reason="CLOCKIFY_TEST_API_KEY / CLOCKIFY_TEST_WORKSPACE_ID not set",
)
def test_approvals_list_smoke() -> None:
    # Arrange
    client = ClockifyClient(api_key=environ["CLOCKIFY_TEST_API_KEY"])
    workspace = client.workspace(WorkspaceId(environ["CLOCKIFY_TEST_WORKSPACE_ID"]))
    try:
        # Act
        page = workspace.approvals.list_page(page_size=1)
    except ForbiddenError:
        pytest.skip(
            "403 from the Approvals API: the key authenticated but the workspace plan (below Standard) lacks it"
        )
    else:
        # Assert
        assert page.page == 1
    finally:
        client.close()


@pytest.mark.live
@pytest.mark.skipif(
    not (environ.get("CLOCKIFY_TEST_API_KEY") and environ.get("CLOCKIFY_TEST_WORKSPACE_ID")),
    reason="CLOCKIFY_TEST_API_KEY / CLOCKIFY_TEST_WORKSPACE_ID not set",
)
def test_expenses_list_smoke() -> None:
    # Arrange
    client = ClockifyClient(api_key=environ["CLOCKIFY_TEST_API_KEY"])
    workspace = client.workspace(WorkspaceId(environ["CLOCKIFY_TEST_WORKSPACE_ID"]))
    try:
        # Act
        page = workspace.expenses.list_page(page_size=1)
    except ForbiddenError:
        pytest.skip("403 from the Expenses API: the key authenticated but the workspace plan (below Pro) lacks it")
    else:
        # Assert
        assert page.page == 1
    finally:
        client.close()


@pytest.mark.live
@pytest.mark.skipif(
    not (environ.get("CLOCKIFY_TEST_API_KEY") and environ.get("CLOCKIFY_TEST_WORKSPACE_ID")),
    reason="CLOCKIFY_TEST_API_KEY / CLOCKIFY_TEST_WORKSPACE_ID not set",
)
def test_expense_categories_list_smoke() -> None:
    # Arrange
    client = ClockifyClient(api_key=environ["CLOCKIFY_TEST_API_KEY"])
    workspace = client.workspace(WorkspaceId(environ["CLOCKIFY_TEST_WORKSPACE_ID"]))
    try:
        # Act
        page = workspace.expense_categories.list_page(page_size=1)
    except ForbiddenError:
        pytest.skip("403 from the Expenses API: the key authenticated but the workspace plan (below Pro) lacks it")
    else:
        # Assert
        assert page.page == 1
    finally:
        client.close()


@pytest.mark.live
@pytest.mark.skipif(
    not (environ.get("CLOCKIFY_TEST_API_KEY") and environ.get("CLOCKIFY_TEST_WORKSPACE_ID")),
    reason="CLOCKIFY_TEST_API_KEY / CLOCKIFY_TEST_WORKSPACE_ID not set",
)
def test_webhook_statuses_smoke() -> None:
    # Arrange
    client = ClockifyClient(api_key=environ["CLOCKIFY_TEST_API_KEY"])
    workspace = client.workspace(WorkspaceId(environ["CLOCKIFY_TEST_WORKSPACE_ID"]))
    try:
        # Act
        webhooks = list(workspace.webhooks.list())
        if not webhooks:
            pytest.skip("the workspace has no webhook to read the delivery statuses of")
        page = workspace.webhooks.statuses_page(webhooks[0].id, page_size=1)
    except ForbiddenError:
        pytest.skip("403 from the Webhooks API: the key authenticated but the workspace plan lacks it")
    else:
        # Assert
        assert page.page == 1
    finally:
        client.close()


@pytest.mark.live
@pytest.mark.skipif(
    not (environ.get("CLOCKIFY_TEST_API_KEY") and environ.get("CLOCKIFY_TEST_WORKSPACE_ID")),
    reason="CLOCKIFY_TEST_API_KEY / CLOCKIFY_TEST_WORKSPACE_ID not set",
)
def test_time_off_policies_list_smoke() -> None:
    # Arrange
    client = ClockifyClient(api_key=environ["CLOCKIFY_TEST_API_KEY"])
    workspace = client.workspace(WorkspaceId(environ["CLOCKIFY_TEST_WORKSPACE_ID"]))
    try:
        # Act
        page = workspace.time_off_policies.list_page(page_size=1)
    except ForbiddenError:
        pytest.skip(
            "403 from the Time off API: the key authenticated but the workspace plan (below Standard) lacks it"
        )
    else:
        # Assert
        assert page.page == 1
    finally:
        client.close()


@pytest.mark.live
@pytest.mark.skipif(
    not (environ.get("CLOCKIFY_TEST_API_KEY") and environ.get("CLOCKIFY_TEST_WORKSPACE_ID")),
    reason="CLOCKIFY_TEST_API_KEY / CLOCKIFY_TEST_WORKSPACE_ID not set",
)
def test_time_off_requests_list_smoke() -> None:
    # Arrange
    client = ClockifyClient(api_key=environ["CLOCKIFY_TEST_API_KEY"])
    workspace = client.workspace(WorkspaceId(environ["CLOCKIFY_TEST_WORKSPACE_ID"]))
    try:
        # Act
        page = workspace.time_off_requests.list_page(page_size=1)
    except ForbiddenError:
        pytest.skip(
            "403 from the Time off API: the key authenticated but the workspace plan (below Standard) lacks it"
        )
    else:
        # Assert
        assert page.page == 1
    finally:
        client.close()
