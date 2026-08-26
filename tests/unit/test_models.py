from __future__ import annotations

from typing import Final

import pytest
from pydantic import ValidationError as PydanticValidationError
from pydantic.alias_generators import to_camel

from clockify.models import ClockifyModel
from clockify.models import TimeEntryType
from clockify.models import TimeInterval
from clockify.models import User
from clockify.models import UserStatus

_PAYLOAD: Final = {
    "id": "64a1f",
    "email": "dev@gajaguar.com",
    "name": "Dev",
    "activeWorkspace": "ws-1",
    "defaultWorkspace": "ws-2",
    "status": "ACTIVE",
}


def test_camel_case_alias_round_trip():
    # Arrange
    payload = dict(_PAYLOAD)
    # Act
    user = User.model_validate(payload)
    dumped = user.model_dump(by_alias=True)
    # Assert
    assert user.active_workspace == "ws-1"
    assert user.default_workspace == "ws-2"
    assert dumped["activeWorkspace"] == "ws-1"
    assert dumped["defaultWorkspace"] == "ws-2"
    assert dumped == {
        "id": "64a1f",
        "email": "dev@gajaguar.com",
        "name": "Dev",
        "activeWorkspace": "ws-1",
        "defaultWorkspace": "ws-2",
        "status": UserStatus.ACTIVE,
    }


def test_populate_by_name_accepts_snake_case():
    # Arrange
    payload = {k: v for k, v in _PAYLOAD.items() if k != "activeWorkspace"} | {"active_workspace": "ws-9"}
    # Act
    user = User.model_validate(payload)
    # Assert
    assert user.active_workspace == "ws-9"


def test_optional_workspaces_default_to_none():
    # Arrange
    payload = {"id": "1", "email": "a@b.c", "name": "A", "status": "ACTIVE"}
    # Act
    user = User.model_validate(payload)
    # Assert
    assert user.active_workspace is None
    assert user.default_workspace is None


def test_model_is_frozen():
    # Arrange
    user = User.model_validate(_PAYLOAD)
    # Act
    with pytest.raises(PydanticValidationError) as excinfo:
        user.name = "Other"
    # Assert
    assert isinstance(excinfo.value, PydanticValidationError)


def test_extra_keys_are_allowed_and_retrievable():
    # Arrange
    payload = {**_PAYLOAD, "profilePicture": "https://example.invalid/a.png"}
    # Act
    user = User.model_validate(payload)
    # Assert
    assert user.model_extra is not None
    assert user.model_extra["profilePicture"] == "https://example.invalid/a.png"


def test_unknown_status_falls_back_to_unknown():
    # Arrange
    payload = {**_PAYLOAD, "status": "SOMETHING_NEW"}
    # Act
    user = User.model_validate(payload)
    # Assert
    assert user.status is UserStatus.UNKNOWN


@pytest.mark.parametrize("value", ["ACTIVE", "PENDING_EMAIL_VERIFICATION", "DELETED"])
def test_known_statuses_are_preserved(value):
    # Arrange
    payload = {**_PAYLOAD, "status": value}
    # Act
    user = User.model_validate(payload)
    # Assert
    assert user.status == value


def test_base_model_config():
    # Arrange
    config = ClockifyModel.model_config
    # Act
    extra = config["extra"]
    # Assert
    assert extra == "allow"
    assert config["frozen"] is True
    assert config["populate_by_name"] is True
    assert config == {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "validate_by_alias": True,
        "validate_by_name": True,
        "extra": "allow",
        "frozen": True,
    }


def test_time_interval_round_trips_instant_and_duration():
    # Arrange
    payload = {"start": "2026-08-26T10:00:00Z", "end": "2026-08-26T11:30:00Z", "duration": "PT1H30M"}
    # Act
    interval = TimeInterval.model_validate(payload)
    dumped = interval.model_dump(mode="json", by_alias=True)
    # Assert
    assert interval.start.tzinfo is not None
    assert interval.duration.total_seconds() == 5400
    assert dumped == payload


def test_unknown_time_entry_type_falls_back_to_unknown():
    # Arrange
    # Act
    entry_type = TimeEntryType("SOMETHING_NEW")
    # Assert
    assert entry_type is TimeEntryType.UNKNOWN
