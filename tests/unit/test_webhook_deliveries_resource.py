from __future__ import annotations

import json
from typing import Final

import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import AsyncClockifyClient
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import CqsKind
from clockify import Webhook
from clockify import WebhookDeliveryStatus
from clockify import WebhookEvent
from clockify import WebhookEventStatus
from clockify import WebhookLog
from clockify import WebhookLogSearch
from clockify import WebhookLogStatus
from clockify import WebhookTriggerSourceType
from clockify._auth import ApiKeyAuth  # ruff: ignore[import-private-name]
from clockify._transport import AsyncTransport  # ruff: ignore[import-private-name]
from clockify._transport import Transport  # ruff: ignore[import-private-name]
from clockify.config import ClientConfig
from clockify.ids import WorkspaceId
from clockify.resources.webhooks import AsyncWebhooksResource
from clockify.resources.webhooks import WebhooksResource

BASE_URL: Final = "https://fake.clockify.test/api/v1"
WORKSPACE_ID: Final = WorkspaceId("64a1f0000000000000000001")
WEBHOOK_ID: Final = "6973710805e44c5a46763239"
ADDON_ID: Final = "69737108aaaaaaaaaaaaaaaa"
WEBHOOK_URL: Final = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/webhooks/{WEBHOOK_ID}"
ADDON_URL: Final = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/addons/{ADDON_ID}/webhooks"

LOG_PAYLOAD: Final = {
    "id": "log-1",
    "webhookId": WEBHOOK_ID,
    "webhookEventStatusId": "status-1",
    "statusCode": 200,
    "requestBody": "{}",
    "responseBody": "ok",
    "respondedAt": "2026-01-02T03:04:05Z",
}
LOG: Final = WebhookLog(
    id="log-1",
    webhook_id=WEBHOOK_ID,
    webhook_event_status_id="status-1",
    status_code=200,
    request_body="{}",
    response_body="ok",
    responded_at="2026-01-02T03:04:05Z",
)
STATUS_PAYLOAD: Final = {
    "id": "status-1",
    "webhookId": WEBHOOK_ID,
    "webhookLogId": "log-1",
    "status": "FAILED",
    "statusCode": 500,
    "retryCount": 3,
    "requestBody": "{}",
    "responseBody": "boom",
    "respondedAt": "2026-01-02T03:04:05Z",
}
STATUS: Final = WebhookEventStatus(
    id="status-1",
    webhook_id=WEBHOOK_ID,
    webhook_log_id="log-1",
    status=WebhookDeliveryStatus.FAILED,
    status_code=500,
    retry_count=3,
    request_body="{}",
    response_body="boom",
    responded_at="2026-01-02T03:04:05Z",
)
WEBHOOK_PAYLOAD: Final = {
    "id": WEBHOOK_ID,
    "url": "https://example.test/hook",
    "webhookEvent": "NEW_PROJECT",
    "triggerSource": [str(WORKSPACE_ID)],
    "triggerSourceType": "WORKSPACE_ID",
}
WEBHOOK: Final = Webhook(
    id=WEBHOOK_ID,
    url="https://example.test/hook",
    webhook_event=WebhookEvent.NEW_PROJECT,
    trigger_source=[str(WORKSPACE_ID)],
    trigger_source_type=WebhookTriggerSourceType.WORKSPACE_ID,
)
SEARCH: Final = WebhookLogSearch(
    start="2026-01-01T00:00:00Z", to="2026-02-01T00:00:00Z", status=WebhookLogStatus.FAILED, sort_by_newest=True
)
SEARCH_BODY: Final = {
    "from": "2026-01-01T00:00:00Z",
    "to": "2026-02-01T00:00:00Z",
    "status": "FAILED",
    "sortByNewest": True,
}


def _client() -> ClockifyClient:
    return ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


def _async_client() -> AsyncClockifyClient:
    return AsyncClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


@respx.mock
def test_logs_page_posts_the_search_with_size_param_and_declares_query() -> None:
    # Arrange
    route = respx.post(f"{WEBHOOK_URL}/logs").mock(return_value=Response(200, json=[LOG_PAYLOAD]))
    client = _client()
    # Act
    page = client.workspace(WORKSPACE_ID).webhooks.logs_page(WEBHOOK_ID, search=SEARCH, page=2, page_size=10)
    # Assert
    assert route.call_count == 1
    assert route.calls[0].request.url.params.multi_items() == [("page", "2"), ("size", "10")]
    assert json.loads(route.calls[0].request.content) == SEARCH_BODY
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    assert page.items == [LOG]
    assert (page.page, page.page_size) == (2, 10)
    client.close()


@respx.mock
def test_logs_without_a_search_posts_an_empty_object_and_auto_paginates() -> None:
    # Arrange
    route = respx.post(f"{WEBHOOK_URL}/logs").mock(
        side_effect=[Response(200, json=[LOG_PAYLOAD, LOG_PAYLOAD]), Response(200, json=[LOG_PAYLOAD])]
    )
    config = ClientConfig(api_key="dummy", base_url=BASE_URL, reports_base_url=BASE_URL, retry=NO_RETRY)
    transport = Transport(config, BASE_URL, ApiKeyAuth("dummy"))
    # Act
    logs = list(WebhooksResource(transport, WORKSPACE_ID, page_size=2).logs(WEBHOOK_ID))
    # Assert
    assert logs == [LOG, LOG, LOG]
    assert [call.request.url.params["page"] for call in route.calls] == ["1", "2"]
    assert json.loads(route.calls[0].request.content) == {}
    transport.close()


