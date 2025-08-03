"""test suit for complaint."""

from datetime import datetime
from http import HTTPStatus
from urllib.parse import urljoin

from faker import Faker
from flask import json

from compliance_api.models.complaint import ComplaintSourceEnum, ComplaintStatusEnum
from compliance_api.services import CaseFileService, ComplaintService
from compliance_api.utils.constant import INPUT_DATE_TIME_FORMAT
from tests.utilities.factory_scenario import CasefileScenario, ComplaintScenario


API_BASE_URL = "/api/"
fake = Faker()


def test_get_complaint_sources(client, auth_header):
    """Get complaint sources."""
    url = urljoin(API_BASE_URL, "complaints/sources")
    print(url)
    result = client.get(url, headers=auth_header)
    assert len(result.json) == 4
    assert result.status_code == HTTPStatus.OK


def test_get_case_files_without_case_file_id_passed(
    client, auth_header, mocker, mock_track_service, created_staff, created_case_file
):
    """Get case files."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    complaint_data = ComplaintScenario.complaint_default.value
    complaint_data["primary_officer_id"] = created_staff.id
    complaint_data["case_file_id"] = created_case_file.id
    ComplaintService.create(complaint_data)

    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    case_file_data = CasefileScenario.default_value.value
    case_file_data["primary_officer_id"] = created_staff.id
    second_case_file = CaseFileService.create(case_file_data)

    complaint_data["case_file_id"] = second_case_file.id
    ComplaintService.create(complaint_data)

    result = client.get(urljoin(API_BASE_URL, "complaints"), headers=auth_header)

    assert result.status_code == HTTPStatus.OK
    assert len(result.json) == 2


def test_get_case_files_with_case_file_id_passed(
    client, auth_header, mocker, mock_track_service, created_staff, created_case_file
):
    """Get case files."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    complaint_data = ComplaintScenario.complaint_default.value
    complaint_data["primary_officer_id"] = created_staff.id
    complaint_data["case_file_id"] = created_case_file.id
    ComplaintService.create(complaint_data)

    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    case_file_data = CasefileScenario.default_value.value
    case_file_data["primary_officer_id"] = created_staff.id
    second_case_file = CaseFileService.create(case_file_data)

    complaint_data["case_file_id"] = second_case_file.id
    ComplaintService.create(complaint_data)

    result = client.get(
        urljoin(API_BASE_URL, f"complaints?case_file_id={second_case_file.id}"),
        headers=auth_header,
    )

    assert result.status_code == HTTPStatus.OK
    # Check that the response has the expected pagination structure
    assert "items" in result.json
    assert "total" in result.json
    assert result.json["items"][0].get("case_file_id") == second_case_file.id
    assert len(result.json["items"]) == 1
    assert result.json["total"] == 1


def test_create_complaint_by_non_super_user_fail(
    client, auth_header, created_staff, created_case_file, mock_track_service
):
    """Create case file by non-super user should fail."""
    complaint_data = ComplaintScenario.complaint_default.value
    complaint_data["primary_officer_id"] = created_staff.id
    complaint_data["case_file_id"] = created_case_file.id
    result = client.post(
        urljoin(API_BASE_URL, "complaints"),
        headers=auth_header,
        data=json.dumps(complaint_data),
    )
    assert result.status_code == HTTPStatus.FORBIDDEN


