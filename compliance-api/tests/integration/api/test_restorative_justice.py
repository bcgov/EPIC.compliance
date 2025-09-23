"""Test suite for restorative justices."""

import copy
import json
from datetime import datetime, timezone
from http import HTTPStatus
from urllib.parse import urljoin

from compliance_api.models.restorative_justice import RestorativeJustice, RestorativeJusticeStatusEnum
from tests.utilities.factory_scenario.restorative_justice_scenario import RestorativeJusticeScenario


API_BASE_URL = "/api/restorative-justices/"


def test_get_restorative_justices(
    client, auth_header_super_user, created_inspection, created_restorative_justice
):
    """Test getting all restorative justices for an inspection."""
    url = f"{API_BASE_URL}?inspection_id={created_inspection.id}"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert len(result.json) == 1
    assert isinstance(result.json, list)


def test_get_restorative_justices_without_inspection_id(client, auth_header_super_user):
    """Test getting restorative justices without inspection_id parameter."""
    url = API_BASE_URL
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_get_restorative_justices_with_invalid_inspection_id(
    client, auth_header_super_user
):
    """Test getting restorative justices with invalid inspection ID."""
    url = f"{API_BASE_URL}?inspection_id=9999"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert result.json == []


def test_get_restorative_justice_by_id(
    client, auth_header_super_user, created_restorative_justice
):
    """Test getting a restorative justice by ID."""
    url = urljoin(API_BASE_URL, str(created_restorative_justice.id))
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert result.json["id"] == created_restorative_justice.id


def test_get_restorative_justice_by_invalid_id(client, auth_header_super_user):
    """Test getting a restorative justice with invalid ID."""
    url = urljoin(API_BASE_URL, "9999")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_get_restorative_justice_by_number(
    client, auth_header_super_user, created_restorative_justice
):
    """Test getting a restorative justice by number."""
    url = urljoin(
        API_BASE_URL,
        f"by-number/{created_restorative_justice.restorative_justice_number}",
    )
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert (
        result.json["restorative_justice_number"]
        == created_restorative_justice.restorative_justice_number
    )