@respx.mock
def test_statuses_page_sends_the_status_filter_and_size_param() -> None:
    # Arrange
    route = respx.get(f"{WEBHOOK_URL}/statuses").mock(return_value=Response(200, json=[STATUS_PAYLOAD]))
    client = _client()
    # Act
    page = client.workspace(WORKSPACE_ID).webhooks.statuses_page(
        WEBHOOK_ID, status=WebhookDeliveryStatus.FAILED, page_size=5
    )
    # Assert
    assert route.calls[0].request.url.params.multi_items() == [("page", "1"), ("size", "5"), ("statuses", "FAILED")]
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    assert page.items == [STATUS]
    client.close()


@respx.mock
def test_statuses_without_a_filter_sends_only_the_page() -> None:
    # Arrange
    route = respx.get(f"{WEBHOOK_URL}/statuses").mock(return_value=Response(200, json=[STATUS_PAYLOAD]))
    client = _client()
    # Act
    statuses = list(client.workspace(WORKSPACE_ID).webhooks.statuses(WEBHOOK_ID))
    # Assert
    assert route.calls[0].request.url.params.multi_items() == [("page", "1"), ("size", "200")]
    assert statuses == [STATUS]
    client.close()


def test_an_unknown_delivery_status_falls_back_to_unknown() -> None:
    # Arrange
    # Act
    status = WebhookEventStatus.model_validate({"status": "SOMETHING_NEW"})
    # Assert
    assert status.status is WebhookDeliveryStatus.UNKNOWN


@respx.mock
def test_list_for_addon_makes_one_request_and_unwraps_the_envelope() -> None:
    # Arrange
    route = respx.get(ADDON_URL).mock(
        return_value=Response(200, json={"webhooks": [WEBHOOK_PAYLOAD], "workspaceWebhookCount": 1})
    )
    client = _client()
    # Act
    webhooks = list(client.workspace(WORKSPACE_ID).webhooks.list_for_addon(ADDON_ID))
    # Assert
    assert route.call_count == 1
    assert not route.calls[0].request.url.params
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    assert webhooks == [WEBHOOK]
    client.close()


@respx.mock
async def test_async_logs_page_posts_the_search_with_size_param() -> None:
    # Arrange
    route = respx.post(f"{WEBHOOK_URL}/logs").mock(return_value=Response(200, json=[LOG_PAYLOAD]))
    client = _async_client()
    # Act
    page = await client.workspace(WORKSPACE_ID).webhooks.logs_page(WEBHOOK_ID, search=SEARCH, page_size=10)
    # Assert
    assert route.calls[0].request.url.params.multi_items() == [("page", "1"), ("size", "10")]
    assert json.loads(route.calls[0].request.content) == SEARCH_BODY
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    assert page.items == [LOG]
    await client.aclose()


@respx.mock
async def test_async_statuses_auto_paginates_with_the_filter() -> None:
    # Arrange
    route = respx.get(f"{WEBHOOK_URL}/statuses").mock(return_value=Response(200, json=[STATUS_PAYLOAD]))
    client = _async_client()
    # Act
    statuses = [
        status
        async for status in client.workspace(WORKSPACE_ID).webhooks.statuses(
            WEBHOOK_ID, status=WebhookDeliveryStatus.RETRYING
        )
    ]
    # Assert
    assert route.calls[0].request.url.params.multi_items() == [
        ("page", "1"),
        ("size", "200"),
        ("statuses", "RETRYING"),
    ]
    assert statuses == [STATUS]
    await client.aclose()


@respx.mock
async def test_async_list_for_addon_makes_one_request() -> None:
    # Arrange
    route = respx.get(ADDON_URL).mock(
        return_value=Response(200, json={"webhooks": [WEBHOOK_PAYLOAD], "workspaceWebhookCount": 1})
    )
    client = _async_client()
    # Act
    webhooks = [webhook async for webhook in client.workspace(WORKSPACE_ID).webhooks.list_for_addon(ADDON_ID)]
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    assert webhooks == [WEBHOOK]
    await client.aclose()


@respx.mock
async def test_async_logs_auto_paginates() -> None:
    # Arrange
    route = respx.post(f"{WEBHOOK_URL}/logs").mock(
        side_effect=[Response(200, json=[LOG_PAYLOAD, LOG_PAYLOAD]), Response(200, json=[LOG_PAYLOAD])]
    )
    config = ClientConfig(api_key="dummy", base_url=BASE_URL, reports_base_url=BASE_URL, retry=NO_RETRY)
    transport = AsyncTransport(config, BASE_URL, ApiKeyAuth("dummy"))
    # Act
    logs = [log async for log in AsyncWebhooksResource(transport, WORKSPACE_ID, page_size=2).logs(WEBHOOK_ID)]
    # Assert
    assert logs == [LOG, LOG, LOG]
    assert [call.request.url.params["page"] for call in route.calls] == ["1", "2"]
    await transport.aclose()
