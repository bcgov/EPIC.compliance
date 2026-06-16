"""Test suite for IR download request endpoints (Finding #3)."""

from http import HTTPStatus
from urllib.parse import urljoin

import pytest

from compliance_api.models.inspection_record import InspectionRecord


API_BASE_URL = "/api/"


@pytest.fixture
def inspection_record(created_inspection):
    """Create an inspection record for IR download tests."""
    return InspectionRecord.create_inspection_record(
        {
            "inspection_id": created_inspection.id,
            "ir_status_id": 1,
        }
    )


def test_create_download_request_succeeds(
    client, auth_header, created_inspection, inspection_record
):
    """POST /download-requests returns 201 for an authenticated caller."""
    url = urljoin(
        API_BASE_URL,
        f"inspections/{created_inspection.id}/inspection-records/{inspection_record.id}/download-requests",
    )

    result = client.post(url, headers=auth_header)

    assert result.status_code == HTTPStatus.CREATED
    assert result.json["inspection_record_id"] == inspection_record.id


def test_get_latest_download_request_uses_token_identity(
    client, auth_header, auth_header_super_user, created_inspection, inspection_record
):
    """GET /download-requests/latest is scoped to the calling user's token identity.

    The endpoint must derive the caller's identity from the token, not accept a
    client-supplied query parameter.

    - POST as the default VIEWER user creates a record stored under that identity.
    - GET with the same VIEWER token returns 200 (token identity matched the stored value).
    - GET with a *different* token (SUPERUSER) returns 404 — proving the GET uses the
      token identity to scope results, not an open query or a client-supplied param.
    """
    inspection_id = created_inspection.id
    record_id = inspection_record.id
    base = f"inspections/{inspection_id}/inspection-records/{record_id}/download-requests"

    # Create a request under the VIEWER token
    post_result = client.post(urljoin(API_BASE_URL, base), headers=auth_header)
    assert post_result.status_code == HTTPStatus.CREATED

    # Same token → 200
    get_url = urljoin(API_BASE_URL, f"{base}/latest")
    result_same = client.get(get_url, headers=auth_header)
    assert result_same.status_code == HTTPStatus.OK

    # Different token (SUPERUSER has no request for this record) → 404, not the VIEWER's record
    result_other = client.get(get_url, headers=auth_header_super_user)
    assert result_other.status_code == HTTPStatus.NOT_FOUND
