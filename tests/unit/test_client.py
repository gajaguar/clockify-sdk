from __future__ import annotations

from typing import Final

import pytest
import respx
from httpx import Response

from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import ConfigurationError
from clockify.retry import NO_RETRY

BASE_URL: Final = "https://fake.test/api/v1"
USER: Final = {"id": "u1", "email": "a@b.test", "name": "n", "status": "ACTIVE"}


def _options() -> ClientOptions:
    return ClientOptions(base_url=BASE_URL, retry=NO_RETRY)


@respx.mock
def test_addon_token_argument_is_sent_as_the_addon_token_header(monkeypatch) -> None:
    # Arrange
    monkeypatch.delenv("CLOCKIFY_API_KEY", raising=False)
    route = respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json=USER))
    client = ClockifyClient(addon_token="tok", options=_options())
    # Act
    client.user.me()
    # Assert
    headers = route.calls[0].request.headers
    assert headers["X-Addon-Token"] == "tok"
    assert "X-Api-Key" not in headers
    client.close()


@respx.mock
def test_addon_token_environment_variable_is_sent_end_to_end(monkeypatch) -> None:
    # Arrange
    monkeypatch.delenv("CLOCKIFY_API_KEY", raising=False)
    monkeypatch.setenv("CLOCKIFY_ADDON_TOKEN", "env-tok")
    route = respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json=USER))
    client = ClockifyClient(options=_options())
    # Act
    client.user.me()
    # Assert
    assert route.calls[0].request.headers["X-Addon-Token"] == "env-tok"
    client.close()


@respx.mock
def test_addon_token_provider_is_sent_end_to_end(monkeypatch) -> None:
    # Arrange
    monkeypatch.delenv("CLOCKIFY_API_KEY", raising=False)
    route = respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json=USER))
    client = ClockifyClient(addon_token=lambda: "provided", options=_options())
    # Act
    client.user.me()
    # Assert
    assert route.calls[0].request.headers["X-Addon-Token"] == "provided"
    client.close()


def test_api_key_and_addon_token_are_mutually_exclusive() -> None:
    # Arrange
    # Act
    # Assert
    with pytest.raises(ConfigurationError, match="not both"):
        ClockifyClient(api_key="k", addon_token="t", options=_options())
