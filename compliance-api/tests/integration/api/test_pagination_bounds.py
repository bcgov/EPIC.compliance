"""End-to-end checks that the paginated list endpoints reject bad page_size (COMP-932)."""
from http import HTTPStatus

import pytest

from compliance_api.utils.constant import MAX_PAGE_SIZE

# Every list endpoint that reads page_size straight from request.args.
LIST_ENDPOINTS = [
    "/api/inspections",
    "/api/case-files",
    "/api/complaints",
    "/api/inspection-requirements",
]

BAD_PAGE_SIZES = [str(MAX_PAGE_SIZE + 1), "1000000", "abc", "0", "-5"]


@pytest.mark.parametrize("url", LIST_ENDPOINTS)
@pytest.mark.parametrize("page_size", BAD_PAGE_SIZES)
def test_rejects_invalid_page_size(client, auth_header_super_user, url, page_size):
    """An out-of-range or non-numeric page_size is a validation error, never a 500."""
    result = client.get(f"{url}?page_size={page_size}", headers=auth_header_super_user)

    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("url", LIST_ENDPOINTS)
@pytest.mark.parametrize("page_no", ["abc", "0", "-1"])
def test_rejects_invalid_page_no(client, auth_header_super_user, url, page_no):
    """page_no is parsed on the same path and gets the same treatment."""
    result = client.get(f"{url}?page_no={page_no}", headers=auth_header_super_user)

    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("url", LIST_ENDPOINTS)
def test_accepts_the_maximum_page_size(client, auth_header_super_user, url):
    """The cap itself is a valid request, so nothing legitimate is broken."""
    result = client.get(
        f"{url}?page_size={MAX_PAGE_SIZE}", headers=auth_header_super_user
    )

    assert result.status_code == HTTPStatus.OK


@pytest.mark.parametrize("url", LIST_ENDPOINTS)
def test_accepts_a_request_without_pagination_parameters(
    client, auth_header_super_user, url
):
    """Omitting the parameters keeps the existing default behaviour."""
    result = client.get(url, headers=auth_header_super_user)

    assert result.status_code == HTTPStatus.OK


def test_continuation_report_rejects_oversized_page_size(
    client, auth_header_super_user, created_case_file
):
    """The continuation report list validates through the schema rather than the parser."""
    result = client.get(
        f"/api/continuation-reports?case_file_id={created_case_file.id}"
        f"&page_size={MAX_PAGE_SIZE + 1}",
        headers=auth_header_super_user,
    )

    assert result.status_code in (
        HTTPStatus.UNPROCESSABLE_ENTITY,
        HTTPStatus.BAD_REQUEST,
    )
