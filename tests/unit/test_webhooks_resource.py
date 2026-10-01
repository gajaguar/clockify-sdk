from __future__ import annotations

import json
from typing import Final

import pytest
import respx
from httpx import Response

from clockify import NO_RETRY
from clockify import AsyncClockifyClient
from clockify import ClientOptions
from clockify import ClockifyClient
from clockify import CqsKind
from clockify import Webhook
from clockify import WebhookCreate
from clockify import WebhookEvent
from clockify import WebhookTriggerSourceType
from clockify import WebhookType
from clockify import WebhookUpdate
from clockify.ids import WorkspaceId

BASE_URL: Final = "https://fake.clockify.test/api/v1"
WORKSPACE_ID: Final = WorkspaceId("64a1f0000000000000000001")
WEBHOOKS_URL: Final = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/webhooks"
WEBHOOK_ID: Final = "6973710805e44c5a46763239"
DELIVERY_SIGNATURE: Final = "secret-token-value"

WEBHOOK_PAYLOAD: Final = {
    "id": WEBHOOK_ID,
    "name": "on-new-project",
    "url": "https://example.test/hook",
    "userId": "5a0ab5acb07987125438b60f",
    "workspaceId": str(WORKSPACE_ID),
    "webhookEvent": "NEW_PROJECT",
    "triggerSource": [str(WORKSPACE_ID)],
    "triggerSourceType": "WORKSPACE_ID",
    "enabled": True,
    "authToken": DELIVERY_SIGNATURE,
}
LIST_PAYLOAD: Final = {"webhooks": [WEBHOOK_PAYLOAD], "workspaceWebhookCount": 1}
CREATE: Final = WebhookCreate(
    url="https://example.test/hook",
    webhook_event=WebhookEvent.NEW_PROJECT,
    trigger_source=[str(WORKSPACE_ID)],
    trigger_source_type=WebhookTriggerSourceType.WORKSPACE_ID,
    name="on-new-project",
)
UPDATE: Final = WebhookUpdate(
    url="https://example.test/hook",
    webhook_event=WebhookEvent.NEW_PROJECT,
    trigger_source=[str(WORKSPACE_ID)],
    trigger_source_type=WebhookTriggerSourceType.WORKSPACE_ID,
)


def _client() -> ClockifyClient:
    return ClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


def _async_client() -> AsyncClockifyClient:
    return AsyncClockifyClient(api_key="dummy", options=ClientOptions(base_url=BASE_URL, retry=NO_RETRY))


@respx.mock
def test_list_makes_one_request_without_query_and_unwraps_the_envelope() -> None:
    # Arrange
    route = respx.get(WEBHOOKS_URL).mock(return_value=Response(200, json=LIST_PAYLOAD))
    client = _client()
    # Act
    webhooks = list(client.workspace(WORKSPACE_ID).webhooks.list())
    # Assert
    assert route.call_count == 1
    assert not route.calls[0].request.url.params
    assert [webhook.id for webhook in webhooks] == [WEBHOOK_ID]
    assert webhooks[0].webhook_event is WebhookEvent.NEW_PROJECT
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.QUERY
    client.close()


@respx.mock
def test_list_filters_by_type() -> None:
    # Arrange
    route = respx.get(WEBHOOKS_URL).mock(return_value=Response(200, json=LIST_PAYLOAD))
    client = _client()
    # Act
    list(client.workspace(WORKSPACE_ID).webhooks.list(webhook_type=WebhookType.ADDON))
    # Assert
    assert route.calls[0].request.url.params["type"] == "ADDON"
    client.close()


def test_list_page_is_not_supported_because_clockify_does_not_paginate() -> None:
    # Arrange
    client = _client()
    # Act
    # Assert
    with pytest.raises(NotImplementedError):
        client.workspace(WORKSPACE_ID).webhooks.list_page()
    client.close()


@respx.mock
def test_get_returns_the_webhook() -> None:
    # Arrange
    route = respx.get(f"{WEBHOOKS_URL}/{WEBHOOK_ID}").mock(return_value=Response(200, json=WEBHOOK_PAYLOAD))
    client = _client()
    # Act
    webhook = client.workspace(WORKSPACE_ID).webhooks.get(WEBHOOK_ID)
    # Assert
    assert route.call_count == 1
    assert webhook.auth_token == DELIVERY_SIGNATURE
    client.close()


@respx.mock
def test_create_posts_camel_case_body_and_declares_non_idempotent_command() -> None:
    # Arrange
    route = respx.post(WEBHOOKS_URL).mock(return_value=Response(201, json=WEBHOOK_PAYLOAD))
    client = _client()
    # Act
    webhook = client.workspace(WORKSPACE_ID).webhooks.create(CREATE)
    # Assert
    assert route.call_count == 1
    assert json.loads(respx.calls[0].request.content) == {
        "url": "https://example.test/hook",
        "webhookEvent": "NEW_PROJECT",
        "triggerSource": [str(WORKSPACE_ID)],
        "triggerSourceType": "WORKSPACE_ID",
        "name": "on-new-project",
    }
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert webhook.id == WEBHOOK_ID
    client.close()


