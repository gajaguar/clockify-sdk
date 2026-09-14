from __future__ import annotations

import datetime
import re
from typing import Annotated
from typing import Final

from pydantic import BeforeValidator
from pydantic import PlainSerializer

from clockify.errors import ErrorBody
from clockify.errors import ValidationError

_DURATION_RE: Final = re.compile(
    r"^(?P<sign>[+-])?P(?:(?P<days>\d+)D)?"
    r"(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+(?:\.\d+)?)S)?)?$"
)

_SECONDS_PER_MINUTE: Final = 60
_SECONDS_PER_HOUR: Final = 3600
_SECONDS_PER_DAY: Final = 86400


def _invalid(value: object, kind: str) -> ValidationError:
    message = f"Invalid Clockify {kind}: {value!r}"
    return ValidationError(body=ErrorBody(message=message))


def parse_duration(value: str) -> datetime.timedelta:
    if not isinstance(value, str):
        raise _invalid(value, "duration")
    match = _DURATION_RE.match(value)
    if match is None:
        raise _invalid(value, "duration")
    groups = match.groupdict()
    if all(groups[key] is None for key in ("days", "hours", "minutes", "seconds")):
        raise _invalid(value, "duration")
    total = datetime.timedelta(
        days=int(groups["days"] or 0),
        hours=int(groups["hours"] or 0),
        minutes=int(groups["minutes"] or 0),
        seconds=float(groups["seconds"] or 0),
    )
    if groups["sign"] == "-":
        return -total
    return total


def format_duration(value: datetime.timedelta) -> str:
    if not isinstance(value, datetime.timedelta):
        raise _invalid(value, "duration")
    total = value.total_seconds()
    sign = "-" if total < 0 else ""
    total = abs(total)
    days, rest = divmod(total, _SECONDS_PER_DAY)
    hours, rest = divmod(rest, _SECONDS_PER_HOUR)
    minutes, seconds = divmod(rest, _SECONDS_PER_MINUTE)
    parts = ""
    if days:
        parts += f"{int(days)}D"
    time_parts = ""
    if hours:
        time_parts += f"{int(hours)}H"
    if minutes:
        time_parts += f"{int(minutes)}M"
    if seconds or (not parts and not time_parts):
        rendered = f"{seconds:.3f}".rstrip("0").rstrip(".") if seconds % 1 else str(int(seconds))
        time_parts += f"{rendered}S"
    if time_parts:
        parts += f"T{time_parts}"
    return f"{sign}P{parts}"


def parse_instant(value: str) -> datetime.datetime:
    if not isinstance(value, str):
        raise _invalid(value, "instant")
    try:
        parsed = datetime.datetime.fromisoformat(value)
    except ValueError as exc:
        raise _invalid(value, "instant") from exc
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=datetime.UTC)
    return parsed.astimezone(datetime.UTC)


def format_instant(value: datetime.datetime) -> str:
    if not isinstance(value, datetime.datetime):
        raise _invalid(value, "instant")
    moment = value.replace(tzinfo=datetime.UTC) if value.tzinfo is None else value.astimezone(datetime.UTC)
    return moment.strftime("%Y-%m-%dT%H:%M:%S") + (f".{moment.microsecond:06d}Z" if moment.microsecond else "Z")


def _validate_duration(value: object) -> datetime.timedelta:
    if isinstance(value, datetime.timedelta):
        return value
    if isinstance(value, str):
        return parse_duration(value)
    raise _invalid(value, "duration")


def _validate_instant(value: object) -> datetime.datetime:
    if isinstance(value, datetime.datetime):
        return parse_instant(format_instant(value))
    if isinstance(value, str):
        return parse_instant(value)
    raise _invalid(value, "instant")


type ClockifyDuration = Annotated[  # pylint: disable=app-module-const-naming
    datetime.timedelta,
    BeforeValidator(_validate_duration),
    PlainSerializer(format_duration, return_type=str, when_used="json"),
]

type ClockifyInstant = Annotated[  # pylint: disable=app-module-const-naming
    datetime.datetime,
    BeforeValidator(_validate_instant),
    PlainSerializer(format_instant, return_type=str, when_used="json"),
]
