from __future__ import annotations

from typing import Final

import pytest

from clockify import EVENT_TYPE_HEADER
from clockify import SIGNATURE_HEADER
from clockify import verify_signature

DELIVERY_SIGNATURE: Final = "secret-token-value"


def test_matching_signature_is_valid() -> None:
    # Arrange
    # Act
    result = verify_signature(DELIVERY_SIGNATURE, DELIVERY_SIGNATURE)
    # Assert
    assert result is True


@pytest.mark.parametrize("signature", ["other-token", DELIVERY_SIGNATURE[:-1], DELIVERY_SIGNATURE + "x", None, ""])
def test_other_or_missing_signature_is_invalid(signature: str | None) -> None:
    # Arrange
    # Act
    result = verify_signature(signature, DELIVERY_SIGNATURE)
    # Assert
    assert result is False


def test_empty_stored_token_never_validates() -> None:
    # Arrange
    # Act
    result = verify_signature("", "")
    # Assert
    assert result is False


def test_header_names_match_what_clockify_sends() -> None:
    # Arrange
    # Act
    # Assert
    assert SIGNATURE_HEADER == "Clockify-Signature"
    assert EVENT_TYPE_HEADER == "Clockify-Webhook-Event-Type"
