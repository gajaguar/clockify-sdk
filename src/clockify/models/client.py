from __future__ import annotations

from clockify.ids import ClientId
from clockify.ids import WorkspaceId
from clockify.models.base import ClockifyModel


class Client(ClockifyModel):
    id: ClientId
    name: str
    email: str | None = None
    address: str | None = None
    note: str | None = None
    archived: bool = False
    cc_emails: list[str] | None = None
    currency_id: str | None = None
    workspace_id: WorkspaceId


class ClientCreate(ClockifyModel):
    name: str
    email: str | None = None
    address: str | None = None
    note: str | None = None


class ClientUpdate(ClockifyModel):
    name: str | None = None
    email: str | None = None
    address: str | None = None
    note: str | None = None
    archived: bool | None = None
    cc_emails: list[str] | None = None
    currency_id: str | None = None
