"""test suit for enforcement actions."""

from http import HTTPStatus
from urllib.parse import urljoin


API_BASE_URL = "/api/"


def test_get_enforcement_actions(client, auth_header):
    """Get enforcement actions."""
    url = urljoin(API_BASE_URL, "enforcement-actions")
    result = client.get(url, headers=auth_header)
    assert len(result.json) == 12
    assert result.status_code == HTTPStatus.OK
