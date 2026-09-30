from __future__ import annotations

from asyncio import sleep as yield_to_loop

import httpx

from clockify._retry_transport import AsyncRetryTransport  # ruff: ignore[import-private-name]
from clockify.retry import CqsKind
from clockify.retry import RetryPolicy


class _SequenceTransport(httpx.AsyncBaseTransport):
    def __init__(self, responses: list[httpx.Response]) -> None:
        self.responses = list(responses)
        self.requests: list[httpx.Request] = []
        self.closed = False

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if len(self.responses) > 1:
            return self.responses.pop(0)
        return self.responses[0]

    async def aclose(self) -> None:
        self.closed = True


def _request(kind: CqsKind | None = None) -> httpx.Request:
    extensions = {} if kind is None else {"clockify_cqs": kind}
    return httpx.Request("GET", "https://fake.test/user", extensions=extensions)


def _response(status: int, headers: dict[str, str] | None = None) -> httpx.Response:
    return httpx.Response(status, headers=headers, json={"status": status})


def _transport(inner: _SequenceTransport, slept: list[float], policy: RetryPolicy | None = None):
    async def sleep(delay: float) -> None:
        await yield_to_loop(0)
        slept.append(delay)

    return AsyncRetryTransport(inner, policy=policy or RetryPolicy(), sleep=sleep)


async def test_retries_429_and_honors_retry_after() -> None:
    # Arrange
    inner = _SequenceTransport([_response(429, {"Retry-After": "2.5"}), _response(200)])
    slept: list[float] = []
    transport = _transport(inner, slept)
    # Act
    response = await transport.handle_async_request(_request(CqsKind.NON_IDEMPOTENT_COMMAND))
    # Assert
    assert response.status_code == 200
    assert slept == [2.5]
    assert len(inner.requests) == 2


async def test_retries_5xx_for_a_query() -> None:
    # Arrange
    inner = _SequenceTransport([_response(503), _response(200)])
    slept: list[float] = []
    transport = _transport(inner, slept, RetryPolicy(random_source=lambda: 1.0))
    # Act
    response = await transport.handle_async_request(_request(CqsKind.QUERY))
    # Assert
    assert response.status_code == 200
    assert slept == [0.5]


async def test_does_not_retry_5xx_for_a_non_idempotent_command() -> None:
    # Arrange
    inner = _SequenceTransport([_response(503), _response(200)])
    slept: list[float] = []
    transport = _transport(inner, slept)
    # Act
    response = await transport.handle_async_request(_request(CqsKind.NON_IDEMPOTENT_COMMAND))
    # Assert
    assert response.status_code == 503
    assert slept == []
    assert len(inner.requests) == 1


async def test_missing_kind_defaults_to_non_idempotent_command() -> None:
    # Arrange
    inner = _SequenceTransport([_response(500), _response(200)])
    transport = _transport(inner, [])
    # Act
    response = await transport.handle_async_request(_request())
    # Assert
    assert response.status_code == 500


async def test_stops_after_max_attempts() -> None:
    # Arrange
    inner = _SequenceTransport([_response(429)])
    slept: list[float] = []
    transport = _transport(inner, slept, RetryPolicy(max_attempts=3, random_source=lambda: 0.0))
    # Act
    response = await transport.handle_async_request(_request(CqsKind.QUERY))
    # Assert
    assert response.status_code == 429
    assert len(inner.requests) == 3
    assert len(slept) == 2


async def test_aclose_closes_the_inner_transport() -> None:
    # Arrange
    inner = _SequenceTransport([_response(200)])
    transport = _transport(inner, [])
    # Act
    await transport.aclose()
    # Assert
    assert inner.closed
