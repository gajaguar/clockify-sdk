from __future__ import annotations

from clockify.models.client import Client
from clockify.models.client import ClientCreate
from clockify.models.client import ClientUpdate
from clockify.resources.base import WorkspaceResource


class ClientsResource(WorkspaceResource[Client, ClientCreate, ClientUpdate]):
    _path = "/clients"
    _read_model = Client
