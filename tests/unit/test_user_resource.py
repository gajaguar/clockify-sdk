from __future__ import annotations

from typing import Final

import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import CqsKind

BASE_URL: Final = "https://fake.clockify.test/api/v1"

USER_PAYLOAD: Final = {
    "id": "5b0f5b1f1f1f1f1f1f1f1f1f",
    "email": "someone@example.com",
    "name": "Some One",
    "activeWorkspace": "64a1f0000000000000000001",
    "defaultWorkspace": "64a1f0000000000000000002",
    "status": "ACTIVE",
}


@respx.mock
def test_me_returns_populated_user() -> None:
    # Arrange
    route = respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json=USER_PAYLOAD))
    client = ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))
    # Act
    user = client.user.me()
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.method == "GET"
    assert respx.calls[0].request.url.path == "/api/v1/user"
    assert user.model_dump(by_alias=True) == USER_PAYLOAD
    client.close()


@respx.mock
def test_me_declares_query_cqs_kind() -> None:
    # Arrange
    respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json=USER_PAYLOAD))
    client = ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))
    # Act
    client.user.me()
    # Assert
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    client.close()


@respx.mock
def test_client_is_a_context_manager() -> None:
    # Arrange
    respx.get(f"{BASE_URL}/user").mock(return_value=Response(200, json=USER_PAYLOAD))
    # Act
    with ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY)) as client:
        user = client.user.me()
    # Assert
    assert user.email == "someone@example.com"
