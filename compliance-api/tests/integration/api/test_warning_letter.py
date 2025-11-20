"""Test suite for warning letters."""

import copy
import json
import random
from datetime import datetime, timezone
from http import HTTPStatus
from urllib.parse import urljoin

from compliance_api.models import db
from compliance_api.models.warning_letter import WarningLetter, WarningLetterProgressEnum, WarningLetterStatusEnum
from tests.utilities.factory_scenario.warning_letter_scenario import WarningLetterScenario


API_BASE_URL = "/api/warning-letters/"


def test_get_warning_letters(
    client, auth_header_super_user, created_inspection, created_warning_letter
):
    """Test getting all warning letters for an inspection."""
    url = f"{API_BASE_URL}?inspection_id={created_inspection.id}"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert len(result.json) == 1
    assert isinstance(result.json, list)


def test_get_warning_letters_without_inspection_id(client, auth_header_super_user):
    """Test getting warning letters without inspection_id parameter."""
    url = API_BASE_URL
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert isinstance(result.json, list)


def test_get_warning_letters_with_invalid_inspection_id(client, auth_header_super_user):
    """Test getting warning letters with invalid inspection ID."""
    url = f"{API_BASE_URL}?inspection_id=9999"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert result.json == []


def test_get_warning_letter_by_id(
    client, auth_header_super_user, created_warning_letter
):
    """Test getting a warning letter by ID."""
    url = urljoin(API_BASE_URL, str(created_warning_letter.id))
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert result.json["id"] == created_warning_letter.id


def test_get_warning_letter_by_invalid_id(client, auth_header_super_user):
    """Test getting a warning letter with invalid ID."""
    url = urljoin(API_BASE_URL, "9999")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_get_warning_letter_by_warning_letter_number(
    client, auth_header_super_user, created_warning_letter
):
    """Test getting a warning letter by warning letter number."""
    url = urljoin(
        API_BASE_URL,
        f"warning-letter-numbers/{created_warning_letter.warning_letter_number}",
    )
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert (
        result.json["warning_letter_number"]
        == created_warning_letter.warning_letter_number
    )


