from __future__ import annotations

from typing import override

from clockify.models.user_group import UserGroup
from clockify.models.user_group import UserGroupCreate
from clockify.models.user_group import UserGroupUpdate
from clockify.resources.base import WorkspaceResource


class UserGroupsResource(WorkspaceResource[UserGroup, UserGroupCreate, UserGroupUpdate]):
    _path = "/user-groups"
    _read_model = UserGroup

    # Clockify has no GET .../user-groups/{id}; only list/create/update/delete exist.
    @override
    def get(self, item_id: str) -> UserGroup:
        del item_id
        message = "Clockify has no GET .../user-groups/{id} endpoint; filter list() instead."
        raise NotImplementedError(message)
