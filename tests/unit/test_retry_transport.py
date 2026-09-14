from __future__ import annotations

import httpx
import pytest

from clockify._retry_transport import RetryTransport  # ruff: ignore[import-private-name]
from clockify.retry import CqsKind
from clockify.retry import RetryPolicy


class _SequenceTransport(httpx.BaseTransport):
    def __init__(self, responses: list[httpx.Response]) -> None:
        self.responses = list(responses)
        self.requests: list[httpx.Request] = []

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if len(self.responses) > 1:
            return self.responses.pop(0)
        return self.responses[0]


def _request(kind: CqsKind | None = None) -> httpx.Request:
    extensions = {} if kind is None else {"clockify_cqs": kind}
    return httpx.Request("GET", "https://fake.test/user", extensions=extensions)


def _response(status: int, headers: dict[str, str] | None = None) -> httpx.Response:
    return httpx.Response(status, headers=headers, json={"status": status})


def test_retries_429_and_honors_retry_after() -> None:
    # Arrange
    inner = _SequenceTransport([_response(429, {"Retry-After": "2.5"}), _response(200)])
    slept: list[float] = []
    transport = RetryTransport(inner, policy=RetryPolicy(), sleep=slept.append)
    # Act
    response = transport.handle_request(_request(CqsKind.NON_IDEMPOTENT_COMMAND))
    # Assert
    assert response.status_code == 200
    assert len(inner.requests) == 2
    assert slept == [2.5]


def test_ignores_unparsable_retry_after_header() -> None:
    # Arrange
    inner = _SequenceTransport([_response(429, {"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"}), _response(200)])
    slept: list[float] = []
    policy = RetryPolicy(random_source=lambda: 1.0)
    transport = RetryTransport(inner, policy=policy, sleep=slept.append)
    # Act
    response = transport.handle_request(_request(CqsKind.QUERY))
    # Assert
    assert response.status_code == 200
    assert slept == pytest.approx([policy.backoff_base])


def test_retries_503_for_query() -> None:
    # Arrange
    inner = _SequenceTransport([_response(503), _response(200)])
    slept: list[float] = []
    policy = RetryPolicy(random_source=lambda: 1.0)
    transport = RetryTransport(inner, policy=policy, sleep=slept.append)
    # Act
    response = transport.handle_request(_request(CqsKind.QUERY))
    # Assert
    assert response.status_code == 200
    assert len(inner.requests) == 2
    assert len(slept) == 1


def test_does_not_retry_503_for_non_idempotent_command() -> None:
    # Arrange
    inner = _SequenceTransport([_response(503), _response(200)])
    slept: list[float] = []
    transport = RetryTransport(inner, policy=RetryPolicy(), sleep=slept.append)
    # Act
    response = transport.handle_request(_request(CqsKind.NON_IDEMPOTENT_COMMAND))
    # Assert
    assert response.status_code == 503
    assert len(inner.requests) == 1
    assert not slept


def test_missing_kind_defaults_to_non_idempotent_command() -> None:
    # Arrange
    inner = _SequenceTransport([_response(500), _response(200)])
    slept: list[float] = []
    transport = RetryTransport(inner, policy=RetryPolicy(), sleep=slept.append)
    # Act
    response = transport.handle_request(_request())
    # Assert
    assert response.status_code == 500
    assert not slept


def test_exhausting_max_attempts_returns_final_response() -> None:
    # Arrange
    inner = _SequenceTransport([_response(429, {"Retry-After": "0"})])
    slept: list[float] = []
    transport = RetryTransport(inner, policy=RetryPolicy(max_attempts=3), sleep=slept.append)
    # Act
    response = transport.handle_request(_request(CqsKind.QUERY))
    # Assert
    assert response.status_code == 429
    assert len(inner.requests) == len(slept) + 1
    assert len(inner.requests) <= 4


def test_body_is_read_before_returning() -> None:
    # Arrange
    inner = _SequenceTransport([_response(200)])
    transport = RetryTransport(inner, policy=RetryPolicy(), sleep=lambda _: None)
    # Act
    response = transport.handle_request(_request(CqsKind.QUERY))
    # Assert
    assert response.json() == {"status": 200}


def test_close_closes_next_transport() -> None:
    # Arrange
    inner = httpx.MockTransport(lambda _: httpx.Response(200))
    transport = RetryTransport(inner, policy=RetryPolicy(), sleep=lambda _: None)
    # Act
    transport.close()
    # Assert
    assert transport.next_transport is inner
