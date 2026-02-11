"""Service to call epic.authorize endpoints."""

import requests
from flask import current_app, g

from compliance_api.exceptions import BadRequestError, BusinessError, ResourceNotFoundError, ServiceUnavailableError
from compliance_api.utils.constant import AUTH_APP
from compliance_api.utils.enum import HttpMethod

from .constant import API_REQUEST_TIMEOUT


class AuthService:
    """Handle service request for epic.authorize."""

    @staticmethod
    def get_epic_user_by_guid(auth_user_guid: str):
        """Return the user representation from epic.authorize."""
        try:
            response = _request_auth_service(f"users/{auth_user_guid}")

            if response.status_code == 404:
                raise ResourceNotFoundError(
                    f"User with ID {auth_user_guid} not found in EPIC.auth"
                )

            if response.status_code != 200:
                current_app.logger.error(
                    f"EPIC.auth returned status {response.status_code} "
                    f"for user {auth_user_guid}"
                )
                raise BadRequestError(
                    "Unable to retrieve user information at this time"
                )

            return response.json()

        except requests.exceptions.RequestException as e:
            current_app.logger.error(
                f"EPIC.auth service unavailable for user {auth_user_guid}: {str(e)}",
                exc_info=True,
            )
            raise ServiceUnavailableError(
                "The user service is temporarily unavailable. Please try again later."
            )

        except (ResourceNotFoundError, BadRequestError):
            raise

        except (KeyError, ValueError, TypeError) as e:
            current_app.logger.error(
                f"Error parsing user data for {auth_user_guid}: {str(e)}",
                exc_info=True,
            )
            raise BadRequestError(
                f"Unable to parse user information for {auth_user_guid}"
            )

    @staticmethod
    def get_epic_users_by_app():
        """Return all users belonging to COMPLIANCE app."""
        try:
            response = _request_auth_service(f"users?app_name={AUTH_APP}")

            if response.status_code != 200:
                current_app.logger.error(
                    f"EPIC.auth returned status {response.status_code} for app users"
                )
                raise BadRequestError(
                    f"Unable to retrieve users for the app {AUTH_APP}"
                )

            return response.json()

        except requests.exceptions.RequestException as e:
            current_app.logger.error(
                f"EPIC.auth service unavailable for app users: {str(e)}",
                exc_info=True,
            )
            raise ServiceUnavailableError(
                "The user service is temporarily unavailable. Please try again later."
            )

        except BadRequestError:
            raise

        except (KeyError, ValueError, TypeError) as e:
            current_app.logger.error(
                f"Error parsing app users response: {str(e)}",
                exc_info=True,
            )
            raise BadRequestError("Unable to parse user information")

    @staticmethod
    def update_user_group(auth_user_guid: str, payload: dict):
        """Update the group of the user in the identity server."""
        try:
            response = _request_auth_service(
                f"users/{auth_user_guid}/groups",
                HttpMethod.PUT,
                payload,
            )

            if response.status_code != 204:
                current_app.logger.error(
                    f"EPIC.auth returned status {response.status_code} "
                    f"for updating user group {auth_user_guid}"
                )
                raise BadRequestError(
                    f"Update group failed for user {auth_user_guid}"
                )

            return response

        except requests.exceptions.RequestException as e:
            current_app.logger.error(
                f"EPIC.auth service unavailable while updating group "
                f"for {auth_user_guid}: {str(e)}",
                exc_info=True,
            )
            raise ServiceUnavailableError(
                "The user service is temporarily unavailable. Please try again later."
            )

    @staticmethod
    def delete_user_group(auth_user_guid: str, group: str, del_sub_group_mappings=True):
        """Delete user group."""
        try:
            response = _request_auth_service(
                f"users/{auth_user_guid}/groups/{group}"
                f"?del_sub_group_mappings={del_sub_group_mappings}",
                HttpMethod.DELETE,
            )

            if response.status_code != 204:
                current_app.logger.error(
                    f"EPIC.auth returned status {response.status_code} "
                    f"for deleting group {group} for user {auth_user_guid}"
                )
                raise BadRequestError("Delete group mapping failed")

            return response

        except requests.exceptions.RequestException as e:
            current_app.logger.error(
                f"EPIC.auth service unavailable while deleting group "
                f"for {auth_user_guid}: {str(e)}",
                exc_info=True,
            )
            raise ServiceUnavailableError(
                "The user service is temporarily unavailable. Please try again later."
            )


def _request_auth_service(
    relative_url, http_method: HttpMethod = HttpMethod.GET, data=None
):
    """REST Api call to authorize service."""
    token = getattr(g, "access_token", None)
    if not token:
        raise BusinessError("No access token found", 401)
    auth_base_url = current_app.config["AUTH_BASE_URL"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "App-Id": AUTH_APP,
    }

    url = f"{auth_base_url}/api/{relative_url}"

    try:
        if http_method == HttpMethod.GET:
            response = requests.get(url, headers=headers, timeout=API_REQUEST_TIMEOUT)
        elif http_method == HttpMethod.PUT:
            response = requests.put(
                url, headers=headers, json=data, timeout=API_REQUEST_TIMEOUT
            )
        elif http_method == HttpMethod.PATCH:
            response = requests.patch(
                url, headers=headers, json=data, timeout=API_REQUEST_TIMEOUT
            )
        elif http_method == HttpMethod.DELETE:
            response = requests.delete(url, headers=headers, timeout=API_REQUEST_TIMEOUT)
        else:
            raise ValueError("Invalid HTTP method")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Error making request to EPIC.track server: {str(e)}"
        ) from e
    return response
