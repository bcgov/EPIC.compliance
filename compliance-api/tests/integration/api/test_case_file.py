"""Test suite for case file."""

import copy
import json
from datetime import datetime
from http import HTTPStatus
from urllib.parse import urljoin

import pytest
from faker import Faker

from compliance_api.models import CaseFile as CaseFileModel
from compliance_api.models import CaseFileStatusEnum
from compliance_api.models import ContinuationReport as ContinuationReportModel
from compliance_api.models import ContinuationReportKey as ContinuationReportKeyModel
from compliance_api.models import db
from compliance_api.services.case_file import CaseFileService
from compliance_api.utils.enum import ContextEnum
from tests.utilities.factory_scenario import CasefileScenario, StaffScenario, TokenJWTClaims
from tests.utilities.factory_utils import factory_auth_header


API_BASE_URL = "/api/"
fake = Faker()


@pytest.fixture(scope="session")
def mock_auth_service(mocker):
    """Fixture to mock AuthService methods."""
    mock_get_user_by_guid = mocker.patch(
        "compliance_api.services.authorize_service.auth_service.AuthService.get_epic_user_by_guid"
    )
    mock_get_user_by_guid.return_value = {
        "first_name": fake.word(),
        "last_name": fake.word(),
        "username": fake.word(),  # Fixed the key to "username"
    }

    mock_update_user_group = mocker.patch(
        "compliance_api.services.authorize_service.auth_service.AuthService.update_user_group"
    )
    mock_update_user_group.return_value = {}

    yield mock_get_user_by_guid, mock_update_user_group


@pytest.fixture
def created_staff(mocker):
    """Create staff."""
    user_data = StaffScenario.default_data.value
    auth_user_guid = str(datetime.utcnow().timestamp() * 1000)
    user_data["auth_user_guid"] = auth_user_guid
    new_user = StaffScenario.create(user_data)
    return new_user


def test_get_case_file_initiation_options(client, auth_header):
    """Get complaint sources."""
    url = urljoin(API_BASE_URL, "case-files/initiation-options")
    result = client.get(url, headers=auth_header)
    assert len(result.json) == 3
    assert result.status_code == HTTPStatus.OK


