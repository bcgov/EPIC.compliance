"""Class to manage epictrack services."""

import requests
from flask import current_app, g
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from compliance_api.exceptions import BusinessError
from compliance_api.utils.enum import HttpMethod

from .constant import API_REQUEST_TIMEOUT


class TrackService:
    """EPIC.Track service class."""

    @staticmethod
    def get_project_by_id(project_id: int):
        """Return project details from track."""
        project_response = _request_track_service(f"projects/{project_id}")
        if project_response.status_code != 200:
            raise BusinessError(
                f"Error finding project with ID {project_id} from EPIC.track server"
            )
        return project_response.json()

    @staticmethod
    def get_projects():
        """Return projects from track."""
        project_response = _request_track_service("projects")
        if project_response.status_code != 200:
            raise BusinessError("Error finding projects")
        return project_response.json()

    @staticmethod
    def get_project_statuses():
        """Return the project statuses from track."""
        project_status_response = _request_track_service(
            "project-states?components=compliance"
        )
        if project_status_response.status_code != 200:
            raise BusinessError("Error finding project statuses")
        return project_status_response.json()

    @staticmethod
    def get_first_nation_by_id(first_nation_id: int):
        """Return firstnation by id."""
        first_nation_response = _request_track_service(
            f"indigenous-nations/{first_nation_id}"
        )
        if first_nation_response.status_code != 200:
            raise BusinessError(
                f"Error finding the first nation with ID {first_nation_id} from EPIC.track server"
            )
        return first_nation_response.json()


@retry(
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    stop=stop_after_attempt(3),  # Retry up to 3 times
    wait=wait_fixed(2),  # Wait 2 seconds between retries
)
def _request_track_service(
    relative_url, http_method: HttpMethod = HttpMethod.GET, data=None
):
    """REST Api call to track service."""
    try:
        token = getattr(g, "access_token", None)
        auth_base_url = current_app.config["EPIC_TRACK_URL"]
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        url = f"{auth_base_url}/api/v1/{relative_url}"

        if http_method == HttpMethod.GET:
            response = requests.get(url, headers=headers, timeout=API_REQUEST_TIMEOUT)
        else:
            raise ValueError("Invalid HTTP method")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Error making request to EPIC.track server: {str(e)}"
        ) from e
    return response
