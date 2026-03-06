"""Service for project resource management."""

from compliance_api.models import Project as ProjectModel
from compliance_api.services.epic_track_service.track_service import TrackService


class ProjectService:
    """Project management service."""

    @classmethod
    def get_project_by_id(cls, project_id):
        """Get project by id."""
        project = ProjectModel.find_by_id(project_id)
        return project

    @classmethod
    def get_all_projects(cls):
        """Get all projects."""
        projects = ProjectModel.get_all(default_filters=False)
        return projects

    @classmethod
    def get_project_abbreviation_by_id(cls, project_id):
        """Get project abbreviation by id."""
        project = TrackService.get_project_by_id(project_id)
        return project.get("abbreviation", None)
