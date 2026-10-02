from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from clockify._time import ClockifyInstant
from clockify.ids import WebhookId
from clockify.ids import WorkspaceId
from clockify.models.base import ClockifyModel


class WebhookEvent(StrEnum):
    NEW_PROJECT = "NEW_PROJECT"
    NEW_TASK = "NEW_TASK"
    NEW_CLIENT = "NEW_CLIENT"
    NEW_TIMER_STARTED = "NEW_TIMER_STARTED"
    TIMER_STOPPED = "TIMER_STOPPED"
    TIME_ENTRY_UPDATED = "TIME_ENTRY_UPDATED"
    TIME_ENTRY_DELETED = "TIME_ENTRY_DELETED"
    TIME_ENTRY_SPLIT = "TIME_ENTRY_SPLIT"
    NEW_TIME_ENTRY = "NEW_TIME_ENTRY"
    TIME_ENTRY_RESTORED = "TIME_ENTRY_RESTORED"
    NEW_TAG = "NEW_TAG"
    USER_DELETED_FROM_WORKSPACE = "USER_DELETED_FROM_WORKSPACE"
    USER_JOINED_WORKSPACE = "USER_JOINED_WORKSPACE"
    USER_DEACTIVATED_ON_WORKSPACE = "USER_DEACTIVATED_ON_WORKSPACE"
    USER_ACTIVATED_ON_WORKSPACE = "USER_ACTIVATED_ON_WORKSPACE"
    USER_EMAIL_CHANGED = "USER_EMAIL_CHANGED"
    USER_UPDATED = "USER_UPDATED"
    NEW_INVOICE = "NEW_INVOICE"
    INVOICE_UPDATED = "INVOICE_UPDATED"
    NEW_APPROVAL_REQUEST = "NEW_APPROVAL_REQUEST"
    APPROVAL_REQUEST_STATUS_UPDATED = "APPROVAL_REQUEST_STATUS_UPDATED"
    TIME_OFF_REQUESTED = "TIME_OFF_REQUESTED"
    TIME_OFF_REQUEST_UPDATED = "TIME_OFF_REQUEST_UPDATED"
    TIME_OFF_REQUEST_APPROVED = "TIME_OFF_REQUEST_APPROVED"
    TIME_OFF_REQUEST_REJECTED = "TIME_OFF_REQUEST_REJECTED"
    TIME_OFF_REQUEST_STARTED = "TIME_OFF_REQUEST_STARTED"
    TIME_OFF_REQUEST_WITHDRAWN = "TIME_OFF_REQUEST_WITHDRAWN"
    BALANCE_UPDATED = "BALANCE_UPDATED"
    TAG_UPDATED = "TAG_UPDATED"
    TAG_DELETED = "TAG_DELETED"
    TASK_UPDATED = "TASK_UPDATED"
    CLIENT_UPDATED = "CLIENT_UPDATED"
    TASK_DELETED = "TASK_DELETED"
    CLIENT_DELETED = "CLIENT_DELETED"
    EXPENSE_RESTORED = "EXPENSE_RESTORED"
    ASSIGNMENT_CREATED = "ASSIGNMENT_CREATED"
    ASSIGNMENT_DELETED = "ASSIGNMENT_DELETED"
    ASSIGNMENT_PUBLISHED = "ASSIGNMENT_PUBLISHED"
    ASSIGNMENT_UPDATED = "ASSIGNMENT_UPDATED"
    EXPENSE_CREATED = "EXPENSE_CREATED"
    EXPENSE_DELETED = "EXPENSE_DELETED"
    EXPENSE_UPDATED = "EXPENSE_UPDATED"
    PROJECT_UPDATED = "PROJECT_UPDATED"
    PROJECT_DELETED = "PROJECT_DELETED"
    USER_GROUP_CREATED = "USER_GROUP_CREATED"
    USER_GROUP_UPDATED = "USER_GROUP_UPDATED"
    USER_GROUP_DELETED = "USER_GROUP_DELETED"
    USERS_INVITED_TO_WORKSPACE = "USERS_INVITED_TO_WORKSPACE"
    LIMITED_USERS_ADDED_TO_WORKSPACE = "LIMITED_USERS_ADDED_TO_WORKSPACE"
    COST_RATE_UPDATED = "COST_RATE_UPDATED"
    BILLABLE_RATE_UPDATED = "BILLABLE_RATE_UPDATED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> WebhookEvent:
        del value
        return cls.UNKNOWN


class WebhookTriggerSourceType(StrEnum):
    PROJECT_ID = "PROJECT_ID"
    USER_ID = "USER_ID"
    TAG_ID = "TAG_ID"
    TASK_ID = "TASK_ID"
    WORKSPACE_ID = "WORKSPACE_ID"
    ASSIGNMENT_ID = "ASSIGNMENT_ID"
    EXPENSE_ID = "EXPENSE_ID"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> WebhookTriggerSourceType:
        del value
        return cls.UNKNOWN


class WebhookType(StrEnum):
    USER_CREATED = "USER_CREATED"
    SYSTEM = "SYSTEM"
    ADDON = "ADDON"


class Webhook(ClockifyModel):
    id: WebhookId
    name: str | None = None
    url: str
    user_id: str | None = None
    workspace_id: WorkspaceId | None = None
    webhook_event: WebhookEvent
    trigger_source: list[str]
    trigger_source_type: WebhookTriggerSourceType
    enabled: bool | None = None
    delivery_enabled: bool | None = None
    plan_enabled: bool | None = None
    # repr=False: the token is the secret that proves a delivery came from Clockify, so
    # it must not reach a traceback or a log line that captures this model.
    auth_token: str | None = Field(default=None, repr=False)


class WebhookList(ClockifyModel):
    webhooks: list[Webhook]
    workspace_webhook_count: int | None = None


class WebhookCreate(ClockifyModel):
    url: str
    webhook_event: WebhookEvent
    trigger_source: list[str]
    trigger_source_type: WebhookTriggerSourceType
    name: str | None = None


class WebhookUpdate(ClockifyModel):
    url: str
    webhook_event: WebhookEvent
    trigger_source: list[str]
    trigger_source_type: WebhookTriggerSourceType
    name: str | None = None


class WebhookDeliveryStatus(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    RETRYING = "RETRYING"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> WebhookDeliveryStatus:
        del value
        return cls.UNKNOWN


class WebhookLogStatus(StrEnum):
    ALL = "ALL"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


# None of the delivery-log models has been checked against a real response: webhooks
# answer 403 on the Free plan the SDK was built on. They follow the OpenAPI spec, with
# every field optional.
class WebhookLog(ClockifyModel):
    id: str | None = None
    webhook_id: WebhookId | None = None
    webhook_event_status_id: str | None = None
    status_code: int | None = None
    request_body: str | None = None
    response_body: str | None = None
    responded_at: str | None = None


class WebhookEventStatus(ClockifyModel):
    id: str | None = None
    webhook_id: WebhookId | None = None
    webhook_log_id: str | None = None
    status: WebhookDeliveryStatus | None = None
    status_code: int | None = None
    retry_count: int | None = None
    request_body: str | None = None
    response_body: str | None = None
    responded_at: str | None = None


class WebhookLogSearch(ClockifyModel):
    # `from` is a Python keyword, so the field is `start` and only the wire name differs.
    start: ClockifyInstant | None = Field(default=None, alias="from")
    to: ClockifyInstant | None = None
    status: WebhookLogStatus | None = None
    sort_by_newest: bool | None = None
