from __future__ import annotations

from typing import TYPE_CHECKING
from typing import override

from clockify.models.user_group import UserGroup
from clockify.models.user_group import UserGroupCreate
from clockify.models.user_group import UserGroupUpdate
from clockify.resources.base import AsyncWorkspaceResource
from clockify.resources.base import WorkspaceResource
from clockify.retry import CqsKind

if TYPE_CHECKING:
    from clockify.ids import UserGroupId
    from clockify.ids import UserId


class UserGroupsResource(WorkspaceResource[UserGroup, UserGroupCreate, UserGroupUpdate]):
    _path = "/user-groups"
    _read_model = UserGroup

    # Clockify has no GET .../user-groups/{id}; only list/create/update/delete exist.
    @override
    def get(self, item_id: str) -> UserGroup:
        del item_id
        message = "Clockify has no GET .../user-groups/{id} endpoint; filter list() instead."
        raise NotImplementedError(message)

    # POST {path}/{id}/users
    def add_user(self, group_id: UserGroupId | str, user_id: UserId | str) -> UserGroup:
        data = self._transport.request(
            "POST",
            f"{self._item_path(group_id)}/users",
            kind=CqsKind.NON_IDEMPOTENT_COMMAND,
            json={"userId": user_id},
        )
        return UserGroup.model_validate(data)

    # DELETE {path}/{id}/users/{userId}
    def remove_user(self, group_id: UserGroupId | str, user_id: UserId | str) -> UserGroup:
        data = self._transport.request(
            "DELETE", f"{self._item_path(group_id)}/users/{user_id}", kind=CqsKind.IDEMPOTENT_COMMAND
        )
        return UserGroup.model_validate(data)


class AsyncUserGroupsResource(AsyncWorkspaceResource[UserGroup, UserGroupCreate, UserGroupUpdate]):
    _path = "/user-groups"
    _read_model = UserGroup

    # Clockify has no GET .../user-groups/{id}; only list/create/update/delete exist.
    @override
    async def get(self, item_id: str) -> UserGroup:
        del item_id
        message = "Clockify has no GET .../user-groups/{id} endpoint; filter list() instead."
        raise NotImplementedError(message)

    # POST {path}/{id}/users
    async def add_user(self, group_id: UserGroupId | str, user_id: UserId | str) -> UserGroup:
        data = await self._transport.request(
            "POST",
            f"{self._item_path(group_id)}/users",
            kind=CqsKind.NON_IDEMPOTENT_COMMAND,
            json={"userId": user_id},
        )
        return UserGroup.model_validate(data)

    # DELETE {path}/{id}/users/{userId}
    async def remove_user(self, group_id: UserGroupId | str, user_id: UserId | str) -> UserGroup:
        data = await self._transport.request(
            "DELETE", f"{self._item_path(group_id)}/users/{user_id}", kind=CqsKind.IDEMPOTENT_COMMAND
        )
        return UserGroup.model_validate(data)
