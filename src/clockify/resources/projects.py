from __future__ import annotations

from clockify.models.project import Project
from clockify.models.project import ProjectCreate
from clockify.models.project import ProjectUpdate
from clockify.resources.base import WorkspaceResource


class ProjectsResource(WorkspaceResource[Project, ProjectCreate, ProjectUpdate]):
    _path = "/projects"
    _read_model = Project
