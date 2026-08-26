from __future__ import annotations

from typing import override

from clockify.models.custom_field import CustomField
from clockify.models.custom_field import CustomFieldCreate
from clockify.models.custom_field import CustomFieldUpdate
from clockify.resources.base import WorkspaceResource


class CustomFieldsResource(WorkspaceResource[CustomField, CustomFieldCreate, CustomFieldUpdate]):
    _path = "/custom-fields"
    _read_model = CustomField

    # Clockify has no GET .../custom-fields/{id}; only list/create/update/delete exist.
    @override
    def get(self, item_id: str) -> CustomField:
        del item_id
        message = "Clockify has no GET .../custom-fields/{id} endpoint; filter list() instead."
        raise NotImplementedError(message)
