"""Common fixture for all test."""

import copy
from datetime import datetime

import pytest
from faker import Faker

from compliance_api.models import CaseFile as CaseFileModel
from compliance_api.services import InspectionRequirementService, InspectionService
from tests.utilities.factory_scenario import (
    CasefileScenario, InspectionRequirementScenario, InspectionScenario, StaffScenario)


fake = Faker()


@pytest.fixture
def mock_auth_service(mocker):
    """Fixture to mock AuthService methods."""
    mock_get_user_by_guid = mocker.patch(
        "compliance_api.services.authorize_service.auth_service.AuthService.get_epic_user_by_guid"
    )
    mock_get_user_by_guid.return_value = {
        "first_name": fake.word(),
        "last_name": fake.word(),
        "username": fake.word(),
    }

    mock_update_user_group = mocker.patch(
        "compliance_api.services.authorize_service.auth_service.AuthService.update_user_group"
    )
    mock_update_user_group.return_value = {}
    mock_delete_user_group = mocker.patch(
        "compliance_api.services.authorize_service.auth_service.AuthService.delete_user_group"
    )
    mock_delete_user_group.return_value = {}

    yield mock_get_user_by_guid, mock_update_user_group, mock_delete_user_group


@pytest.fixture
def mock_track_service(mocker):
    """Fixture to mock TrackService methods."""
    mock_get_project_by_id = mocker.patch(
        "compliance_api.services.epic_track_service.track_service.TrackService.get_project_by_id"
    )
    mock_get_project_by_id.return_value = {
        "ea_certificate": fake.word(),
        "type": {"name": fake.word()},
        "abbreviation": "PRJ",
        "sub_type": {"name": fake.word()},
        "proponent": {"name": fake.word()},
    }

    mock_get_project_statuses = mocker.patch(
        "compliance_api.services.epic_track_service.track_service.TrackService.get_project_statuses"
    )
    mock_get_project_statuses.return_value = [
        {
            "id": 13,
            "name": "Preconstruction",
            "component": "COMPLIANCE",
            "is_active": True,
        }
    ]

    yield mock_get_project_by_id, mock_get_project_statuses


@pytest.fixture
def mock_doc_service(mocker):
    """Fixture to mock DocService methods."""
    mock_get_presigned_url = mocker.patch(
        "compliance_api.services.document_service.doc_service.DocService.get_presigned_url"
    )
    mock_get_presigned_url.return_value = {
        "presigned_url": "https://example.com/presigned-url"
    }

    yield mock_get_presigned_url


@pytest.fixture
def mock_doc_gen_service(mocker):
    """Fixture to mock DocGenService methods."""

    def mock_render_template(template_name, data, output_format="html"):
        """Mock render_template that returns appropriate format based on output_format."""
        mock_response = mocker.MagicMock()

        if output_format == "pdf":
            # Return response object with .content attribute for PDF format
            mock_response.content = b"Mock PDF content"
        else:
            # Return HTML content for HTML format
            mock_response.json.return_value = {
                "content": "<html><body>Mock Document</body></html>"
            }

        return mock_response

    # Set up the mock render_template method
    mock_generate_doc = mocker.patch(
        "compliance_api.services.docgen_service.docgen_service.DocGenService.render_template"
    )
    mock_generate_doc.side_effect = mock_render_template

    yield mock_generate_doc


@pytest.fixture(scope="session")
def mock_requests(mocker):
    """Fixture to mock requests library."""
    mock_delete = mocker.patch("requests.delete")
    mock_delete.return_value.status_code = 204

    yield mock_delete


@pytest.fixture
def created_staff(mocker):
    """Create staff."""
    user_data = StaffScenario.default_data.value
    auth_user_guid = str(datetime.utcnow().timestamp() * 1000)
    user_data["auth_user_guid"] = auth_user_guid
    new_user = StaffScenario.create(user_data)
    return new_user


# Note: Test staff users are now created automatically by the session-scoped
# setup_test_staff_users fixture in conftest.py. Individual fixtures are not needed.


# Global counter for unique case file numbers
_case_file_counter = 0


@pytest.fixture
def created_case_file(created_staff):
    """Create a case file for testing."""
    global _case_file_counter
    case_file_data = copy.copy(CasefileScenario.default_value.value)
    case_file_data["primary_officer_id"] = created_staff.id
    # Use a counter to ensure unique case file numbers
    _case_file_counter += 1
    case_file_data["case_file_number"] = f"CF{_case_file_counter:04d}"
    case_file = CaseFileModel.create_case_file(case_file_data)
    return case_file


@pytest.fixture
def created_inspection(
    app, created_case_file, created_staff, mocker, mock_track_service
):
    """Create an inspection for testing."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    inspection_data = copy.copy(InspectionScenario.default_value.value)
    inspection_data["case_file_id"] = created_case_file.id
    inspection_data["primary_officer_id"] = created_staff.id
    inspection_data["initiation_id"] = 1
    inspection_data["start_date"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    inspection = InspectionService.create(inspection_data)
    return inspection


@pytest.fixture
def created_inspection_requirement(app, created_inspection, mocker):
    """Create an inspection requirement for testing."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    access_check_fn = mocker.patch(
        "compliance_api.services.service_utils.ServiceUtils.access_check_update_for_inspection"
    )
    access_check_fn.return_value = True
    requirement_data = copy.copy(InspectionRequirementScenario.default_value.value)
    # Ensure the requirement has ORDER enforcement action (ID 5)
    requirement_data["enforcement_action_ids"] = [5]
    requirement = InspectionRequirementService.create(
        created_inspection.id, requirement_data
    )
    return requirement
