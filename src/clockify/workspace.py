from __future__ import annotations

from typing import TYPE_CHECKING

from clockify.resources.clients import ClientsResource
from clockify.resources.custom_fields import CustomFieldsResource
from clockify.resources.projects import ProjectsResource
from clockify.resources.tags import TagsResource
from clockify.resources.tasks import TasksResource
from clockify.resources.user_groups import UserGroupsResource
from clockify.resources.users import UsersResource

if TYPE_CHECKING:
    from clockify._transport import Transport
    from clockify.ids import WorkspaceId


class WorkspaceClient:
    def __init__(self, transport: Transport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        self.id = workspace_id
        self.users = UsersResource(transport, workspace_id, page_size=page_size)
        self.user_groups = UserGroupsResource(transport, workspace_id, page_size=page_size)
        self.projects = ProjectsResource(transport, workspace_id, page_size=page_size)
        self.tasks = TasksResource(transport, workspace_id, page_size=page_size)
        self.clients = ClientsResource(transport, workspace_id, page_size=page_size)
        self.tags = TagsResource(transport, workspace_id, page_size=page_size)
        self.custom_fields = CustomFieldsResource(transport, workspace_id, page_size=page_size)
