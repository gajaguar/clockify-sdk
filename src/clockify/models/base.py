from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


class ClockifyModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
        frozen=True,
    )
