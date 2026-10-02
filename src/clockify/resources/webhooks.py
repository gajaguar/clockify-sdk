from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Final
from typing import cast
from typing import override

from clockify._pagination import Page
from clockify._pagination import apaginate
from clockify._pagination import paginate
from clockify.models.webhook import Webhook
from clockify.models.webhook import WebhookCreate
from clockify.models.webhook import WebhookEventStatus
from clockify.models.webhook import WebhookList
from clockify.models.webhook import WebhookLog
from clockify.models.webhook import WebhookUpdate
from clockify.resources.base import AsyncWorkspaceResource
from clockify.resources.base import WorkspaceResource
from clockify.retry import CqsKind

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from collections.abc import Iterator

    from clockify.ids import AddonId
    from clockify.ids import WebhookId
    from clockify.models.webhook import WebhookDeliveryStatus
    from clockify.models.webhook import WebhookLogSearch
    from clockify.models.webhook import WebhookType

_NOT_PAGINATED: Final = "Clockify does not paginate webhooks; use list()."


def _list_params(webhook_type: WebhookType | None) -> dict[str, str] | None:
    return None if webhook_type is None else {"type": str(webhook_type)}


# These two endpoints take `size`, not the `page-size` of the rest of the API.
def _delivery_params(page: int, size: int, status: WebhookDeliveryStatus | None = None) -> dict[str, Any]:
    params: dict[str, Any] = {"page": page, "size": size}
    if status is not None:
        params["statuses"] = str(status)
    return params


def _search_body(search: WebhookLogSearch | None) -> dict[str, Any]:
    if search is None:
        return {}
    return search.model_dump(mode="json", by_alias=True, exclude_unset=True)


def _logs(data: object) -> list[WebhookLog]:
    return [WebhookLog.model_validate(item) for item in cast("list[dict[str, Any]]", data)]


def _event_statuses(data: object) -> list[WebhookEventStatus]:
    return [WebhookEventStatus.model_validate(item) for item in cast("list[dict[str, Any]]", data)]


class WebhooksResource(WorkspaceResource[Webhook, WebhookCreate, WebhookUpdate]):
    _path = "/webhooks"
    _read_model = Webhook

    # GET {path} (one request: the endpoint returns every webhook and takes no page)
    @override
    def list(self, *, webhook_type: WebhookType | None = None) -> Iterator[Webhook]:
        data = self._transport.request(
            "GET", self._collection_path(), kind=CqsKind.QUERY, params=_list_params(webhook_type)
        )
        return iter(WebhookList.model_validate(data).webhooks)

    # Clockify returns every webhook in one response; there is no page to ask for.
    @override
    def list_page(self, *, page: int = 1, page_size: int | None = None) -> Page[Webhook]:
        del page, page_size
        raise NotImplementedError(_NOT_PAGINATED)

    # PATCH {path}/{id}/token
    def regenerate_token(self, webhook_id: WebhookId | str) -> Webhook:
        data = self._transport.request(
            "PATCH", f"{self._item_path(webhook_id)}/token", kind=CqsKind.NON_IDEMPOTENT_COMMAND
        )
        return Webhook.model_validate(data)

    # POST {path}/{id}/logs (auto-paginating; a query despite the verb)
    def logs(self, webhook_id: WebhookId | str, *, search: WebhookLogSearch | None = None) -> Iterator[WebhookLog]:
        return paginate(lambda page: self.logs_page(webhook_id, search=search, page=page))

    # POST {path}/{id}/logs
    def logs_page(
        self,
        webhook_id: WebhookId | str,
        *,
        search: WebhookLogSearch | None = None,
        page: int = 1,
        page_size: int | None = None,
    ) -> Page[WebhookLog]:
        size = self._page_size if page_size is None else page_size
        data = self._transport.request(
            "POST",
            f"{self._item_path(webhook_id)}/logs",
            kind=CqsKind.QUERY,
            params=_delivery_params(page, size),
            json=_search_body(search),
        )
        return Page(items=_logs(data), page=page, page_size=size)

    # GET {path}/{id}/statuses (auto-paginating)
    def statuses(
        self, webhook_id: WebhookId | str, *, status: WebhookDeliveryStatus | None = None
    ) -> Iterator[WebhookEventStatus]:
        return paginate(lambda page: self.statuses_page(webhook_id, status=status, page=page))

    # GET {path}/{id}/statuses
    def statuses_page(
        self,
        webhook_id: WebhookId | str,
        *,
        status: WebhookDeliveryStatus | None = None,
        page: int = 1,
        page_size: int | None = None,
    ) -> Page[WebhookEventStatus]:
        size = self._page_size if page_size is None else page_size
        data = self._transport.request(
            "GET",
            f"{self._item_path(webhook_id)}/statuses",
            kind=CqsKind.QUERY,
            params=_delivery_params(page, size, status),
        )
        return Page(items=_event_statuses(data), page=page, page_size=size)

    # GET .../addons/{addonId}/webhooks (one request, like list())
    def list_for_addon(self, addon_id: AddonId | str) -> Iterator[Webhook]:
        data = self._transport.request(
            "GET", f"/workspaces/{self._workspace_id}/addons/{addon_id}/webhooks", kind=CqsKind.QUERY
        )
        return iter(WebhookList.model_validate(data).webhooks)


