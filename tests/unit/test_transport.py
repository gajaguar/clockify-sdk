from __future__ import annotations

from logging import DEBUG
from typing import Final

import pytest
import respx
from httpx import ConnectError
from httpx import Response

from clockify._transport import Transport  # ruff: ignore[import-private-name]
from clockify.config import ClientConfig
from clockify.errors import NotFoundError
from clockify.errors import TransportError
from clockify.retry import NO_RETRY
from clockify.retry import CqsKind

BASE_URL: Final = "https://api.clockify.me/api/v1"
API_KEY: Final = "super-secret-key-value"


def _config(**overrides) -> ClientConfig:
    defaults = {
        "api_key": API_KEY,
        "base_url": BASE_URL,
        "reports_base_url": "https://reports.api.clockify.me/v1",
        "retry": NO_RETRY,
    }
    return ClientConfig(**(defaults | overrides))


@respx.mock
def test_request_sends_api_key_header() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json={"ok": True}))
    transport = Transport(_config(), BASE_URL)
    # Act
    data = transport.request("GET", "/user", kind=CqsKind.QUERY)
    # Assert
    assert data == {"ok": True}
    assert route.calls[0].request.headers["X-Api-Key"] == API_KEY
    assert route.calls[0].request.headers["User-Agent"] == "clockify-unofficial-sdk"
    transport.close()


@respx.mock
def test_request_forwards_params_and_json() -> None:
    # Arrange
    route = respx.post(f"{BASE_URL}/thing").mock(return_value=Response(200, json=[]))
    transport = Transport(_config(), BASE_URL)
    # Act
    transport.request("POST", "/thing", kind=CqsKind.QUERY, params={"page": 2}, json={"name": "x"})
    # Assert
    assert route.calls[0].request.url.params["page"] == "2"
    assert route.calls[0].request.content == b'{"name":"x"}'
    transport.close()


@respx.mock
def test_no_content_maps_to_none() -> None:
    # Arrange
    respx.delete(f"{BASE_URL}/thing/1").mock(return_value=Response(204))
    transport = Transport(_config(), BASE_URL)
    # Act
    result = transport.request("DELETE", "/thing/1", kind=CqsKind.IDEMPOTENT_COMMAND)
    # Assert
    assert result is None
    transport.close()


@respx.mock
def test_error_status_maps_to_typed_exception() -> None:
    # Arrange
    respx.get(f"{BASE_URL}/missing").mock(return_value=Response(404, json={"code": 404, "message": "nope"}))
    transport = Transport(_config(), BASE_URL)
    # Act
    # Assert
    with pytest.raises(NotFoundError):
        transport.request("GET", "/missing", kind=CqsKind.QUERY)
    transport.close()


@respx.mock
def test_connect_error_maps_to_transport_error() -> None:
    # Arrange
    respx.get(f"{BASE_URL}/user").mock(side_effect=ConnectError("dns failure"))
    transport = Transport(_config(), BASE_URL)
    # Act
    # Assert
    with pytest.raises(TransportError, match="dns failure"):
        transport.request("GET", "/user", kind=CqsKind.QUERY)
    transport.close()


@respx.mock
def test_debug_log_never_contains_api_key(caplog) -> None:
    # Arrange
    respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json={"ok": True}))
    transport = Transport(_config(), BASE_URL)
    caplog.set_level(DEBUG, logger="clockify")
    # Act
    transport.request("GET", "/user", kind=CqsKind.QUERY)
    # Assert
    assert "GET /user -> 200" in caplog.text
    assert API_KEY not in caplog.text
    transport.close()
