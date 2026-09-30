from __future__ import annotations

import pytest

from clockify.config import ClientConfig
from clockify.config import Region
from clockify.config import resolve_addon_token
from clockify.config import resolve_api_key
from clockify.config import resolve_credentials
from clockify.config import resolve_urls
from clockify.errors import ConfigurationError
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


def test_resolve_api_key_error_says_where_to_create_the_key(monkeypatch) -> None:
    # Arrange
    monkeypatch.delenv("CLOCKIFY_API_KEY", raising=False)
    # Act
    # Assert
    with pytest.raises(MissingCredentialsError, match="Manage API keys"):
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


def test_client_config_repr_never_contains_the_api_key() -> None:
    # Arrange
    config = ClientConfig(api_key="super-secret-key-value", base_url="b", reports_base_url="r")
    # Act
    rendered = repr(config)
    # Assert
    assert "super-secret-key-value" not in rendered


def _provider() -> str:
    return "from-provider"


def test_resolve_api_key_returns_a_provider_callable_unchanged(monkeypatch) -> None:
    # Arrange
    monkeypatch.setenv("CLOCKIFY_API_KEY", "from-env")
    # Act
    resolved = resolve_api_key(_provider)
    # Assert
    assert resolved is _provider


def test_resolve_api_key_prefers_a_provider_over_the_environment(monkeypatch) -> None:
    # Arrange
    monkeypatch.delenv("CLOCKIFY_API_KEY", raising=False)
    # Act
    resolved = resolve_api_key(_provider)
    # Assert
    assert resolved is _provider


def test_resolve_addon_token_prefers_explicit_argument(monkeypatch) -> None:
    # Arrange
    monkeypatch.setenv("CLOCKIFY_ADDON_TOKEN", "from-env")
    # Act
    resolved = resolve_addon_token("explicit")
    # Assert
    assert resolved == "explicit"


def test_resolve_addon_token_falls_back_to_environment(monkeypatch) -> None:
    # Arrange
    monkeypatch.setenv("CLOCKIFY_ADDON_TOKEN", "from-env")
    # Act
    resolved = resolve_addon_token(None)
    # Assert
    assert resolved == "from-env"


def test_resolve_addon_token_raises_when_missing_and_names_the_variable(monkeypatch) -> None:
    # Arrange
    monkeypatch.delenv("CLOCKIFY_ADDON_TOKEN", raising=False)
    # Act
    # Assert
    with pytest.raises(MissingCredentialsError, match="CLOCKIFY_ADDON_TOKEN") as excinfo:
        resolve_addon_token(None)
    assert "add-on" in str(excinfo.value)


def test_resolve_addon_token_returns_a_provider_unchanged_and_ahead_of_the_environment(monkeypatch) -> None:
    # Arrange
    monkeypatch.setenv("CLOCKIFY_ADDON_TOKEN", "from-env")
    # Act
    resolved = resolve_addon_token(_provider)
    # Assert
    assert resolved is _provider


def test_resolve_credentials_rejects_a_provider_with_an_explicit_credential_of_the_other_kind() -> None:
    # Arrange
    # Act
    # Assert
    with pytest.raises(ConfigurationError, match="not both"):
        resolve_credentials(lambda: "key", "token")


def test_resolve_credentials_rejects_both_explicit(monkeypatch) -> None:
    # Arrange
    monkeypatch.delenv("CLOCKIFY_API_KEY", raising=False)
    monkeypatch.delenv("CLOCKIFY_ADDON_TOKEN", raising=False)
    # Act
    # Assert
    with pytest.raises(ConfigurationError, match="not both"):
        resolve_credentials("key", "token")


def test_resolve_credentials_rejects_both_environment_variables(monkeypatch) -> None:
    # Arrange
    monkeypatch.setenv("CLOCKIFY_API_KEY", "key")
    monkeypatch.setenv("CLOCKIFY_ADDON_TOKEN", "token")
    # Act
    # Assert
    with pytest.raises(ConfigurationError, match="CLOCKIFY_ADDON_TOKEN"):
        resolve_credentials(None, None)


def test_resolve_credentials_explicit_addon_token_beats_the_api_key_variable(monkeypatch) -> None:
    # Arrange
    monkeypatch.setenv("CLOCKIFY_API_KEY", "key")
    # Act
    resolved = resolve_credentials(None, "token")
    # Assert
    assert resolved == (None, "token")


def test_resolve_credentials_explicit_api_key_beats_the_addon_token_variable(monkeypatch) -> None:
    # Arrange
    monkeypatch.setenv("CLOCKIFY_ADDON_TOKEN", "token")
    # Act
    resolved = resolve_credentials("key", None)
    # Assert
    assert resolved == ("key", None)


def test_resolve_credentials_addon_token_variable_alone_selects_the_token(monkeypatch) -> None:
    # Arrange
    monkeypatch.delenv("CLOCKIFY_API_KEY", raising=False)
    monkeypatch.setenv("CLOCKIFY_ADDON_TOKEN", "token")
    # Act
    resolved = resolve_credentials(None, None)
    # Assert
    assert resolved == (None, "token")


def test_resolve_credentials_api_key_variable_alone_selects_the_key(monkeypatch) -> None:
    # Arrange
    monkeypatch.setenv("CLOCKIFY_API_KEY", "key")
    monkeypatch.delenv("CLOCKIFY_ADDON_TOKEN", raising=False)
    # Act
    resolved = resolve_credentials(None, None)
    # Assert
    assert resolved == ("key", None)


def test_resolve_credentials_raises_when_nothing_is_set(monkeypatch) -> None:
    # Arrange
    monkeypatch.delenv("CLOCKIFY_API_KEY", raising=False)
    monkeypatch.delenv("CLOCKIFY_ADDON_TOKEN", raising=False)
    # Act
    # Assert
    with pytest.raises(MissingCredentialsError, match="CLOCKIFY_API_KEY"):
        resolve_credentials(None, None)


def test_client_config_repr_never_contains_the_addon_token() -> None:
    # Arrange
    config = ClientConfig(addon_token="super-secret-addon-token", base_url="b", reports_base_url="r")
    # Act
    rendered = repr(config)
    # Assert
    assert "super-secret-addon-token" not in rendered
