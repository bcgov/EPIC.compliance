"""Class to manage document service."""

import requests
from flask import current_app, g
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from compliance_api.exceptions import BusinessError
from compliance_api.utils.enum import HttpMethod

from .constant import API_REQUEST_TIMEOUT


class DocService:
    """Doc service."""

    @staticmethod
    def get_presigned_url(payload: dict, params: dict = None) -> dict:
        """Get presigned url for the given action on the given file."""
        response = _request_doc_service(
            "storage-operations/presigned-urls", HttpMethod.POST, payload, params
        )
        if response.status_code != 200:
            raise BusinessError("Error contacting the document service")
        return response.json()


@retry(
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    stop=stop_after_attempt(3),  # Retry up to 3 times
    wait=wait_fixed(2),  # Wait 2 seconds between retries
)
def _request_doc_service(
    relative_url, http_method: HttpMethod = HttpMethod.GET, data=None, params=None
):
    """REST Api call to doc service."""
    token = getattr(g, "access_token", None)
    if not token:
        raise BusinessError("No access token found", 401)
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
