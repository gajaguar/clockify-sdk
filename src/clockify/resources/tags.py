from __future__ import annotations

from clockify.models.tag import Tag
from clockify.models.tag import TagCreate
from clockify.models.tag import TagUpdate
from clockify.resources.base import WorkspaceResource


class TagsResource(WorkspaceResource[Tag, TagCreate, TagUpdate]):
    _path = "/tags"
    _read_model = Tag
