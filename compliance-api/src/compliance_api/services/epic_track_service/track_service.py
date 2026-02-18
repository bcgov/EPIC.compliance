"""Class to manage epictrack services."""

from datetime import date
import requests
from flask import current_app, g
from tenacity import RetryError, retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from compliance_api.exceptions import BadRequestError, ResourceNotFoundError, ServiceUnavailableError
from compliance_api.utils.enum import HttpMethod

from .constant import API_REQUEST_TIMEOUT


class TrackService:
    """EPIC.Track service class."""

    @staticmethod
    def get_project_by_id(project_id: int, as_of_date: date = None):
        """Return project details from track."""
        try:
            if as_of_date:
                project_response = _request_track_service(
                    f"projects/{project_id}?as_of_date={as_of_date.isoformat()}"
                )
            else:
                project_response = _request_track_service(f"projects/{project_id}")

            if project_response.status_code == 404:
                raise ResourceNotFoundError(
                    f"Project with ID {project_id} not found in EPIC.track"
                )

            if project_response.status_code != 200:
                current_app.logger.error(
                    f"EPIC.track returned status {project_response.status_code} for project {project_id}"
                )
                raise BadRequestError(
                    "Unable to retrieve project information at this time"
                )

            return project_response.json()

        except (RetryError, requests.exceptions.RequestException) as e:
            current_app.logger.error(
                f"EPIC.track service unavailable for project {project_id}: {str(e)}",
                exc_info=True
            )
            raise ServiceUnavailableError(
                "The project information service is temporarily unavailable. Please try again later."
            )
        except (ResourceNotFoundError, BadRequestError):
            # Re-raise custom exceptions
            raise
        except (KeyError, ValueError, TypeError) as e:
            current_app.logger.error(
                f"Error parsing project data for project {project_id}: {str(e)}",
                exc_info=True
            )
            raise BadRequestError(
                f"Unable to parse project information for project {project_id}"
            )

    @staticmethod
    def get_project_statuses():
        """Return the project statuses from track."""
        try:
            project_status_response = _request_track_service(
                "project-states?components=compliance"
            )

            if project_status_response.status_code != 200:
                current_app.logger.error(
                    f"EPIC.track returned status {project_status_response.status_code} for project statuses"
                )
                raise BadRequestError("Unable to retrieve project statuses")

            return project_status_response.json()

        except (RetryError, requests.exceptions.RequestException) as e:
            current_app.logger.error(
                f"EPIC.track service unavailable for project statuses: {str(e)}",
                exc_info=True
            )
            raise BadRequestError(
                "The project status service is temporarily unavailable. Please try again later."
            )
        except BadRequestError:
            raise
        except (KeyError, ValueError, TypeError) as e:
            current_app.logger.error(f"Error parsing project statuses: {str(e)}", exc_info=True)
            raise BadRequestError("Unable to parse project status information")

    @staticmethod
    def get_first_nation_by_id(first_nation_id: int):
        """Return firstnation by id."""
        try:
            first_nation_response = _request_track_service(
                f"indigenous-nations/{first_nation_id}"
            )

            if first_nation_response.status_code == 404:
                raise ResourceNotFoundError(
                    f"First Nation with ID {first_nation_id} not found in EPIC.track"
                )

            if first_nation_response.status_code != 200:
                current_app.logger.error(
                    f"EPIC.track returned status {first_nation_response.status_code} for first nation {first_nation_id}"
                )
                raise BadRequestError(
                    "Unable to retrieve First Nation information at this time"
                )

            return first_nation_response.json()

        except (RetryError, requests.exceptions.RequestException) as e:
            current_app.logger.error(
                f"EPIC.track service unavailable for first nation {first_nation_id}: {str(e)}",
                exc_info=True
            )
            raise BadRequestError(
                "The First Nation information service is temporarily unavailable. Please try again later."
            )
        except (ResourceNotFoundError, BadRequestError):
            raise
        except (KeyError, ValueError, TypeError) as e:
            current_app.logger.error(
                f"Error parsing first nation data for ID {first_nation_id}: {str(e)}",
                exc_info=True
            )
            raise BadRequestError(
                f"Unable to parse First Nation information for ID {first_nation_id}"
            )

    @staticmethod
    def get_first_nations():
        """Return firstnations."""
        try:
            first_nation_response = _request_track_service("indigenous-nations")
            if first_nation_response.status_code != 200:
                current_app.logger.error(
                    f"EPIC.track returned status {first_nation_response.status_code} for GET first nations."
                )
                raise BadRequestError(
                    "Unable to retrieve First Nation information at this time"
                )

            return first_nation_response.json()
        except (RetryError, requests.exceptions.RequestException) as e:
            current_app.logger.error(
                f"EPIC.track service unavailable for GET first nations: {str(e)}",
                exc_info=True
            )
            raise BadRequestError(
                "The First Nation information service is temporarily unavailable. Please try again later."
            )
        except (ResourceNotFoundError, BadRequestError):
            raise
        except (KeyError, ValueError, TypeError) as e:
            current_app.logger.error(
                f"Error parsing first nation data for GET first nations: {str(e)}",
                exc_info=True
            )
            raise BadRequestError(
                "Unable to parse First Nation information for GET first nations"
            )


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
