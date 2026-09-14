from __future__ import annotations

from typing import Final

import pytest
from httpx import Request
from httpx import Response

from clockify.errors import AuthenticationError
from clockify.errors import ClockifyAPIError
from clockify.errors import ConflictError
from clockify.errors import ForbiddenError
from clockify.errors import NotFoundError
from clockify.errors import RateLimitError
from clockify.errors import ServerError
from clockify.errors import ValidationError
from clockify.errors import error_for_response

_REQUEST: Final = Request("GET", "https://api.clockify.me/api/v1/user")


def _response(status_code, *, json=None, text=None, headers=None):
    if json is not None:
        return Response(status_code=status_code, json=json, request=_REQUEST, headers=headers)
    return Response(status_code=status_code, text=text or "", request=_REQUEST, headers=headers)


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (400, ValidationError),
        (401, AuthenticationError),
        (403, ForbiddenError),
        (404, NotFoundError),
        (409, ConflictError),
        (422, ValidationError),
        (429, RateLimitError),
        (500, ServerError),
        (502, ServerError),
        (503, ServerError),
        (504, ServerError),
        (418, ClockifyAPIError),
    ],
)
def test_error_for_response_maps_status(status, expected):
    # Arrange
    response = _response(status, json={"code": 1, "message": "boom"})
    # Act
    error = error_for_response(response)
    # Assert
    assert type(error) is expected  # pylint: disable=unidiomatic-typecheck
    assert error.status_code == status


def test_unmapped_status_is_plain_api_error():
    # Arrange
    response = _response(418, text="teapot")
    # Act
    error = error_for_response(response)
    # Assert
    assert type(error) is ClockifyAPIError  # pylint: disable=unidiomatic-typecheck
    assert error.raw == "teapot"


def test_well_formed_body_populates_code_and_message():
    # Arrange
    response = _response(404, json={"code": 404, "message": "Project not found"})
    # Act
    error = error_for_response(response)
    # Assert
    assert error.code == "404"
    assert error.message == "Project not found"
    assert error.raw is None


@pytest.mark.parametrize("body", ["", "<html>oops</html>", "{not json", "[1, 2, 3]", '{"other": 1}'])
def test_unparsable_body_populates_raw(body):
    # Arrange
    response = _response(500, text=body)
    # Act
    error = error_for_response(response)
    # Assert
    assert error.raw == body
    assert error.code is None
    assert error.message is None


def test_rate_limit_reads_retry_after():
    # Arrange
    response = _response(429, json={"message": "slow down"}, headers={"Retry-After": "2.5"})
    # Act
    error = error_for_response(response)
    # Assert
    assert isinstance(error, RateLimitError)
    assert error.retry_after == pytest.approx(2.5)


def test_rate_limit_without_retry_after():
    # Arrange
    response = _response(429, text="")
    # Act
    error = error_for_response(response)
    # Assert
    assert isinstance(error, RateLimitError)
    assert error.retry_after is None


def test_rate_limit_with_unparsable_retry_after():
    # Arrange
    response = _response(429, text="", headers={"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"})
    # Act
    error = error_for_response(response)
    # Assert
    assert isinstance(error, RateLimitError)
    assert error.retry_after is None


def test_error_carries_request_and_response():
    # Arrange
    response = _response(403, json={"code": 403, "message": "nope"})
    # Act
    error = error_for_response(response)
    # Assert
    assert error.request is _REQUEST
    assert error.response is response
    assert str(error) == "nope"
