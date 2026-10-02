from __future__ import annotations

from logging import DEBUG
from typing import Final

import pytest
import respx
from httpx import ConnectError
from httpx import Response

from clockify._auth import AddonTokenAuth  # ruff: ignore[import-private-name]
from clockify._auth import ApiKeyAuth  # ruff: ignore[import-private-name]
from clockify._transport import Multipart  # ruff: ignore[import-private-name]
from clockify._transport import Transport  # ruff: ignore[import-private-name]
from clockify.config import AddonTokenProvider
from clockify.config import ApiKeyProvider
from clockify.config import ClientConfig
from clockify.errors import MissingCredentialsError
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


def _transport(api_key: str | ApiKeyProvider = API_KEY) -> Transport:
    return Transport(_config(api_key=api_key), BASE_URL, ApiKeyAuth(api_key))


@respx.mock
def test_request_sends_api_key_header() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json={"ok": True}))
    transport = _transport()
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
    transport = _transport()
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
    transport = _transport()
    # Act
    result = transport.request("DELETE", "/thing/1", kind=CqsKind.IDEMPOTENT_COMMAND)
    # Assert
    assert result is None
    transport.close()


@respx.mock
def test_success_with_empty_body_maps_to_none() -> None:
    # Arrange
    respx.delete(f"{BASE_URL}/thing/1").mock(return_value=Response(200))
    transport = _transport()
    # Act
    result = transport.request("DELETE", "/thing/1", kind=CqsKind.IDEMPOTENT_COMMAND)
    # Assert
    assert result is None
    transport.close()


@respx.mock
def test_error_status_maps_to_typed_exception() -> None:
    # Arrange
    respx.get(f"{BASE_URL}/missing").mock(return_value=Response(404, json={"code": 404, "message": "nope"}))
    transport = _transport()
    # Act
    # Assert
    with pytest.raises(NotFoundError):
        transport.request("GET", "/missing", kind=CqsKind.QUERY)
    transport.close()


@respx.mock
def test_connect_error_maps_to_transport_error() -> None:
    # Arrange
    respx.get(f"{BASE_URL}/user").mock(side_effect=ConnectError("dns failure"))
    transport = _transport()
    # Act
    # Assert
    with pytest.raises(TransportError, match="dns failure"):
        transport.request("GET", "/user", kind=CqsKind.QUERY)
    transport.close()


class _CountingProvider:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self) -> str:
        self.calls += 1
        return API_KEY


@respx.mock
def test_api_key_provider_is_deferred_until_the_first_request() -> None:
    # Arrange
    provider = _CountingProvider()
    respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json={"ok": True}))
    transport = _transport(provider)
    # Act
    transport.request("GET", "/user", kind=CqsKind.QUERY)
    # Assert
    assert provider.calls == 1
    transport.close()


@respx.mock
def test_api_key_provider_is_invoked_on_every_request() -> None:
    # Arrange
    provider = _CountingProvider()
    respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json={"ok": True}))
    transport = _transport(provider)
    # Act
    transport.request("GET", "/user", kind=CqsKind.QUERY)
    transport.request("GET", "/user", kind=CqsKind.QUERY)
    # Assert
    assert provider.calls == 2
    transport.close()


@respx.mock
def test_empty_api_key_provider_raises_missing_credentials_error() -> None:
    # Arrange
    respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json={"ok": True}))
    transport = _transport(lambda: "")
    # Act
    # Assert
    with pytest.raises(MissingCredentialsError):
        transport.request("GET", "/user", kind=CqsKind.QUERY)
    transport.close()


@respx.mock
def test_debug_log_never_contains_api_key(caplog) -> None:
    # Arrange
    respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json={"ok": True}))
    transport = _transport()
    caplog.set_level(DEBUG, logger="clockify")
    # Act
    transport.request("GET", "/user", kind=CqsKind.QUERY)
    # Assert
    assert "GET /user -> 200" in caplog.text
    assert API_KEY not in caplog.text
    transport.close()


def _addon_transport(token: str | AddonTokenProvider = API_KEY) -> Transport:
    return Transport(_config(api_key=None, addon_token=token), BASE_URL, AddonTokenAuth(token))


@respx.mock
def test_request_sends_addon_token_header_and_no_api_key_header() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json={"ok": True}))
    transport = _addon_transport()
    # Act
    transport.request("GET", "/user", kind=CqsKind.QUERY)
    # Assert
    assert route.calls[0].request.headers["X-Addon-Token"] == API_KEY
    assert "X-Api-Key" not in route.calls[0].request.headers
    transport.close()


@respx.mock
def test_addon_token_provider_is_deferred_until_the_first_request() -> None:
    # Arrange
    provider = _CountingProvider()
    respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json={"ok": True}))
    transport = _addon_transport(provider)
    calls_before = provider.calls
    # Act
    transport.request("GET", "/user", kind=CqsKind.QUERY)
    # Assert
    assert calls_before == 0
    assert provider.calls == 1
    transport.close()


