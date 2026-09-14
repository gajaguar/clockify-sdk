from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

from clockify._pagination import Page
from clockify._pagination import paginate
from clockify.models.user import User
from clockify.retry import CqsKind

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any

    from clockify._transport import Transport
    from clockify.ids import WorkspaceId


class UsersResource:
    # Clockify has no GET .../users/{id}; only the collection is documented.
    def __init__(self, transport: Transport, workspace_id: WorkspaceId, *, page_size: int = 50) -> None:
        self._transport = transport
        self._workspace_id = workspace_id
        self._page_size = page_size

    # GET .../users (auto-paginating)
    def list(self) -> Iterator[User]:
        return paginate(lambda page: self.list_page(page=page))

    # GET .../users
    def list_page(self, *, page: int = 1, page_size: int | None = None) -> Page[User]:
        resolved_page_size = self._page_size if page_size is None else page_size
        data = self._transport.request(
            "GET",
            f"/workspaces/{self._workspace_id}/users",
            kind=CqsKind.QUERY,
            params={"page": page, "page-size": resolved_page_size},
        )
        items = [User.model_validate(item) for item in cast("list[dict[str, Any]]", data)]
        return Page(items=items, page=page, page_size=resolved_page_size)
