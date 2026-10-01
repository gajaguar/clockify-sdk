from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Final
from typing import override

from clockify.models.webhook import Webhook
from clockify.models.webhook import WebhookCreate
from clockify.models.webhook import WebhookList
from clockify.models.webhook import WebhookUpdate
from clockify.resources.base import AsyncWorkspaceResource
from clockify.resources.base import WorkspaceResource
from clockify.retry import CqsKind

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from collections.abc import Iterator

    from clockify._pagination import Page
    from clockify.ids import WebhookId
    from clockify.models.webhook import WebhookType

_NOT_PAGINATED: Final = "Clockify does not paginate webhooks; use list()."


def _list_params(webhook_type: WebhookType | None) -> dict[str, str] | None:
    return None if webhook_type is None else {"type": str(webhook_type)}


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