def test_create_case_file_without_file_number(
    client, auth_header_super_user, created_staff
):
    """Create case file with basic fields."""
    url = urljoin(API_BASE_URL, "case-files")
    case_file_data = CasefileScenario.default_value.value
    case_file_data["primary_officer_id"] = created_staff.id
    result = client.post(
        url,
        data=json.dumps(CasefileScenario.default_value.value),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["case_file_number"] == f"{datetime.now().year}0001"
    assert result.json["case_file_status"] == CaseFileStatusEnum.OPEN.value
    #  check continuation report entries
    cr_entry = (
        db.session.query(ContinuationReportModel)
        .filter_by(
            case_file_id=result.json.get("id"),
            context_id=result.json.get("id"),
            context_type=ContextEnum.CASE_FILE,
        )
        .first()
    )
    assert cr_entry is not None
    assert cr_entry.text == f"{result.json.get('case_file_number')} is created"
    assert (
        cr_entry.rich_text == f"<p>{result.json.get('case_file_number')} is created</p>"
    )
    #  Check continuation report entry key
    cr_key = (
        db.session.query(ContinuationReportKeyModel)
        .filter_by(
            key=result.json.get("case_file_number"),
            key_context=ContextEnum.CASE_FILE,
            report_id=cr_entry.id,
        )
        .first()
    )
    assert cr_key is not None


def test_create_case_file_with_non_superuser(client, auth_header, created_staff):
    """Create case file with basic fields."""
    url = urljoin(API_BASE_URL, "case-files")
    case_file_data = CasefileScenario.default_value.value
    case_file_data["primary_officer_id"] = created_staff.id
    result = client.post(
        url, data=json.dumps(CasefileScenario.default_value.value), headers=auth_header
    )
    assert result.status_code == HTTPStatus.FORBIDDEN


def test_create_case_file_with_file_number(client, auth_header_super_user):
    """Create case file with file number."""
    user_data = StaffScenario.default_data.value
    auth_user_guid = fake.word()
    user_data["auth_user_guid"] = auth_user_guid
    new_user = StaffScenario.create(user_data)
    url = urljoin(API_BASE_URL, "case-files")
    case_file_data = copy.copy(CasefileScenario.default_value.value)
    case_file_data["case_file_number"] = "XYZ"
    case_file_data["primary_officer_id"] = new_user.id
    case_file_data["officer_ids"] = [new_user.id]
    result = client.post(
        url, data=json.dumps(case_file_data), headers=auth_header_super_user
    )
    assert result.json["case_file_number"] == "XYZ"
    assert result.json["case_file_status"] == CaseFileStatusEnum.OPEN.value
    assert result.json["primary_officer_id"] == new_user.id
    assert result.status_code == HTTPStatus.CREATED

    officers = CaseFileService.get_other_officers(result.json["id"])
    assert len(officers) == 1
    assert officers[0].id == new_user.id


def test_create_case_file_with_existing_case_file_number(
    client, auth_header_super_user, created_staff
):
    """Create case file with basic fields."""
    url = urljoin(API_BASE_URL, "case-files")
    case_file_data = copy.copy(CasefileScenario.default_value.value)
    case_file_data["case_file_number"] = "XYZ"
    case_file_data["primary_officer_id"] = created_staff.id
    result = client.post(
        url, data=json.dumps(case_file_data), headers=auth_header_super_user
    )
    print(result.json)
    assert result.status_code == HTTPStatus.CONFLICT


def test_get_case_files_by_project_id(client, auth_header):
    """Get case files by project id."""
    case_file_data = copy.copy(CasefileScenario.default_value.value)
    case_file_data["case_file_number"] = f"test_{datetime.utcnow().timestamp()}"
    CaseFileModel.create_case_file(case_file_data)
    url = urljoin(API_BASE_URL, "case-files?project_id=1")
    result = client.get(url, headers=auth_header)

    assert result.status_code == HTTPStatus.OK
    assert len(result.json) == 2


# def test_get_case_files(client, auth_header, mocker):
#     """Get all case files."""
#     contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
#     contains_role.return_value = True

#     case_file_data = copy.copy(CasefileScenario.default_value.value)
#     case_file_data["project_id"] = 2
#     case_file_data["case_file_number"] = f"test_{datetime.utcnow().timestamp()}"
#     case_file_data["created_by"] = "test_user"
#     created_case = CaseFileService.create(case_file_data)
#     db.session.commit()
#     url = urljoin(API_BASE_URL, "case-files")
#     result = client.get(url, headers=auth_header)

#     assert result.status_code == HTTPStatus.OK
#     # Check that the response has the expected pagination structure
#     assert "items" in result.json
#     assert "total" in result.json

#     # Find the created case file in the results
#     filtered_case_file = next(
#         (case for case in result.json["items"] if case["id"] == created_case.id), None
#     )
#     assert filtered_case_file is not None, f"Created case file with ID {created_case.id} not found in API response"


def test_get_case_file_by_id(client, auth_header, mocker):
    """Test case file by id."""
    mock_get_user_by_guid = mocker.patch(
        "compliance_api.services.epic_track_service.track_service.TrackService.get_project_by_id"
    )
    mock_get_user_by_guid.return_value = {
        "ea_certificate": fake.word(),
        "type": {"name": fake.word()},
        "sub_type": {"name": fake.word()},
        "proponent": {"name": fake.word()},
    }
    case_file_data = copy.copy(CasefileScenario.default_value.value)
    case_file_data["project_id"] = 2
    case_file_data["case_file_number"] = f"test_{datetime.utcnow().timestamp()}"
    case_file_data["case_file_status"] = CaseFileStatusEnum.OPEN
    created_case_file = CaseFileModel.create_case_file(case_file_data)
    url = urljoin(API_BASE_URL, f"case-files/{created_case_file.id}")
    result = client.get(url, headers=auth_header)

    assert result.status_code == HTTPStatus.OK
    assert result.json["id"] == created_case_file.id
    assert result.json["case_file_status"] == CaseFileStatusEnum.OPEN.value


def test_get_case_file_officers(client, auth_header_super_user, mocker):
    """Create case file with file number."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    user_data = StaffScenario.default_data.value
    auth_user_guid = fake.word()
    user_data["auth_user_guid"] = auth_user_guid
    new_user = StaffScenario.create(user_data)
    case_file_data = copy.copy(CasefileScenario.default_value.value)
    case_file_data["case_file_number"] = f"test_{datetime.utcnow().timestamp()}"
    case_file_data["primary_officer_id"] = new_user.id
    case_file_data["officer_ids"] = [new_user.id]
    result = CaseFileService.create(case_file_data)
    url = urljoin(API_BASE_URL, f"case-files/{result.id}/officers")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert len(result.json) == 1
    assert result.json[0].get("id") == new_user.id


def test_get_case_file_by_number(client, auth_header_super_user, mocker):
    """Get case file by case file number."""
    mock_get_user_by_guid = mocker.patch(
        "compliance_api.services.epic_track_service.track_service.TrackService.get_project_by_id"
    )
    mock_get_user_by_guid.return_value = {
        "ea_certificate": fake.word(),
        "type": {"name": fake.word()},
        "sub_type": {"name": fake.word()},
        "proponent": {"name": fake.word()},
    }
    case_file_data = copy.copy(CasefileScenario.default_value.value)
    case_file_data["case_file_number"] = f"test_{datetime.utcnow().timestamp()}"
    result = CaseFileModel.create_case_file(case_file_data)
    url = urljoin(
        API_BASE_URL,
        f"case-files/case-file-numbers/{case_file_data['case_file_number']}",
    )
    result = client.get(url, headers=auth_header_super_user)

    assert result.status_code == HTTPStatus.OK
    assert result.json["id"] == result.json.get("id")
    assert result.json["case_file_number"] == case_file_data["case_file_number"]


def test_case_file_update(client, auth_header_super_user, created_staff, mocker):
    """Update case file."""
    mock_get_user_by_guid = mocker.patch(
        "compliance_api.services.epic_track_service.track_service.TrackService.get_project_by_id"
    )
    mock_get_user_by_guid.return_value = {
        "ea_certificate": fake.word(),
        "type": {"name": fake.word()},
        "sub_type": {"name": fake.word()},
        "proponent": {"name": fake.word()},
    }
    #  creating case file without officers or primary officer
    case_file_data = copy.copy(CasefileScenario.default_value.value)
    case_file_data["case_file_number"] = f"test_{datetime.utcnow().timestamp()}"
    case_file_data["primary_officer_id"] = created_staff.id
    case_file_data["project_description"] = "sample description"
    created_result = CaseFileModel.create_case_file(case_file_data)
    url = urljoin(
        API_BASE_URL,
        f"case-files/case-file-numbers/{case_file_data['case_file_number']}",
    )
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    officers = CaseFileService.get_other_officers(result.json["id"])
    assert len(officers) == 0
    assert result.json.get("project_description") == "sample description"
    #  create one user
    user_data = StaffScenario.default_data.value
    auth_user_guid = fake.word()
    user_data["auth_user_guid"] = auth_user_guid
    new_user = StaffScenario.create(user_data)
    #  update the payload by adding primary officer and officers
    case_file_data["primary_officer_id"] = new_user.id
    case_file_data["officer_ids"] = [new_user.id]
    case_file_data["project_description"] = "changed description"
    url = urljoin(API_BASE_URL, f"case-files/{created_result.id}")
    result = client.patch(
        url, data=json.dumps(case_file_data), headers=auth_header_super_user
    )

    assert result.status_code == HTTPStatus.OK
    assert result.json["primary_officer_id"] == new_user.id
    assert result.json.get("project_description") == "changed description"
    officers = CaseFileService.get_other_officers(result.json["id"])
    assert len(officers) == 1
    assert officers[0].id == new_user.id
    #  update the payload by making the officer list empty
    case_file_data["primary_officer_id"] = new_user.id
    case_file_data["officer_ids"] = []
    url = urljoin(API_BASE_URL, f"case-files/{created_result.id}")
    result = client.patch(
        url, data=json.dumps(case_file_data), headers=auth_header_super_user
    )

    assert result.status_code == HTTPStatus.OK
    assert result.json["primary_officer_id"] == new_user.id
    officers = CaseFileService.get_other_officers(result.json["id"])
    assert len(officers) == 0


def test_case_file_update_viewer_fails(client, auth_header, created_staff):
    """Update as Viewer."""
    case_file_data = copy.copy(CasefileScenario.default_value.value)
    case_file_data["case_file_number"] = f"test_{datetime.utcnow().timestamp()}"
    case_file_data["primary_officer_id"] = created_staff.id
    created_result = CaseFileModel.create_case_file(case_file_data)
    url = urljoin(API_BASE_URL, f"case-files/{created_result.id}")
    result = client.patch(url, data=json.dumps(case_file_data), headers=auth_header)
    assert result.status_code == HTTPStatus.FORBIDDEN


def test_case_file_update_with_primary(
    client, jwt, created_staff, auth_header_super_user
):
    """Update as primary."""
    case_file_data = copy.copy(CasefileScenario.default_value.value)
    case_file_data["case_file_number"] = str(datetime.utcnow().timestamp() * 1000)
    case_file_data["primary_officer_id"] = created_staff.id
    created_result = CaseFileModel.create_case_file(case_file_data)
    header = TokenJWTClaims.default.value
    header["preferred_username"] = created_staff.auth_user_guid
    headers = factory_auth_header(jwt=jwt, claims=header)

    url = urljoin(API_BASE_URL, f"case-files/{created_result.id}")
    result = client.patch(url, data=json.dumps(case_file_data), headers=headers)
    assert result.status_code == HTTPStatus.OK


def test_case_file_close(client, jwt, created_staff, mocker):
    """Update as primary."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    case_file_data = copy.copy(CasefileScenario.default_value.value)
    case_file_data["case_file_number"] = str(datetime.utcnow().timestamp() * 1000)
    case_file_data["primary_officer_id"] = created_staff.id
    created_result = CaseFileService.create(case_file_data)
    print(created_result)
    case_file_id = created_result.id
    case_file_number = created_result.case_file_number
    header = TokenJWTClaims.default.value
    header["preferred_username"] = created_staff.auth_user_guid
    headers = factory_auth_header(jwt=jwt, claims=header)
    print(created_result)
    url = urljoin(API_BASE_URL, f"case-files/{created_result.id}/status")
    result = client.patch(url, data=json.dumps({"status": "OPEN"}), headers=headers)
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    result = client.patch(url, data=json.dumps({"status": "CLOSED"}), headers=headers)
    assert result.status_code == HTTPStatus.NO_CONTENT
    cr_entry = (
        db.session.query(ContinuationReportModel)
        .filter_by(
            case_file_id=case_file_id,
            context_id=case_file_id,
            context_type=ContextEnum.CASE_FILE,
            text=f"{case_file_number} is closed",
        )
        .first()
    )
    assert cr_entry is not None
    assert cr_entry.rich_text == f"<p>{case_file_number} is closed</p>"
    #  Check continuation report entry key
    cr_key = (
        db.session.query(ContinuationReportKeyModel)
        .filter_by(
            key=case_file_number,
            key_context=ContextEnum.CASE_FILE,
            report_id=cr_entry.id,
        )
        .all()
    )
    assert cr_key is not None
    result = client.patch(url, data=json.dumps({"status": "CLOSED"}), headers=headers)
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    result = client.patch(url, data=json.dumps({"status": "OPEN"}), headers=headers)
    assert result.status_code == HTTPStatus.NO_CONTENT
    cr_entry = (
        db.session.query(ContinuationReportModel)
        .filter_by(
            case_file_id=case_file_id,
            context_id=case_file_id,
            context_type=ContextEnum.CASE_FILE,
            text=f"{case_file_number} is reopened",
        )
        .first()
    )
    assert cr_entry is not None
    assert cr_entry.rich_text == f"<p>{case_file_number} is reopened</p>"
    #  Check continuation report entry key
    cr_key = (
        db.session.query(ContinuationReportKeyModel)
        .filter_by(
            key=case_file_number,
            key_context=ContextEnum.CASE_FILE,
            report_id=cr_entry.id,
        )
        .all()
    )
    assert cr_key is not None


def test_case_file_delete(client, jwt, created_staff, mocker, auth_header_super_user):
    """Update as primary."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    case_file_data = copy.copy(CasefileScenario.default_value.value)
    case_file_data["case_file_number"] = str(datetime.utcnow().timestamp() * 1000)
    case_file_data["primary_officer_id"] = created_staff.id
    created_result = CaseFileService.create(case_file_data)

    url = urljoin(API_BASE_URL, f"case-files/{created_result.id}")
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NO_CONTENT
    url = urljoin(API_BASE_URL, f"case-files/{created_result.id}")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_case_file_linking(client, jwt, created_staff, auth_header_super_user, mocker):
    """Link case file."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    #  Create source case file
    case_file_data = copy.copy(CasefileScenario.default_value.value)
    case_file_data["case_file_number"] = str(datetime.utcnow().timestamp() * 1000)
    case_file_data["primary_officer_id"] = created_staff.id
    source_case_file = CaseFileService.create(case_file_data)
    # Create target case file
    case_file_data = copy.copy(CasefileScenario.default_value.value)
    case_file_data["case_file_number"] = str(datetime.utcnow().timestamp() * 1000)
    case_file_data["primary_officer_id"] = created_staff.id
    target_case_file = CaseFileService.create(case_file_data)
    url = urljoin(API_BASE_URL, f"case-files/{source_case_file.id}/links")
    post_data = {"link_case_file_id": target_case_file.id}
    result = client.post(
        url,
        data=json.dumps(post_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    # Get the link
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert len(result.json) == 1
