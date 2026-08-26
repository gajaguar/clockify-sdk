from __future__ import annotations

from os import environ

import pytest

from clockify import ClockifyClient


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
