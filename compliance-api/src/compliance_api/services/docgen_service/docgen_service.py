"""Service for generating documents."""
import json
import requests
from flask import current_app, g
from tenacity import RetryError, retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from compliance_api.exceptions import (
    BadRequestError, PermissionDeniedError, ResourceNotFoundError, ServiceUnavailableError)
from compliance_api.utils.constant import AUTH_APP
from compliance_api.utils.enum import HttpMethod


class DocGenService:
    """Service for generating documents."""

    @staticmethod
    def render_template(
        template_key: str, context: dict, output_type: str = "html"
    ) -> str:
        """Render a template with the given context."""
        try:
            if not template_key:
                raise BadRequestError("Template key is required")

            if not context:
                raise BadRequestError("Template context is required")

            response = _request_docgen_service(
                "templates/render?use_total_pages=true",
                HttpMethod.POST,
                {
                    "template_key": template_key,
                    "app": AUTH_APP,
                    "data": context,
                    "output_type": output_type,
                },
            )

            if response.status_code == 400:
                current_app.logger.error(f"Invalid template request: {response.text}")
                raise BadRequestError("Invalid template or context data")

            if response.status_code == 404:
                raise ResourceNotFoundError(f"Template '{template_key}' not found")

            if response.status_code != 200:
                current_app.logger.error(
                    f"Document generation service returned status {response.status_code}: {response.text}"
                )
                raise BadRequestError("Unable to generate document at this time")

            return response

        except (RetryError, requests.exceptions.RequestException) as e:
            current_app.logger.error(
                f"Document generation service unavailable for template '{template_key}': {str(e)}",
                exc_info=True
            )
            raise ServiceUnavailableError(
                "The document generation service is temporarily unavailable. Please try again later."
            )
        except (PermissionDeniedError, BadRequestError, ResourceNotFoundError):
            # Re-raise custom exceptions
            raise
        except (KeyError, ValueError, TypeError) as e:
            current_app.logger.error(
                f"Error processing template '{template_key}': {str(e)}",
                exc_info=True
            )
            raise BadRequestError("Unable to process document template")


@retry(
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
)
def _request_docgen_service(
    relative_url, http_method: HttpMethod = HttpMethod.GET, data=None
):
    """REST Api call to docgen service."""
    try:
        token = getattr(g, "access_token", None)
        if not token:
            raise PermissionDeniedError("No access token found")

        docgen_service_url = current_app.config["DOCGEN_SERVICE_URL"]
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        url = f"{docgen_service_url}/api/{relative_url}"

        if http_method == HttpMethod.GET:
            response = requests.get(url, headers=headers, timeout=60)
        elif http_method == HttpMethod.POST:
            response = requests.post(
                url=url, headers=headers, data=json.dumps(data), timeout=60
            )
        else:
            raise ValueError("Invalid HTTP method")

        response.raise_for_status()
        return response

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Error making request to document generation service: {str(e)}"
        ) from e
