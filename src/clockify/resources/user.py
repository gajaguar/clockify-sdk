from __future__ import annotations

from typing import TYPE_CHECKING

from clockify.models import User
from clockify.retry import CqsKind

if TYPE_CHECKING:
    from clockify._transport import Transport


class UserResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    # GET /user
    def me(self) -> User:
        data = self._transport.request("GET", "/user", kind=CqsKind.QUERY)
        return User.model_validate(data)
