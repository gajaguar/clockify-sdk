from __future__ import annotations

import pytest

from clockify.config import ClientConfig
from clockify.config import Region
from clockify.config import resolve_api_key
from clockify.config import resolve_urls
from clockify.errors import MissingCredentialsError
from clockify.retry import RetryPolicy


def test_resolve_api_key_prefers_explicit_argument(monkeypatch) -> None:
    # Arrange
    monkeypatch.setenv("CLOCKIFY_API_KEY", "from-env")
    # Act
    resolved = resolve_api_key("explicit")
    # Assert
    assert resolved == "explicit"


def test_resolve_api_key_falls_back_to_environment(monkeypatch) -> None:
    # Arrange
    monkeypatch.setenv("CLOCKIFY_API_KEY", "from-env")
    # Act
    resolved = resolve_api_key(None)
    # Assert
    assert resolved == "from-env"


def test_resolve_api_key_raises_when_missing(monkeypatch) -> None:
    # Arrange
    monkeypatch.delenv("CLOCKIFY_API_KEY", raising=False)
    # Act
    # Assert
    with pytest.raises(MissingCredentialsError, match="CLOCKIFY_API_KEY"):
        resolve_api_key(None)


@pytest.mark.parametrize(
    ("region", "expected"),
    [
        (Region.GLOBAL, ("https://api.clockify.me/api/v1", "https://reports.api.clockify.me/v1")),
        (Region.EU_CENTRAL_1, ("https://euc1.clockify.me/api/v1", "https://euc1.clockify.me/report/v1")),
        (Region.US_EAST_2, ("https://use2.clockify.me/api/v1", "https://use2.clockify.me/report/v1")),
        (Region.EU_WEST_2, ("https://euw2.clockify.me/api/v1", "https://euw2.clockify.me/report/v1")),
        (Region.AP_SOUTHEAST_2, ("https://apse2.clockify.me/api/v1", "https://apse2.clockify.me/report/v1")),
        (Region.DEVELOPER, ("https://developer.clockify.me/api/v1", "https://developer.clockify.me/api/v1")),
    ],
)
def test_resolve_urls_per_region(region, expected) -> None:
    # Arrange
    # Act
    resolved = resolve_urls(region, None, None)
    # Assert
    assert resolved == expected


def test_resolve_urls_explicit_base_url_overrides_region() -> None:
    # Arrange
    override = "https://fake.test/api/v1"
    # Act
    base, reports = resolve_urls(Region.EU_CENTRAL_1, override, None)
    # Assert
    assert base == override
    assert reports == "https://euc1.clockify.me/report/v1"


def test_resolve_urls_explicit_reports_url_overrides_region() -> None:
    # Arrange
    override = "https://fake.test/report/v1"
    # Act
    base, reports = resolve_urls(Region.GLOBAL, None, override)
    # Assert
    assert base == "https://api.clockify.me/api/v1"
    assert reports == override


def test_client_config_defaults() -> None:
    # Arrange
    # Act
    config = ClientConfig(api_key="k", base_url="b", reports_base_url="r")
    # Assert
    assert config.timeout == pytest.approx(30.0)
    assert config.page_size == 200
    assert config.user_agent == "clockify-unofficial-sdk"
    assert config.retry == RetryPolicy()
