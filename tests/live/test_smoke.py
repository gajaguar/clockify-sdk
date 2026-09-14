from __future__ import annotations

from os import environ

import pytest

from clockify import ClockifyClient
from clockify import TimeEntryCreate
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
