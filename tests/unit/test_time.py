from __future__ import annotations

import datetime

import pytest
from pydantic import BaseModel

from clockify._time import ClockifyDuration  # ruff: ignore[import-private-name]
from clockify._time import ClockifyInstant  # ruff: ignore[import-private-name]
from clockify._time import format_duration  # ruff: ignore[import-private-name]
from clockify._time import format_instant  # ruff: ignore[import-private-name]
from clockify._time import parse_duration  # ruff: ignore[import-private-name]
from clockify._time import parse_instant  # ruff: ignore[import-private-name]
from clockify.errors import ValidationError


class _Sample(BaseModel):
    duration: ClockifyDuration
    instant: ClockifyInstant


@pytest.mark.parametrize(
    ("text", "delta"),
    [
        ("PT0S", datetime.timedelta()),
        ("PT1H30M", datetime.timedelta(hours=1, minutes=30)),
        ("P1DT2H3M4S", datetime.timedelta(days=1, hours=2, minutes=3, seconds=4)),
        ("P2D", datetime.timedelta(days=2)),
        ("-PT45M", -datetime.timedelta(minutes=45)),
    ],
)
def test_duration_round_trip(text, delta):
    # Arrange
    parsed = parse_duration(text)
    # Act
    rendered = format_duration(parsed)
    # Assert
    assert parsed == delta
    assert rendered == text


@pytest.mark.parametrize("text", ["", "P", "1H", "PT", "P1Y", "PT1W", "nonsense", "PT1H30"])
def test_parse_duration_invalid(text):
    # Arrange
    parser = parse_duration
    # Act
    with pytest.raises(ValidationError) as excinfo:
        parser(text)
    # Assert
    assert isinstance(excinfo.value, ValidationError)


def test_format_duration_rejects_non_timedelta():
    # Arrange
    value = "PT1H"
    # Act
    with pytest.raises(ValidationError) as excinfo:
        format_duration(value)
    # Assert
    assert isinstance(excinfo.value, ValidationError)


def test_instant_round_trip():
    # Arrange
    text = "2026-08-26T10:00:00Z"
    # Act
    parsed = parse_instant(text)
    # Assert
    assert parsed == datetime.datetime(2026, 8, 26, 10, 0, tzinfo=datetime.UTC)
    assert format_instant(parsed) == text


def test_parse_instant_normalizes_offset_and_naive():
    # Arrange
    offset = "2026-08-26T12:00:00+02:00"
    # Act
    parsed = parse_instant(offset)
    naive = parse_instant("2026-08-26T10:00:00")
    # Assert
    assert format_instant(parsed) == "2026-08-26T10:00:00Z"
    assert naive.tzinfo is datetime.UTC


def test_format_instant_keeps_microseconds():
    # Arrange
    moment = datetime.datetime(2026, 8, 26, 10, 0, 0, 500000, tzinfo=datetime.UTC)
    # Act
    rendered = format_instant(moment)
    # Assert
    assert rendered == "2026-08-26T10:00:00.500000Z"


@pytest.mark.parametrize("text", ["", "not-a-date", "2026-13-45T99:99:99Z"])
def test_parse_instant_invalid(text):
    # Arrange
    parser = parse_instant
    # Act
    with pytest.raises(ValidationError) as excinfo:
        parser(text)
    # Assert
    assert isinstance(excinfo.value, ValidationError)


def test_format_instant_rejects_non_datetime():
    # Arrange
    value = 1
    # Act
    with pytest.raises(ValidationError) as excinfo:
        format_instant(value)
    # Assert
    assert isinstance(excinfo.value, ValidationError)


def test_annotated_types_round_trip_through_model():
    # Arrange
    payload = {"duration": "PT1H30M", "instant": "2026-08-26T10:00:00Z"}
    # Act
    model = _Sample.model_validate(payload)
    dumped = model.model_dump(mode="json")
    # Assert
    assert model.duration == datetime.timedelta(hours=1, minutes=30)
    assert model.instant == datetime.datetime(2026, 8, 26, 10, 0, tzinfo=datetime.UTC)
    assert dumped == payload


def test_annotated_types_accept_native_objects():
    # Arrange
    payload = {
        "duration": datetime.timedelta(seconds=90),
        "instant": datetime.datetime(2026, 8, 26, 10, 0, tzinfo=datetime.UTC),
    }
    # Act
    model = _Sample.model_validate(payload)
    # Assert
    assert model.model_dump(mode="json") == {"duration": "PT1M30S", "instant": "2026-08-26T10:00:00Z"}


def test_annotated_types_reject_bad_input():
    # Arrange
    payload = {"duration": 5, "instant": 5}
    # Act
    with pytest.raises(ValidationError) as excinfo:
        _Sample.model_validate(payload)
    # Assert
    assert isinstance(excinfo.value, ValidationError)