class AsyncWebhooksResource(AsyncWorkspaceResource[Webhook, WebhookCreate, WebhookUpdate]):
    _path = "/webhooks"
    _read_model = Webhook

    # GET {path} (one request: the endpoint returns every webhook and takes no page)
    @override
    async def list(self, *, webhook_type: WebhookType | None = None) -> AsyncIterator[Webhook]:
        data = await self._transport.request(
            "GET", self._collection_path(), kind=CqsKind.QUERY, params=_list_params(webhook_type)
        )
        for webhook in WebhookList.model_validate(data).webhooks:
            yield webhook

    # Clockify returns every webhook in one response; there is no page to ask for.
    @override
    async def list_page(self, *, page: int = 1, page_size: int | None = None) -> Page[Webhook]:
        del page, page_size
        raise NotImplementedError(_NOT_PAGINATED)

    # PATCH {path}/{id}/token
    async def regenerate_token(self, webhook_id: WebhookId | str) -> Webhook:
        data = await self._transport.request(
            "PATCH", f"{self._item_path(webhook_id)}/token", kind=CqsKind.NON_IDEMPOTENT_COMMAND
        )
        return Webhook.model_validate(data)

    # POST {path}/{id}/logs (auto-paginating; a query despite the verb)
    def logs(
        self, webhook_id: WebhookId | str, *, search: WebhookLogSearch | None = None
    ) -> AsyncIterator[WebhookLog]:
        return apaginate(lambda page: self.logs_page(webhook_id, search=search, page=page))

    # POST {path}/{id}/logs
    async def logs_page(
        self,
        webhook_id: WebhookId | str,
        *,
        search: WebhookLogSearch | None = None,
        page: int = 1,
        page_size: int | None = None,
    ) -> Page[WebhookLog]:
        size = self._page_size if page_size is None else page_size
        data = await self._transport.request(
            "POST",
            f"{self._item_path(webhook_id)}/logs",
            kind=CqsKind.QUERY,
            params=_delivery_params(page, size),
            json=_search_body(search),
        )
        return Page(items=_logs(data), page=page, page_size=size)

    # GET {path}/{id}/statuses (auto-paginating)
    def statuses(
        self, webhook_id: WebhookId | str, *, status: WebhookDeliveryStatus | None = None
    ) -> AsyncIterator[WebhookEventStatus]:
        return apaginate(lambda page: self.statuses_page(webhook_id, status=status, page=page))

    # GET {path}/{id}/statuses
    async def statuses_page(
        self,
        webhook_id: WebhookId | str,
        *,
        status: WebhookDeliveryStatus | None = None,
        page: int = 1,
        page_size: int | None = None,
    ) -> Page[WebhookEventStatus]:
        size = self._page_size if page_size is None else page_size
        data = await self._transport.request(
            "GET",
            f"{self._item_path(webhook_id)}/statuses",
            kind=CqsKind.QUERY,
            params=_delivery_params(page, size, status),
        )
        return Page(items=_event_statuses(data), page=page, page_size=size)

    # GET .../addons/{addonId}/webhooks (one request, like list())
    async def list_for_addon(self, addon_id: AddonId | str) -> AsyncIterator[Webhook]:
        data = await self._transport.request(
            "GET", f"/workspaces/{self._workspace_id}/addons/{addon_id}/webhooks", kind=CqsKind.QUERY
        )
        for webhook in WebhookList.model_validate(data).webhooks:
            yield webhook
