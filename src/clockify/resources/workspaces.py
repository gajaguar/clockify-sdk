from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

from clockify.models.workspace import Workspace
from clockify.retry import CqsKind

if TYPE_CHECKING:
    from typing import Any

    from clockify._transport import Transport
    from clockify.ids import WorkspaceId


class WorkspacesResource:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    # GET /workspaces/<workspaceId>
    def get(self, workspace_id: WorkspaceId) -> Workspace:
        data = self._transport.request("GET", f"/workspaces/{workspace_id}", kind=CqsKind.QUERY)
        return Workspace.model_validate(data)

    # GET /workspaces
    def list(self) -> list[Workspace]:
        data = self._transport.request("GET", "/workspaces", kind=CqsKind.QUERY)
        return [Workspace.model_validate(item) for item in cast("list[dict[str, Any]]", data)]
