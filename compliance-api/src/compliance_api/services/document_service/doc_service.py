"""Class to manage document service."""

import requests
from flask import current_app, g
from tenacity import RetryError, retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from compliance_api.exceptions import BadRequestError, PermissionDeniedError, ServiceUnavailableError
from compliance_api.utils.enum import HttpMethod

from .constant import API_REQUEST_TIMEOUT


class DocService:
    """Doc service."""

    @staticmethod
    def get_presigned_url(payload: dict, params: dict = None) -> dict:
        """Get presigned url for the given action on the given file."""
        try:
            response = _request_doc_service(
                "storage-operations/presigned-urls", HttpMethod.POST, payload, params
            )

            if response.status_code == 400:
                current_app.logger.error(f"Invalid request to document service: {response.text}")
                raise BadRequestError("Invalid document request")

            if response.status_code == 403:
                raise PermissionDeniedError("You do not have permission to access this document")

            if response.status_code == 404:
                raise BadRequestError("Document not found")

            if response.status_code != 200:
                current_app.logger.error(
                    f"Document service returned status {response.status_code}: {response.text}"
                )
                raise BadRequestError("Unable to generate document URL at this time")

            return response.json()

        except (RetryError, requests.exceptions.RequestException) as e:
            current_app.logger.error(
                f"Document service unavailable: {str(e)}",
                exc_info=True
            )
            raise ServiceUnavailableError(
                "The document service is temporarily unavailable. Please try again later."
            )
        except (PermissionDeniedError, BadRequestError):
            # Re-raise our custom exceptions
            raise
        except (KeyError, ValueError, TypeError) as e:
            current_app.logger.error(
                f"Error parsing document service response: {str(e)}",
                exc_info=True
            )
            raise BadRequestError("Unable to process document service response")


@retry(
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    stop=stop_after_attempt(3),  # Retry up to 3 times
    wait=wait_fixed(2),  # Wait 2 seconds between retries
)
def _request_doc_service(
    relative_url, http_method: HttpMethod = HttpMethod.GET, data=None, params=None
):
    """REST Api call to doc service."""
    try:
        token = getattr(g, "access_token", None)
        if not token:
            raise PermissionDeniedError("No access token found")

        auth_base_url = current_app.config["DOC_SERVICE_URL"]
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        url = f"{auth_base_url}/api/{relative_url}"

        if http_method == HttpMethod.GET:
            response = requests.get(url, headers=headers, timeout=60)
        elif http_method == HttpMethod.POST:
            response = requests.post(
                url=url, headers=headers, json=data, timeout=API_REQUEST_TIMEOUT, params=params
            )
        else:
            raise ValueError("Invalid HTTP method")

        response.raise_for_status()
        return response

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Error making request to document service: {str(e)}"
        ) from e