def test_get_warning_letter_by_invalid_warning_letter_number(
    client, auth_header_super_user
):
    """Test getting a warning letter with invalid warning letter number."""
    url = urljoin(API_BASE_URL, "warning-letter-numbers/INVALID-WL-NUMBER")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_create_warning_letter_success(
    client,
    auth_header_super_user,
    created_inspection,
    created_warning_letter_inspection_requirement,
):
    """Test successfully creating a warning letter."""
    url = API_BASE_URL
    wl_data = copy.copy(WarningLetterScenario.default_value.value)
    wl_data["inspection_id"] = created_inspection.id
    wl_data["warning_letter_number"] = (
        f"WL-TEST-SUCCESS-{random.randint(100000, 999999)}"
    )
    wl_data["inspection_requirement_ids"] = [
        created_warning_letter_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(wl_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["inspection_id"] == created_inspection.id
    assert "warning_letter_number" in result.json
    assert result.json["warning_letter_number"] == wl_data["warning_letter_number"]


def test_create_warning_letter_with_content(
    client,
    auth_header_super_user,
    created_inspection,
    created_warning_letter_inspection_requirement,
):
    """Test creating a warning letter with specific content."""
    url = API_BASE_URL
    wl_data = copy.copy(WarningLetterScenario.with_content_value.value)
    wl_data["inspection_id"] = created_inspection.id
    wl_data["issuing_officer_id"] = (
        created_inspection.primary_officer_id
    )  # Use valid officer
    wl_data["warning_letter_number"] = (
        f"WL-TEST-CONTENT-{random.randint(100000, 999999)}"
    )
    wl_data["inspection_requirement_ids"] = [
        created_warning_letter_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(wl_data, default=str),
        headers=auth_header_super_user,
    )
    print(result.json)
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["content"] == wl_data["content"]


def test_create_warning_letter_with_officer(
    client,
    auth_header_super_user,
    created_inspection,
    created_warning_letter_inspection_requirement,
    created_staff,
):
    """Test creating a warning letter with specific issuing officer."""
    url = API_BASE_URL
    wl_data = copy.copy(WarningLetterScenario.with_officer_value.value)
    wl_data["inspection_id"] = created_inspection.id
    wl_data["warning_letter_number"] = (
        f"WL-TEST-OFFICER-{random.randint(100000, 999999)}"
    )
    wl_data["issuing_officer_id"] = created_staff.id
    wl_data["inspection_requirement_ids"] = [
        created_warning_letter_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(wl_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["issuing_officer"]["id"] == created_staff.id


def test_create_warning_letter_auto_number(
    client,
    auth_header_super_user,
    created_inspection,
    created_warning_letter_inspection_requirement,
):
    """Test creating a warning letter with auto-generated number."""
    url = API_BASE_URL
    wl_data = copy.copy(WarningLetterScenario.auto_number_value.value)
    wl_data["inspection_id"] = created_inspection.id
    wl_data["issuing_officer_id"] = (
        created_inspection.primary_officer_id
    )  # Use valid officer
    wl_data["inspection_requirement_ids"] = [
        created_warning_letter_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(wl_data),
        headers=auth_header_super_user,
    )
    print(result.json)
    assert result.status_code == HTTPStatus.CREATED
    assert "warning_letter_number" in result.json
    assert result.json["warning_letter_number"] is not None


def test_create_warning_letter_without_inspection_id(client, auth_header_super_user):
    """Test creating warning letter without inspection_id."""
    url = API_BASE_URL
    wl_data = copy.copy(WarningLetterScenario.default_value.value)
    wl_data.pop("inspection_id")

    result = client.post(
        url,
        data=json.dumps(wl_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_create_warning_letter_without_requirements(
    client, auth_header_super_user, created_inspection
):
    """Test creating warning letter without inspection requirements."""
    url = API_BASE_URL
    wl_data = copy.copy(WarningLetterScenario.minimal_value.value)
    wl_data["inspection_id"] = created_inspection.id

    result = client.post(
        url,
        data=json.dumps(wl_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_warning_letter_with_duplicate_requirements(
    client,
    auth_header_super_user,
    created_inspection,
    created_warning_letter_inspection_requirement,
    created_warning_letter,
):
    """Test creating warning letter with requirements that are already used."""
    url = API_BASE_URL
    wl_data = copy.copy(WarningLetterScenario.default_value.value)
    wl_data["inspection_id"] = created_inspection.id
    wl_data["warning_letter_number"] = (
        f"WL-TEST-DUPLICATE-{random.randint(100000, 999999)}"
    )
    wl_data["inspection_requirement_ids"] = [
        created_warning_letter_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(wl_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED


def test_update_warning_letter_success(
    client,
    auth_header_super_user,
    created_warning_letter,
    created_warning_letter_inspection_requirement,
):
    """Test successfully updating an existing warning letter."""
    url = urljoin(API_BASE_URL, str(created_warning_letter.id))
    update_data = {
        "inspection_id": created_warning_letter.inspection_id,
        "issuing_officer_id": created_warning_letter.issuing_officer_id,
        "content": "Updated warning letter content for testing",
        "intended_issuance_date": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "inspection_requirement_ids": [
            created_warning_letter_inspection_requirement.id
        ],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["content"] == update_data["content"]


def test_update_warning_letter_content(
    client,
    auth_header_super_user,
    created_warning_letter_drafting,
    created_warning_letter_inspection_requirement,
):
    """Test updating warning letter content."""
    url = urljoin(API_BASE_URL, str(created_warning_letter_drafting.id))
    update_data = {
        "inspection_id": created_warning_letter_drafting.inspection_id,
        "issuing_officer_id": created_warning_letter_drafting.issuing_officer_id,  # Keep existing officer
        "content": "Updated content for warning letter testing purposes.",
        "inspection_requirement_ids": [
            created_warning_letter_inspection_requirement.id
        ],  # Keep existing requirement
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    print(result.json)
    assert result.status_code == HTTPStatus.OK
    assert result.json["content"] == update_data["content"]


def test_update_warning_letter_officer(
    client, auth_header_super_user, created_warning_letter_drafting, created_staff
):
    """Test updating warning letter issuing officer."""
    url = urljoin(API_BASE_URL, str(created_warning_letter_drafting.id))
    update_data = {
        "inspection_id": created_warning_letter_drafting.inspection_id,
        "issuing_officer_id": created_staff.id,
        "inspection_requirement_ids": [],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["issuing_officer"]["id"] == created_staff.id


def test_update_warning_letter_with_invalid_id(
    client, auth_header_super_user, created_inspection
):
    """Test updating non-existent warning letter."""
    url = urljoin(API_BASE_URL, "9999")
    update_data = {
        "inspection_id": created_inspection.id,
        "content": "Updated content",
        "inspection_requirement_ids": [],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_delete_warning_letter_success(
    client, auth_header_super_user, created_warning_letter_drafting
):
    """Test deleting a warning letter in DRAFTING status."""
    url = urljoin(API_BASE_URL, str(created_warning_letter_drafting.id))
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NO_CONTENT

    # Verify deletion
    deleted_wl = WarningLetter.find_by_id(created_warning_letter_drafting.id)
    assert deleted_wl is None or deleted_wl.is_deleted


def test_delete_warning_letter_issued_status_restriction(
    client, auth_header_super_user, created_warning_letter_issued
):
    """Test that ISSUED warning letters cannot be deleted."""
    url = urljoin(API_BASE_URL, str(created_warning_letter_issued.id))
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_delete_warning_letter_with_invalid_id(client, auth_header_super_user):
    """Test deleting non-existent warning letter."""
    url = urljoin(API_BASE_URL, "9999")
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_issue_warning_letter_success(
    client, auth_header_super_user, created_warning_letter_approved
):
    """Test issuing a warning letter."""
    url = urljoin(API_BASE_URL, f"{created_warning_letter_approved.id}/issue")
    issue_data = {
        "date_issued": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(issue_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.NO_CONTENT


def test_reset_warning_letter_content(
    client, auth_header_super_user, created_warning_letter_drafting
):
    """Test resetting warning letter content."""
    url = urljoin(API_BASE_URL, f"{created_warning_letter_drafting.id}/reset")
    reset_data = {"field_name": "content"}

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(reset_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert "content" in result.json


def test_render_warning_letter_html(
    client,
    auth_header_super_user,
    created_warning_letter_with_content,
    mock_doc_gen_service,
):
    """Test rendering warning letter as HTML."""
    url = urljoin(API_BASE_URL, f"{created_warning_letter_with_content.id}/render")
    render_data = {"output_format": "html"}

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.post(
        url,
        data=json.dumps(render_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK


# Permission Tests
def test_get_warning_letters_unauthorized(client, created_inspection):
    """Test getting warning letters without authentication."""
    url = f"{API_BASE_URL}?inspection_id={created_inspection.id}"
    result = client.get(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_create_warning_letter_unauthorized(client):
    """Test creating warning letter without authentication."""
    url = API_BASE_URL
    wl_data = copy.copy(WarningLetterScenario.default_value.value)

    result = client.post(url, data=json.dumps(wl_data))
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_update_warning_letter_unauthorized(client, created_warning_letter):
    """Test updating warning letter without authentication."""
    url = urljoin(API_BASE_URL, str(created_warning_letter.id))
    update_data = {
        "inspection_id": created_warning_letter.inspection_id,
        "content": "Updated content",
        "inspection_requirement_ids": [],
    }

    headers = {"Content-Type": "application/json"}
    result = client.patch(url, data=json.dumps(update_data), headers=headers)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_delete_warning_letter_unauthorized(client, created_warning_letter):
    """Test deleting warning letter without authentication."""
    url = urljoin(API_BASE_URL, str(created_warning_letter.id))
    result = client.delete(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_get_warning_letter_by_id_unauthorized(client, created_warning_letter):
    """Test getting warning letter by ID without authentication."""
    url = urljoin(API_BASE_URL, str(created_warning_letter.id))
    result = client.get(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_get_warning_letter_by_warning_letter_number_unauthorized(
    client, created_warning_letter
):
    """Test getting warning letter by warning letter number without authentication."""
    print(created_warning_letter.warning_letter_number)
    url = urljoin(
        API_BASE_URL,
        f"warning-letter-numbers/{created_warning_letter.warning_letter_number}",
    )
    print(url)
    result = client.get(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


# Edge Cases and Business Logic Tests
def test_warning_letter_number_generation(
    client,
    auth_header_super_user,
    created_inspection,
    created_warning_letter_inspection_requirement,
):
    """Test that warning letter number is auto-generated."""
    url = API_BASE_URL
    wl_data = copy.copy(WarningLetterScenario.auto_number_value.value)
    wl_data["inspection_id"] = created_inspection.id
    wl_data["issuing_officer_id"] = (
        created_inspection.primary_officer_id
    )  # Use valid officer
    wl_data["inspection_requirement_ids"] = [
        created_warning_letter_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(wl_data),
        headers=auth_header_super_user,
    )
    print(result.json)
    assert result.status_code == HTTPStatus.CREATED
    assert "warning_letter_number" in result.json
    assert result.json["warning_letter_number"] is not None
    assert len(result.json["warning_letter_number"]) > 0


def test_warning_letter_enum_transformations(
    client, auth_header_super_user, created_warning_letter_issued
):
    """Test that enum values are properly transformed in API responses."""
    url = urljoin(API_BASE_URL, str(created_warning_letter_issued.id))
    result = client.get(url, headers=auth_header_super_user)

    assert result.status_code == HTTPStatus.OK
    assert "status" in result.json
    assert "id" in result.json["status"]
    assert "name" in result.json["status"]
    assert result.json["status"]["id"] == WarningLetterStatusEnum.ISSUED.name
    assert result.json["status"]["name"] == WarningLetterStatusEnum.ISSUED.value

    assert "progress" in result.json
    assert "id" in result.json["progress"]
    assert "name" in result.json["progress"]
    assert result.json["progress"]["id"] == WarningLetterProgressEnum.ISSUED.name
    assert result.json["progress"]["name"] == WarningLetterProgressEnum.ISSUED.value


def test_create_multiple_warning_letters_same_inspection(
    client, auth_header_super_user, created_inspection, mocker
):
    """Test creating multiple warning letters for the same inspection with different requirements."""
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

    # Create two different requirements directly in database to avoid session isolation issues
    from compliance_api.models import (
        InspectionReqEnforcementMap, InspectionReqSourceDetail, InspectionRequirement, InspectionRequirementTypeEnum)

    # Create first requirement directly
    requirement_1 = InspectionRequirement(
        inspection_id=created_inspection.id,
        topic_id=1,  # Default topic
        compliance_finding_id=1,  # Default compliance finding
        summary="Test requirement 1",
        findings="Test findings 1",
        req_type=InspectionRequirementTypeEnum.REQ,
        sort_order=1,
        is_active=True,
        is_deleted=False,
    )
    db.session.add(requirement_1)
    db.session.flush()  # Get ID

    # Add enforcement action mapping for Warning Letter (ID 4)
    enf_map_1 = InspectionReqEnforcementMap(
        requirement_id=requirement_1.id,
        enforcement_action_id=4,  # WARNING_LETTER
    )
    db.session.add(enf_map_1)

    # Create second requirement directly
    requirement_2 = InspectionRequirement(
        inspection_id=created_inspection.id,
        topic_id=1,  # Default topic
        compliance_finding_id=1,  # Default compliance finding
        summary="Test requirement 2",
        findings="Test findings 2",
        req_type=InspectionRequirementTypeEnum.REQ,
        sort_order=2,
        is_active=True,
        is_deleted=False,
    )
    db.session.add(requirement_2)
    db.session.flush()  # Get ID

    # Add enforcement action mapping for Warning Letter (ID 4)
    enf_map_2 = InspectionReqEnforcementMap(
        requirement_id=requirement_2.id,
        enforcement_action_id=4,  # WARNING_LETTER
    )
    db.session.add(enf_map_2)

    # Add requirement source details to prevent "No requirement details found" error
    req_source_1 = InspectionReqSourceDetail(
        requirement_id=requirement_1.id,
        requirement_source_id=1,  # Default source
        section_number="1.1",
        is_active=True,
        is_deleted=False,
    )
    db.session.add(req_source_1)

    req_source_2 = InspectionReqSourceDetail(
        requirement_id=requirement_2.id,
        requirement_source_id=1,  # Default source
        section_number="1.2",
        is_active=True,
        is_deleted=False,
    )
    db.session.add(req_source_2)

    db.session.commit()  # Commit all requirements and mappings

    url = API_BASE_URL

    # Create first warning letter
    wl_data_1 = copy.copy(WarningLetterScenario.default_value.value)
    wl_data_1["inspection_id"] = created_inspection.id
    wl_data_1["warning_letter_number"] = (
        f"WL-TEST-MULTI-{random.randint(100000, 999999)}"
    )
    wl_data_1["inspection_requirement_ids"] = [requirement_1.id]

    result_1 = client.post(
        url,
        data=json.dumps(wl_data_1),
        headers=auth_header_super_user,
    )
    print("result_1", result_1.json)
    assert result_1.status_code == HTTPStatus.CREATED

    # Create second warning letter
    wl_data_2 = copy.copy(WarningLetterScenario.default_value.value)
    wl_data_2["inspection_id"] = created_inspection.id
    wl_data_2["warning_letter_number"] = (
        f"WL-TEST-MULTI2-{random.randint(100000, 999999)}"
    )
    wl_data_2["inspection_requirement_ids"] = [requirement_2.id]

    result_2 = client.post(
        url,
        data=json.dumps(wl_data_2),
        headers=auth_header_super_user,
    )
    print("result_2", result_2.json)
    assert result_2.status_code == HTTPStatus.CREATED

    # Verify both were created successfully
    assert result_1.json["id"] != result_2.json["id"]
    assert (
        result_1.json["warning_letter_number"] != result_2.json["warning_letter_number"]
    )