@respx.mock
def test_addon_token_provider_is_invoked_on_every_request() -> None:
    # Arrange
    provider = _CountingProvider()
    respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json={"ok": True}))
    transport = _addon_transport(provider)
    # Act
    transport.request("GET", "/user", kind=CqsKind.QUERY)
    transport.request("GET", "/user", kind=CqsKind.QUERY)
    # Assert
    assert provider.calls == 2
    transport.close()


@respx.mock
def test_empty_addon_token_provider_raises_missing_credentials_error() -> None:
    # Arrange
    respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json={"ok": True}))
    transport = _addon_transport(lambda: "")
    # Act
    # Assert
    with pytest.raises(MissingCredentialsError, match="add-on token"):
        transport.request("GET", "/user", kind=CqsKind.QUERY)
    transport.close()


@respx.mock
def test_debug_log_never_contains_addon_token(caplog) -> None:
    # Arrange
    respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json={"ok": True}))
    transport = _addon_transport()
    caplog.set_level(DEBUG, logger="clockify")
    # Act
    transport.request("GET", "/user", kind=CqsKind.QUERY)
    # Assert
    assert "GET /user -> 200" in caplog.text
    assert API_KEY not in caplog.text
    transport.close()


@respx.mock
def test_multipart_body_is_sent_as_form_data_with_the_api_key() -> None:
    # Arrange
    route = respx.post(f"{BASE_URL}/thing").mock(return_value=Response(201, json={"ok": True}))
    transport = _transport()
    body = Multipart((("note", (None, b"hi", None)), ("file", ("a.txt", b"data", "text/plain"))))
    # Act
    data = transport.request("POST", "/thing", kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=body)
    # Assert
    request = route.calls[0].request
    assert data == {"ok": True}
    assert request.headers["Content-Type"].startswith("multipart/form-data; boundary=")
    assert request.headers["X-Api-Key"] == API_KEY
    assert b'name="note"\r\n\r\nhi' in request.content
    assert b'name="file"; filename="a.txt"\r\nContent-Type: text/plain\r\n\r\ndata' in request.content
    transport.close()


RECEIPT: Final = b"\x89PNG\r\n\x1a\n\x00\xff\xfe not json, not utf-8"


@respx.mock
def test_request_bytes_returns_the_raw_body_and_sends_the_api_key() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/file").mock(
        return_value=Response(200, content=RECEIPT, headers={"Content-Type": "application/octet-stream"})
    )
    transport = _transport()
    # Act
    data = transport.request_bytes("GET", "/file", kind=CqsKind.QUERY, params={"page": 2})
    # Assert
    assert data == RECEIPT
    assert route.calls[0].request.headers["X-Api-Key"] == API_KEY
    assert route.calls[0].request.url.params["page"] == "2"
    assert route.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    transport.close()


@respx.mock
def test_request_bytes_returns_empty_bytes_for_an_empty_body() -> None:
    # Arrange
    respx.get(f"{BASE_URL}/file").mock(return_value=Response(200))
    transport = _transport()
    # Act
    data = transport.request_bytes("GET", "/file", kind=CqsKind.QUERY)
    # Assert
    assert data == b""
    transport.close()


@respx.mock
def test_request_bytes_maps_an_error_status_to_a_typed_exception() -> None:
    # Arrange
    respx.get(f"{BASE_URL}/file").mock(return_value=Response(404, json={"code": 404, "message": "nope"}))
    transport = _transport()
    # Act
    # Assert
    with pytest.raises(NotFoundError):
        transport.request_bytes("GET", "/file", kind=CqsKind.QUERY)
    transport.close()


@respx.mock
def test_request_bytes_maps_a_connect_error_to_transport_error() -> None:
    # Arrange
    respx.get(f"{BASE_URL}/file").mock(side_effect=ConnectError("dns failure"))
    transport = _transport()
    # Act
    # Assert
    with pytest.raises(TransportError, match="dns failure"):
        transport.request_bytes("GET", "/file", kind=CqsKind.QUERY)
    transport.close()


@respx.mock
def test_request_bytes_debug_log_never_contains_the_api_key_or_the_body(caplog) -> None:
    # Arrange
    respx.get(f"{BASE_URL}/file").mock(return_value=Response(200, content=b"receipt-content-marker"))
    transport = _transport()
    caplog.set_level(DEBUG, logger="clockify")
    # Act
    transport.request_bytes("GET", "/file", kind=CqsKind.QUERY)
    # Assert
    assert "GET /file -> 200" in caplog.text
    assert API_KEY not in caplog.text
    assert "receipt-content-marker" not in caplog.text
    transport.close()
