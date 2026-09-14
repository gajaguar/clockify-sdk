from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

from clockify._pagination import Page
from clockify._pagination import paginate
from clockify.models.task import Task
from clockify.models.task import TaskCreate
from clockify.models.task import TaskUpdate
from clockify.retry import CqsKind

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any

    from clockify._transport import Transport
    from clockify.ids import ProjectId
    from clockify.ids import WorkspaceId


class TasksResource:
    # Tasks nest under a project, so every method takes project_id explicitly
    # rather than being bound to it at construction time, unlike WorkspaceResource.
    def __init__(self, transport: Transport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        self._transport = transport
        self._workspace_id = workspace_id
        self._page_size = page_size

    # POST .../projects/{projectId}/tasks
    def create(self, project_id: ProjectId, payload: TaskCreate) -> Task:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = self._transport.request(
            "POST", self._collection_path(project_id), kind=CqsKind.NON_IDEMPOTENT_COMMAND, json=body
        )
        return Task.model_validate(data)

    # DELETE .../projects/{projectId}/tasks/{id}
    def delete(self, project_id: ProjectId, task_id: str) -> None:
        self._transport.request("DELETE", self._item_path(project_id, task_id), kind=CqsKind.IDEMPOTENT_COMMAND)

    # GET .../projects/{projectId}/tasks/{id}
    def get(self, project_id: ProjectId, task_id: str) -> Task:
        data = self._transport.request("GET", self._item_path(project_id, task_id), kind=CqsKind.QUERY)
        return Task.model_validate(data)

    # GET .../projects/{projectId}/tasks (auto-paginating)
    def list(self, project_id: ProjectId) -> Iterator[Task]:
        return paginate(lambda page: self.list_page(project_id, page=page))

    # GET .../projects/{projectId}/tasks
    def list_page(self, project_id: ProjectId, *, page: int = 1, page_size: int | None = None) -> Page[Task]:
        resolved_page_size = self._page_size if page_size is None else page_size
        data = self._transport.request(
            "GET",
            self._collection_path(project_id),
            kind=CqsKind.QUERY,
            params={"page": page, "page-size": resolved_page_size},
        )
        items = [Task.model_validate(item) for item in cast("list[dict[str, Any]]", data)]
        return Page(items=items, page=page, page_size=resolved_page_size)

    # PUT .../projects/{projectId}/tasks/{id}
    def update(self, project_id: ProjectId, task_id: str, payload: TaskUpdate) -> Task:
        body = payload.model_dump(mode="json", by_alias=True, exclude_unset=True)
        data = self._transport.request(
            "PUT", self._item_path(project_id, task_id), kind=CqsKind.IDEMPOTENT_COMMAND, json=body
        )
        return Task.model_validate(data)

    def _collection_path(self, project_id: ProjectId) -> str:
        return f"/workspaces/{self._workspace_id}/projects/{project_id}/tasks"

    def _item_path(self, project_id: ProjectId, task_id: str) -> str:
        return f"{self._collection_path(project_id)}/{task_id}"