def test_create_complaint_by_super_user(
    client,
    auth_header_super_user,
    created_staff,
    created_case_file,
    mocker,
    mock_track_service,
):
    """Create case file by non-super user should fail."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    complaint_data = ComplaintScenario.complaint_default.value
    complaint_data["primary_officer_id"] = created_staff.id
    complaint_data["case_file_id"] = created_case_file.id
    result = client.post(
        urljoin(API_BASE_URL, "complaints"),
        headers=auth_header_super_user,
        data=json.dumps(complaint_data),
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json.get("case_file_id") == created_case_file.id
    assert result.json.get("primary_officer_id") == created_staff.id
    assert result.json.get("status") == ComplaintStatusEnum.OPEN.value


def test_get_complaint_by_not_found(
    client, auth_header, created_staff, created_case_file
):
    """Get complaint which doesn't exist."""
    result = client.get(urljoin(API_BASE_URL, "complaints/9999"), headers=auth_header)
    print(result.json)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_get_complaint_by_id(
    client, auth_header, created_staff, created_case_file, mocker, mock_track_service
):
    """Get complaint which doesn't exist."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    complaint_data = ComplaintScenario.complaint_default.value
    complaint_data["primary_officer_id"] = created_staff.id
    complaint_data["case_file_id"] = created_case_file.id
    created_complaint = ComplaintService.create(complaint_data)
    result = client.get(
        urljoin(API_BASE_URL, f"complaints/{created_complaint.id}"), headers=auth_header
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json.get("case_file_id") == created_case_file.id
    assert result.json.get("primary_officer_id") == created_staff.id


def test_update_complaint_by_super_user(
    client,
    auth_header_super_user,
    created_staff,
    created_case_file,
    mocker,
    mock_track_service,
):
    """Create case file by non-super user should fail."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    complaint_data = ComplaintScenario.complaint_default.value
    complaint_data["primary_officer_id"] = created_staff.id
    complaint_data["case_file_id"] = created_case_file.id
    created_complaint = ComplaintService.create(complaint_data)
    complaint_data["concern_description"] = fake.word()
    complaint_data["location_description"] = fake.word()
    complaint_data["date_received"] = datetime.now().strftime(INPUT_DATE_TIME_FORMAT)
    complaint_data["source_type_id"] = ComplaintSourceEnum.FIRSTNATION.value
    complaint_data["source_first_nation_id"] = fake.random_number()
    del complaint_data["case_file_id"]
    complaint_data["complaint_source_contact"] = {
        "description": fake.text(max_nb_chars=50),
        "full_name": fake.word(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "comment": fake.text(max_nb_chars=50),
    }
    result = client.patch(
        urljoin(API_BASE_URL, f"complaints/{created_complaint.id}"),
        headers=auth_header_super_user,
        data=json.dumps(complaint_data),
    )
    assert result.status_code == HTTPStatus.OK
    assert (
        result.json.get("concern_description") == complaint_data["concern_description"]
    )
    assert (
        result.json.get("location_description")
        == complaint_data["location_description"]
    )
    assert result.json.get("source_type_id") == complaint_data["source_type_id"]


def test_complaint_delete_by_non_super_user(
    client, auth_header, created_staff, created_case_file, mocker, mock_track_service
):
    """Delete complaint by non-superuser."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    complaint_data = ComplaintScenario.complaint_default.value
    complaint_data["primary_officer_id"] = created_staff.id
    complaint_data["case_file_id"] = created_case_file.id
    created_complaint = ComplaintService.create(complaint_data)
    mocker.stop(contains_role)

    result = client.delete(
        urljoin(API_BASE_URL, f"complaints/{created_complaint.id}"), headers=auth_header
    )
    assert result.status_code == HTTPStatus.FORBIDDEN


def test_complaint_delete_by_super_user(
    client,
    auth_header_super_user,
    created_staff,
    created_case_file,
    mocker,
    mock_track_service,
):
    """Delete complaint by non-superuser."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    complaint_data = ComplaintScenario.complaint_default.value
    complaint_data["primary_officer_id"] = created_staff.id
    complaint_data["case_file_id"] = created_case_file.id
    created_complaint = ComplaintService.create(complaint_data)
    mocker.stop(contains_role)
    print(created_complaint.is_deleted)
    result = client.delete(
        urljoin(API_BASE_URL, f"complaints/{created_complaint.id}"),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.NO_CONTENT

    get_result = client.get(
        urljoin(API_BASE_URL, f"complaints/{created_complaint.id}"),
        headers=auth_header_super_user,
    )
    assert get_result.status_code == HTTPStatus.NOT_FOUND


def test_complaint_get_requirement_details(
    client, auth_header, created_staff, created_case_file, mocker, mock_track_service
):
    """Delete complaint by non-superuser."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    complaint_data = ComplaintScenario.complaint_with_requirement_details.value
    complaint_data["primary_officer_id"] = created_staff.id
    complaint_data["case_file_id"] = created_case_file.id
    created_complaint = ComplaintService.create(complaint_data)

    get_result = client.get(
        urljoin(API_BASE_URL, f"complaints/{created_complaint.id}/requirement-details"),
        headers=auth_header,
    )

    assert get_result.status_code == HTTPStatus.OK
    input_source_details = complaint_data.get("requirement_source_details")
    assert get_result.json.get("topic_id") == input_source_details.get("topic_id")
    assert get_result.json.get("additional_details").get(
        "condition_number"
    ) == input_source_details.get("condition_number")


def test_complaint_get_source_contact_details(
    client, auth_header, created_staff, created_case_file, mocker, mock_track_service
):
    """Delete complaint by non-superuser."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    complaint_data = ComplaintScenario.complaint_with_requirement_details.value
    complaint_data["primary_officer_id"] = created_staff.id
    complaint_data["case_file_id"] = created_case_file.id
    created_complaint = ComplaintService.create(complaint_data)

    get_result = client.get(
        urljoin(API_BASE_URL, f"complaints/{created_complaint.id}/source-contacts"),
        headers=auth_header,
    )

    assert get_result.status_code == HTTPStatus.OK
    input_source_details = complaint_data.get("complaint_source_contact")
    assert get_result.json.get("full_name") == input_source_details.get("full_name")
    assert get_result.json.get("email") == input_source_details.get("email")
    assert get_result.json.get("phone") == input_source_details.get("phone")
    assert get_result.json.get("comment") == input_source_details.get("comment")