def test_get_restorative_justice_by_invalid_number(client, auth_header_super_user):
    """Test getting a restorative justice with invalid number."""
    url = urljoin(API_BASE_URL, "by-number/INVALID-NUMBER")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_create_restorative_justice_success(
    client,
    auth_header_super_user,
    created_inspection,
    created_restorative_justice_inspection_requirement,
):
    """Test successfully creating a restorative justice."""
    url = API_BASE_URL
    rj_data = copy.copy(RestorativeJusticeScenario.default_value.value)
    rj_data["inspection_id"] = created_inspection.id
    rj_data["inspection_requirement_ids"] = [
        created_restorative_justice_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(rj_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["inspection_id"] == created_inspection.id
    assert "restorative_justice_number" in result.json
    # Should be OPEN status because it has restitution_details
    assert result.json["status"]["id"] == RestorativeJusticeStatusEnum.OPEN.name


def test_create_restorative_justice_drafting_status(
    client,
    auth_header_super_user,
    created_inspection,
    created_restorative_justice_inspection_requirement,
):
    """Test creating a restorative justice with DRAFTING status (no details)."""
    url = API_BASE_URL
    rj_data = copy.copy(RestorativeJusticeScenario.drafting_value.value)
    rj_data["inspection_id"] = created_inspection.id
    rj_data["inspection_requirement_ids"] = [
        created_restorative_justice_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(rj_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["status"]["id"] == RestorativeJusticeStatusEnum.DRAFTING.name


def test_create_restorative_justice_closed_status(
    client,
    auth_header_super_user,
    created_inspection,
    created_restorative_justice_inspection_requirement,
):
    """Test creating a restorative justice with CLOSED status (has completion date)."""
    url = API_BASE_URL
    rj_data = copy.copy(RestorativeJusticeScenario.closed_value.value)
    rj_data["inspection_id"] = created_inspection.id
    rj_data["inspection_requirement_ids"] = [
        created_restorative_justice_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(rj_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["status"]["id"] == RestorativeJusticeStatusEnum.CLOSED.name


def test_create_restorative_justice_with_custom_number(
    client,
    auth_header_super_user,
    created_inspection,
    created_restorative_justice_inspection_requirement,
):
    """Test creating a restorative justice with custom number."""
    url = API_BASE_URL
    rj_data = copy.copy(RestorativeJusticeScenario.custom_number_value.value)
    rj_data["inspection_id"] = created_inspection.id
    rj_data["inspection_requirement_ids"] = [
        created_restorative_justice_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(rj_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert (
        result.json["restorative_justice_number"]
        == rj_data["restorative_justice_number"]
    )


def test_create_restorative_justice_without_inspection_id(
    client, auth_header_super_user
):
    """Test creating restorative justice without inspection_id."""
    url = API_BASE_URL
    rj_data = copy.copy(RestorativeJusticeScenario.default_value.value)
    rj_data.pop("inspection_id")

    result = client.post(
        url,
        data=json.dumps(rj_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_create_restorative_justice_with_invalid_inspection_id(
    client, auth_header_super_user
):
    """Test creating restorative justice with invalid inspection ID."""
    url = API_BASE_URL
    rj_data = copy.copy(RestorativeJusticeScenario.default_value.value)
    rj_data["inspection_id"] = 9999

    result = client.post(
        url,
        data=json.dumps(rj_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_create_restorative_justice_with_duplicate_requirements(
    client,
    auth_header_super_user,
    created_inspection,
    created_restorative_justice_inspection_requirement,
    created_restorative_justice,
    session,
):
    """Test creating restorative justice with requirements that are already used."""
    # The created_restorative_justice fixture already uses the
    # created_restorative_justice_inspection_requirement
    # Now try to create a new restorative justice with the same requirement (should fail)
    url = API_BASE_URL
    rj_data = copy.copy(RestorativeJusticeScenario.default_value.value)
    rj_data["inspection_id"] = created_inspection.id
    rj_data["inspection_requirement_ids"] = [
        created_restorative_justice_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(rj_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_update_restorative_justice_success(
    client,
    auth_header_super_user,
    created_restorative_justice,
    created_restorative_justice_inspection_requirement,
    session,
):
    """Test successfully updating an existing restorative justice."""
    url = urljoin(API_BASE_URL, str(created_restorative_justice.id))
    update_data = {
        "inspection_id": created_restorative_justice.inspection_id,
        "restitution_details": "Updated restitution details",
        "inspection_requirement_ids": [
            created_restorative_justice_inspection_requirement.id
        ],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["restitution_details"] == "Updated restitution details"


def test_update_restorative_justice_status_transition(
    client,
    auth_header_super_user,
    created_restorative_justice_drafting,
):
    """Test updating restorative justice status from DRAFTING to OPEN to CLOSED."""
    url = urljoin(API_BASE_URL, str(created_restorative_justice_drafting.id))

    # First update: DRAFTING -> OPEN (add restitution details)
    update_data = {
        "inspection_id": created_restorative_justice_drafting.inspection_id,
        "restitution_details": "Work has begun",
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["status"]["id"] == RestorativeJusticeStatusEnum.OPEN.name

    # Second update: OPEN -> CLOSED (add completion date)
    update_data = {
        "inspection_id": created_restorative_justice_drafting.inspection_id,
        "restitution_details": "All work completed",
        "date_restitution_complete": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
    }

    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["status"]["id"] == RestorativeJusticeStatusEnum.CLOSED.name


def test_update_restorative_justice_with_invalid_id(
    client, auth_header_super_user, created_inspection
):
    """Test updating non-existent restorative justice."""
    url = urljoin(API_BASE_URL, "9999")
    update_data = {
        "inspection_id": created_inspection.id,
        "restitution_details": "Updated details",
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_update_restorative_justice_partial_data(
    client,
    auth_header_super_user,
    created_restorative_justice,
):
    """Test updating restorative justice with partial data."""
    url = urljoin(API_BASE_URL, str(created_restorative_justice.id))
    update_data = {
        "inspection_id": created_restorative_justice.inspection_id,
        "restitution_details": "Partially updated details only",
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["restitution_details"] == "Partially updated details only"


def test_delete_restorative_justice_success(
    client, auth_header_super_user, created_restorative_justice_drafting, session
):
    """Test deleting a restorative justice in DRAFTING status."""
    url = urljoin(API_BASE_URL, str(created_restorative_justice_drafting.id))
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NO_CONTENT

    # Verify deletion
    deleted_rj = RestorativeJustice.find_by_id(created_restorative_justice_drafting.id)
    assert deleted_rj is None or deleted_rj.is_deleted


def test_delete_restorative_justice_closed_status(
    client, auth_header_super_user, created_restorative_justice_closed
):
    """Test deleting a restorative justice in CLOSED status (should fail)."""
    url = urljoin(API_BASE_URL, str(created_restorative_justice_closed.id))
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_delete_restorative_justice_with_invalid_id(client, auth_header_super_user):
    """Test deleting non-existent restorative justice."""
    url = urljoin(API_BASE_URL, "9999")
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


# Permission Tests
def test_get_restorative_justices_unauthorized(client, created_inspection):
    """Test getting restorative justices without authentication."""
    url = f"{API_BASE_URL}?inspection_id={created_inspection.id}"
    result = client.get(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_create_restorative_justice_unauthorized(client):
    """Test creating restorative justice without authentication."""
    url = API_BASE_URL
    rj_data = copy.copy(RestorativeJusticeScenario.default_value.value)

    result = client.post(
        url,
        data=json.dumps(rj_data),
    )
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_update_restorative_justice_unauthorized(client, created_restorative_justice):
    """Test updating restorative justice without authentication."""
    url = urljoin(API_BASE_URL, str(created_restorative_justice.id))
    update_data = {
        "inspection_id": created_restorative_justice.inspection_id,
        "restitution_details": "Updated details",
    }

    headers = {"Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_delete_restorative_justice_unauthorized(client, created_restorative_justice):
    """Test deleting restorative justice without authentication."""
    url = urljoin(API_BASE_URL, str(created_restorative_justice.id))
    result = client.delete(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_get_restorative_justice_by_id_unauthorized(
    client, created_restorative_justice
):
    """Test getting restorative justice by ID without authentication."""
    url = urljoin(API_BASE_URL, str(created_restorative_justice.id))
    result = client.get(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_get_restorative_justice_by_number_unauthorized(
    client, created_restorative_justice
):
    """Test getting restorative justice by number without authentication."""
    url = urljoin(
        API_BASE_URL,
        f"by-number/{created_restorative_justice.restorative_justice_number}",
    )
    result = client.get(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


# Edge Cases and Business Logic Tests
def test_create_restorative_justice_with_null_values(
    client, auth_header_super_user, created_inspection
):
    """Test creating restorative justice with null values for optional fields."""
    url = API_BASE_URL
    rj_data = copy.copy(RestorativeJusticeScenario.minimal_value.value)
    rj_data["inspection_id"] = created_inspection.id
    rj_data["restitution_details"] = None
    rj_data["date_restitution_complete"] = None

    result = client.post(
        url,
        data=json.dumps(rj_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["status"]["id"] == RestorativeJusticeStatusEnum.DRAFTING.name


def test_restorative_justice_number_auto_generation(
    client,
    auth_header_super_user,
    created_inspection,
    created_restorative_justice_inspection_requirement,
):
    """Test that restorative justice number is auto-generated when not provided."""
    url = API_BASE_URL
    rj_data = copy.copy(RestorativeJusticeScenario.default_value.value)
    rj_data["inspection_id"] = created_inspection.id
    rj_data["inspection_requirement_ids"] = [
        created_restorative_justice_inspection_requirement.id
    ]
    # Don't provide restorative_justice_number

    result = client.post(
        url,
        data=json.dumps(rj_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert "restorative_justice_number" in result.json
    assert result.json["restorative_justice_number"] is not None
    assert len(result.json["restorative_justice_number"]) > 0


def test_create_multiple_restorative_justices_same_inspection(
    client,
    auth_header_super_user,
    created_inspection,
    mocker,
):
    """Test creating multiple restorative justices for the same inspection with different requirements."""
    from compliance_api.services.inspection_requirement import InspectionRequirementService
    from tests.utilities.factory_scenario.inspection_requirement_scenario import InspectionRequirementScenario

    # Mock auth
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    access_check_fn = mocker.patch(
        "compliance_api.services.service_utils.ServiceUtils.access_check_update_for_inspection"
    )
    access_check_fn.return_value = True
    inspection_status_check = mocker.patch(
        "compliance_api.services.service_utils.ServiceUtils.inspection_status_check"
    )
    inspection_status_check.return_value = True

    # Create two different requirements
    requirement_data_1 = copy.copy(InspectionRequirementScenario.default_value.value)
    requirement_data_1["enforcement_action_ids"] = [12]  # Restorative Justice
    requirement_1 = InspectionRequirementService.create(
        created_inspection.id, requirement_data_1
    )

    requirement_data_2 = copy.copy(InspectionRequirementScenario.default_value.value)
    requirement_data_2["enforcement_action_ids"] = [12]  # Restorative Justice
    requirement_2 = InspectionRequirementService.create(
        created_inspection.id, requirement_data_2
    )

    url = API_BASE_URL

    # Create first restorative justice
    rj_data_1 = copy.copy(RestorativeJusticeScenario.default_value.value)
    rj_data_1["inspection_id"] = created_inspection.id
    rj_data_1["inspection_requirement_ids"] = [requirement_1.id]

    result_1 = client.post(
        url,
        data=json.dumps(rj_data_1),
        headers=auth_header_super_user,
    )
    assert result_1.status_code == HTTPStatus.CREATED

    # Create second restorative justice
    rj_data_2 = copy.copy(RestorativeJusticeScenario.default_value.value)
    rj_data_2["inspection_id"] = created_inspection.id
    rj_data_2["inspection_requirement_ids"] = [requirement_2.id]
    rj_data_2["restitution_details"] = "Different restitution details"

    result_2 = client.post(
        url,
        data=json.dumps(rj_data_2),
        headers=auth_header_super_user,
    )
    assert result_2.status_code == HTTPStatus.CREATED

    # Verify both were created successfully
    assert result_1.json["id"] != result_2.json["id"]
    assert (
        result_1.json["restorative_justice_number"]
        != result_2.json["restorative_justice_number"]
    )


def test_update_restorative_justice_with_empty_requirements(
    client,
    auth_header_super_user,
    created_restorative_justice,
):
    """Test updating restorative justice with empty requirement list."""
    url = urljoin(API_BASE_URL, str(created_restorative_justice.id))
    update_data = {
        "inspection_id": created_restorative_justice.inspection_id,
        "restitution_details": "Updated with no requirements",
        "inspection_requirement_ids": [],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["restitution_details"] == "Updated with no requirements"