@respx.mock
def test_update_puts_and_declares_idempotent_command() -> None:
    # Arrange
    route = respx.put(f"{WEBHOOKS_URL}/{WEBHOOK_ID}").mock(return_value=Response(200, json=WEBHOOK_PAYLOAD))
    client = _client()
    # Act
    webhook = client.workspace(WORKSPACE_ID).webhooks.update(WEBHOOK_ID, UPDATE)
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    assert webhook.id == WEBHOOK_ID
    client.close()


@respx.mock
def test_delete_declares_idempotent_command() -> None:
    # Arrange
    route = respx.delete(f"{WEBHOOKS_URL}/{WEBHOOK_ID}").mock(return_value=Response(200))
    client = _client()
    # Act
    client.workspace(WORKSPACE_ID).webhooks.delete(WEBHOOK_ID)
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.IDEMPOTENT_COMMAND
    client.close()


@respx.mock
def test_regenerate_token_patches_and_declares_non_idempotent_command() -> None:
    # Arrange
    route = respx.patch(f"{WEBHOOKS_URL}/{WEBHOOK_ID}/token").mock(return_value=Response(200, json=WEBHOOK_PAYLOAD))
    client = _client()
    # Act
    webhook = client.workspace(WORKSPACE_ID).webhooks.regenerate_token(WEBHOOK_ID)
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert webhook.auth_token == DELIVERY_SIGNATURE
    client.close()


def test_unknown_event_falls_back_to_unknown() -> None:
    # Arrange
    payload = {**WEBHOOK_PAYLOAD, "webhookEvent": "SOME_FUTURE_EVENT"}
    # Act
    webhook = Webhook.model_validate(payload)
    # Assert
    assert webhook.webhook_event is WebhookEvent.UNKNOWN


@respx.mock
def test_repr_does_not_leak_the_auth_token() -> None:
    # Arrange
    respx.get(f"{WEBHOOKS_URL}/{WEBHOOK_ID}").mock(return_value=Response(200, json=WEBHOOK_PAYLOAD))
    client = _client()
    # Act
    webhook = client.workspace(WORKSPACE_ID).webhooks.get(WEBHOOK_ID)
    # Assert
    assert DELIVERY_SIGNATURE not in repr(webhook)
    assert DELIVERY_SIGNATURE not in str(webhook)
    client.close()


@respx.mock
async def test_async_list_unwraps_the_envelope_and_filters_by_type() -> None:
    # Arrange
    route = respx.get(WEBHOOKS_URL).mock(return_value=Response(200, json=LIST_PAYLOAD))
    client = _async_client()
    # Act
    webhooks = [w async for w in client.workspace(WORKSPACE_ID).webhooks.list(webhook_type=WebhookType.SYSTEM)]
    # Assert
    assert route.call_count == 1
    assert route.calls[0].request.url.params["type"] == "SYSTEM"
    assert [webhook.id for webhook in webhooks] == [WEBHOOK_ID]
    await client.aclose()


async def test_async_list_page_is_not_supported() -> None:
    # Arrange
    client = _async_client()
    # Act
    # Assert
    with pytest.raises(NotImplementedError):
        await client.workspace(WORKSPACE_ID).webhooks.list_page()
    await client.aclose()


@respx.mock
async def test_async_create_posts_and_declares_non_idempotent_command() -> None:
    # Arrange
    respx.post(WEBHOOKS_URL).mock(return_value=Response(201, json=WEBHOOK_PAYLOAD))
    client = _async_client()
    # Act
    webhook = await client.workspace(WORKSPACE_ID).webhooks.create(CREATE)
    # Assert
    assert json.loads(respx.calls[0].request.content)["webhookEvent"] == "NEW_PROJECT"
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert webhook.id == WEBHOOK_ID
    await client.aclose()


@respx.mock
async def test_async_regenerate_token_patches_and_declares_non_idempotent_command() -> None:
    # Arrange
    route = respx.patch(f"{WEBHOOKS_URL}/{WEBHOOK_ID}/token").mock(return_value=Response(200, json=WEBHOOK_PAYLOAD))
    client = _async_client()
    # Act
    webhook = await client.workspace(WORKSPACE_ID).webhooks.regenerate_token(WEBHOOK_ID)
    # Assert
    assert route.call_count == 1
    assert respx.calls[0].request.extensions.get("clockify_cqs") == CqsKind.NON_IDEMPOTENT_COMMAND
    assert webhook.auth_token == DELIVERY_SIGNATURE
    await client.aclose()
