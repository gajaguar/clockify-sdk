from __future__ import annotations

from typing import TYPE_CHECKING

from clockify.resources.approvals import ApprovalsResource
from clockify.resources.approvals import AsyncApprovalsResource
from clockify.resources.clients import AsyncClientsResource
from clockify.resources.clients import ClientsResource
from clockify.resources.custom_fields import AsyncCustomFieldsResource
from clockify.resources.custom_fields import CustomFieldsResource
from clockify.resources.expenses import AsyncExpenseCategoriesResource
from clockify.resources.expenses import AsyncExpensesResource
from clockify.resources.expenses import ExpenseCategoriesResource
from clockify.resources.expenses import ExpensesResource
from clockify.resources.invoices import AsyncInvoiceItemsResource
from clockify.resources.invoices import AsyncInvoicePaymentsResource
from clockify.resources.invoices import AsyncInvoicesResource
from clockify.resources.invoices import InvoiceItemsResource
from clockify.resources.invoices import InvoicePaymentsResource
from clockify.resources.invoices import InvoicesResource
from clockify.resources.projects import AsyncProjectsResource
from clockify.resources.projects import ProjectsResource
from clockify.resources.reports import AsyncReportsResource
from clockify.resources.reports import ReportsResource
from clockify.resources.tags import AsyncTagsResource
from clockify.resources.tags import TagsResource
from clockify.resources.tasks import AsyncTasksResource
from clockify.resources.tasks import TasksResource
from clockify.resources.time_entries import AsyncTimeEntriesResource
from clockify.resources.time_entries import TimeEntriesResource
from clockify.resources.time_off import AsyncTimeOffBalancesResource
from clockify.resources.time_off import AsyncTimeOffPoliciesResource
from clockify.resources.time_off import AsyncTimeOffRequestsResource
from clockify.resources.time_off import TimeOffBalancesResource
from clockify.resources.time_off import TimeOffPoliciesResource
from clockify.resources.time_off import TimeOffRequestsResource
from clockify.resources.user_groups import AsyncUserGroupsResource
from clockify.resources.user_groups import UserGroupsResource
from clockify.resources.users import AsyncUsersResource
from clockify.resources.users import UsersResource
from clockify.resources.webhooks import AsyncWebhooksResource
from clockify.resources.webhooks import WebhooksResource

if TYPE_CHECKING:
    from clockify._transport import AsyncTransport
    from clockify._transport import Transport
    from clockify.ids import WorkspaceId


class WorkspaceClient:
    def __init__(
        self,
        transport: Transport,
        workspace_id: WorkspaceId,
        *,
        page_size: int = 50,
        reports_transport: Transport | None = None,
    ) -> None:
        self.id = workspace_id
        self.users = UsersResource(transport, workspace_id, page_size=page_size)
        self.user_groups = UserGroupsResource(transport, workspace_id, page_size=page_size)
        self.projects = ProjectsResource(transport, workspace_id, page_size=page_size)
        self.tasks = TasksResource(transport, workspace_id, page_size=page_size)
        self.clients = ClientsResource(transport, workspace_id, page_size=page_size)
        self.tags = TagsResource(transport, workspace_id, page_size=page_size)
        self.custom_fields = CustomFieldsResource(transport, workspace_id, page_size=page_size)
        self.time_entries = TimeEntriesResource(transport, workspace_id, page_size=page_size)
        self.webhooks = WebhooksResource(transport, workspace_id, page_size=page_size)
        self.approvals = ApprovalsResource(transport, workspace_id, page_size=page_size)
        self.expenses = ExpensesResource(transport, workspace_id, page_size=page_size)
        self.expense_categories = ExpenseCategoriesResource(transport, workspace_id, page_size=page_size)
        self.invoices = InvoicesResource(transport, workspace_id, page_size=page_size)
        self.invoice_items = InvoiceItemsResource(transport, workspace_id, page_size=page_size)
        self.invoice_payments = InvoicePaymentsResource(transport, workspace_id, page_size=page_size)
        self.time_off_policies = TimeOffPoliciesResource(transport, workspace_id, page_size=page_size)
        self.time_off_requests = TimeOffRequestsResource(transport, workspace_id, page_size=page_size)
        self.time_off_balances = TimeOffBalancesResource(transport, workspace_id, page_size=page_size)
        # Reports live on a separate host; without a dedicated transport they fall back to
        # the core one, which keeps a hand-built WorkspaceClient working as before.
        self.reports = ReportsResource(reports_transport or transport, workspace_id)


class AsyncWorkspaceClient:
    def __init__(
        self,
        transport: AsyncTransport,
        workspace_id: WorkspaceId,
        *,
        page_size: int = 50,
        reports_transport: AsyncTransport | None = None,
    ) -> None:
        self.id = workspace_id
        self.users = AsyncUsersResource(transport, workspace_id, page_size=page_size)
        self.user_groups = AsyncUserGroupsResource(transport, workspace_id, page_size=page_size)
        self.projects = AsyncProjectsResource(transport, workspace_id, page_size=page_size)
        self.tasks = AsyncTasksResource(transport, workspace_id, page_size=page_size)
        self.clients = AsyncClientsResource(transport, workspace_id, page_size=page_size)
        self.tags = AsyncTagsResource(transport, workspace_id, page_size=page_size)
        self.custom_fields = AsyncCustomFieldsResource(transport, workspace_id, page_size=page_size)
        self.time_entries = AsyncTimeEntriesResource(transport, workspace_id, page_size=page_size)
        self.webhooks = AsyncWebhooksResource(transport, workspace_id, page_size=page_size)
        self.approvals = AsyncApprovalsResource(transport, workspace_id, page_size=page_size)
        self.expenses = AsyncExpensesResource(transport, workspace_id, page_size=page_size)
        self.expense_categories = AsyncExpenseCategoriesResource(transport, workspace_id, page_size=page_size)
        self.invoices = AsyncInvoicesResource(transport, workspace_id, page_size=page_size)
        self.invoice_items = AsyncInvoiceItemsResource(transport, workspace_id, page_size=page_size)
        self.invoice_payments = AsyncInvoicePaymentsResource(transport, workspace_id, page_size=page_size)
        self.time_off_policies = AsyncTimeOffPoliciesResource(transport, workspace_id, page_size=page_size)
        self.time_off_requests = AsyncTimeOffRequestsResource(transport, workspace_id, page_size=page_size)
        self.time_off_balances = AsyncTimeOffBalancesResource(transport, workspace_id, page_size=page_size)
        self.reports = AsyncReportsResource(reports_transport or transport, workspace_id)
