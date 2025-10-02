"""Test suite for charge recommendations."""

import copy
import json
from datetime import datetime, timezone
from http import HTTPStatus
from urllib.parse import urljoin

from compliance_api.models.charge_recommendation import (
    ChargeDecisionEnum, ChargeRecommendation, ChargeRecommendationStatusEnum, JudgmentEnum)
from tests.utilities.factory_scenario.charge_recommendation_scenario import ChargeRecommendationScenario


API_BASE_URL = "/api/charge-recommendations/"


def test_get_charge_recommendations(
    client, auth_header_super_user, created_inspection, created_charge_recommendation
):
    """Test getting all charge recommendations for an inspection."""
    url = f"{API_BASE_URL}?inspection_id={created_inspection.id}"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert len(result.json) == 1
    assert isinstance(result.json, list)


def test_get_charge_recommendations_without_inspection_id(
    client, auth_header_super_user
):
    """Test getting charge recommendations without inspection_id parameter."""
    url = API_BASE_URL
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_get_charge_recommendations_with_invalid_inspection_id(
    client, auth_header_super_user
):
    """Test getting charge recommendations with invalid inspection ID."""
    url = f"{API_BASE_URL}?inspection_id=9999"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert result.json == []


def test_get_charge_recommendation_by_id(
    client, auth_header_super_user, created_charge_recommendation
):
    """Test getting a charge recommendation by ID."""
    url = urljoin(API_BASE_URL, str(created_charge_recommendation.id))
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert result.json["id"] == created_charge_recommendation.id


def test_get_charge_recommendation_by_invalid_id(client, auth_header_super_user):
    """Test getting a charge recommendation with invalid ID."""
    url = urljoin(API_BASE_URL, "9999")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_get_charge_recommendation_by_number(
    client, auth_header_super_user, created_charge_recommendation
):
    """Test getting a charge recommendation by number."""
    url = urljoin(
        API_BASE_URL,
        f"by-number/{created_charge_recommendation.charge_recommendation_number}",
    )
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert (
        result.json["charge_recommendation_number"]
        == created_charge_recommendation.charge_recommendation_number
    )


def test_get_charge_recommendation_by_invalid_number(client, auth_header_super_user):
    """Test getting a charge recommendation with invalid number."""
    url = urljoin(API_BASE_URL, "by-number/INVALID-NUMBER")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_create_charge_recommendation_success(
    client,
    auth_header_super_user,
    created_inspection,
    created_charge_recommendation_inspection_requirement,
):
    """Test successfully creating a charge recommendation."""
    url = API_BASE_URL
    cr_data = copy.copy(ChargeRecommendationScenario.default_value.value)
    cr_data["inspection_id"] = created_inspection.id
    cr_data["inspection_requirement_ids"] = [
        created_charge_recommendation_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(cr_data),
        headers=auth_header_super_user,
    )
    print(result.json)
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["inspection_id"] == created_inspection.id
    assert "charge_recommendation_number" in result.json
    assert result.json["status"]["id"] == ChargeRecommendationStatusEnum.DRAFTING.name


def test_create_charge_recommendation_deputy_review_status(
    client,
    auth_header_super_user,
    created_inspection,
    created_charge_recommendation_inspection_requirement,
):
    """Test creating a charge recommendation with DEPUTY_REVIEW status."""
    url = API_BASE_URL
    cr_data = copy.copy(ChargeRecommendationScenario.deputy_review_value.value)
    cr_data["inspection_id"] = created_inspection.id
    cr_data["inspection_requirement_ids"] = [
        created_charge_recommendation_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(cr_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert (
        result.json["status"]["id"] == ChargeRecommendationStatusEnum.DEPUTY_REVIEW.name
    )


def test_create_charge_recommendation_submitted_status(
    client,
    auth_header_super_user,
    created_inspection,
    created_charge_recommendation_inspection_requirement,
):
    """Test creating a charge recommendation with SUBMITTED_TO_CROWN_COUNSEL status."""
    url = API_BASE_URL
    cr_data = copy.copy(
        ChargeRecommendationScenario.submitted_to_crown_counsel_value.value
    )
    cr_data["inspection_id"] = created_inspection.id
    cr_data["inspection_requirement_ids"] = [
        created_charge_recommendation_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(cr_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert (
        result.json["status"]["id"]
        == ChargeRecommendationStatusEnum.SUBMITTED_TO_CROWN_COUNSEL.name
    )
    assert result.json["charge_decision"]["id"] == ChargeDecisionEnum.APPROVED.name


def test_create_charge_recommendation_not_proceeding_status(
    client,
    auth_header_super_user,
    created_inspection,
    created_charge_recommendation_inspection_requirement,
):
    """Test creating a charge recommendation with CEB_NOT_PROCEEDING status."""
    url = API_BASE_URL
    cr_data = copy.copy(ChargeRecommendationScenario.ceb_not_proceeding_value.value)
    cr_data["inspection_id"] = created_inspection.id
    cr_data["inspection_requirement_ids"] = [
        created_charge_recommendation_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(cr_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert (
        result.json["status"]["id"]
        == ChargeRecommendationStatusEnum.CEB_NOT_PROCEEDING.name
    )
    assert (
        result.json["charge_decision"]["id"] == ChargeDecisionEnum.NOT_PROCEEDING.name
    )


def test_create_charge_recommendation_with_court_details(
    client,
    auth_header_super_user,
    created_inspection,
    created_charge_recommendation_inspection_requirement,
):
    """Test creating a charge recommendation with complete court details."""
    url = API_BASE_URL
    cr_data = copy.copy(ChargeRecommendationScenario.with_court_details_value.value)
    cr_data["inspection_id"] = created_inspection.id
    cr_data["inspection_requirement_ids"] = [
        created_charge_recommendation_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(cr_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["court_file_number"] == "CF-2024-001"
    assert result.json["judgment"]["id"] == JudgmentEnum.GUILTY.name
    assert result.json["sentence_type"] == "Fine of $5000"


def test_create_charge_recommendation_with_custom_number(
    client,
    auth_header_super_user,
    created_inspection,
    created_charge_recommendation_inspection_requirement,
):
    """Test creating a charge recommendation with custom number."""
    url = API_BASE_URL
    cr_data = copy.copy(ChargeRecommendationScenario.custom_number_value.value)
    cr_data["inspection_id"] = created_inspection.id
    cr_data["inspection_requirement_ids"] = [
        created_charge_recommendation_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(cr_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert (
        result.json["charge_recommendation_number"]
        == cr_data["charge_recommendation_number"]
    )


def test_create_charge_recommendation_without_inspection_id(
    client, auth_header_super_user
):
    """Test creating charge recommendation without inspection_id."""
    url = API_BASE_URL
    cr_data = copy.copy(ChargeRecommendationScenario.default_value.value)
    cr_data.pop("inspection_id")

    result = client.post(
        url,
        data=json.dumps(cr_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_create_charge_recommendation_with_invalid_inspection_id(
    client, auth_header_super_user
):
    """Test creating charge recommendation with invalid inspection ID."""
    url = API_BASE_URL
    cr_data = copy.copy(ChargeRecommendationScenario.default_value.value)
    cr_data["inspection_id"] = 9999

    result = client.post(
        url,
        data=json.dumps(cr_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_create_charge_recommendation_with_duplicate_requirements(
    client,
    auth_header_super_user,
    created_inspection,
    created_charge_recommendation_inspection_requirement,
    created_charge_recommendation,
    session,
):
    """Test creating charge recommendation with requirements that are already used."""
    # The created_charge_recommendation fixture already uses the
    # created_charge_recommendation_inspection_requirement
    # Now try to create a new charge recommendation with the same requirement (should fail)
    url = API_BASE_URL
    cr_data = copy.copy(ChargeRecommendationScenario.default_value.value)
    cr_data["inspection_id"] = created_inspection.id
    cr_data["inspection_requirement_ids"] = [
        created_charge_recommendation_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(cr_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_update_charge_recommendation_success(
    client,
    auth_header_super_user,
    created_charge_recommendation,
    created_charge_recommendation_inspection_requirement,
    session,
):
    """Test successfully updating an existing charge recommendation."""
    url = urljoin(API_BASE_URL, str(created_charge_recommendation.id))
    update_data = {
        "inspection_id": created_charge_recommendation.inspection_id,
        "status": "DEPUTY_REVIEW",
        "date_to_crown_counsel": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "inspection_requirement_ids": [
            created_charge_recommendation_inspection_requirement.id
        ],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert (
        result.json["status"]["id"] == ChargeRecommendationStatusEnum.DEPUTY_REVIEW.name
    )


def test_update_charge_recommendation_status_transitions(
    client,
    auth_header_super_user,
    created_charge_recommendation_drafting,
):
    """Test updating charge recommendation through status transitions."""
    url = urljoin(API_BASE_URL, str(created_charge_recommendation_drafting.id))

    # First update: DRAFTING -> DEPUTY_REVIEW
    update_data = {
        "inspection_id": created_charge_recommendation_drafting.inspection_id,
        "status": "DEPUTY_REVIEW",
        "date_to_crown_counsel": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert (
        result.json["status"]["id"] == ChargeRecommendationStatusEnum.DEPUTY_REVIEW.name
    )

    # Second update: DEPUTY_REVIEW -> SUBMITTED_TO_CROWN_COUNSEL
    update_data = {
        "inspection_id": created_charge_recommendation_drafting.inspection_id,
        "status": "SUBMITTED_TO_CROWN_COUNSEL",
        "charge_decision": "APPROVED",
        "charge_decision_date": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
    }

    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert (
        result.json["status"]["id"]
        == ChargeRecommendationStatusEnum.SUBMITTED_TO_CROWN_COUNSEL.name
    )
    assert result.json["charge_decision"]["id"] == ChargeDecisionEnum.APPROVED.name


def test_update_charge_recommendation_with_court_details(
    client,
    auth_header_super_user,
    created_charge_recommendation_submitted,
):
    """Test updating charge recommendation with court details."""
    url = urljoin(API_BASE_URL, str(created_charge_recommendation_submitted.id))
    update_data = {
        "inspection_id": created_charge_recommendation_submitted.inspection_id,
        "court_file_number": "CF-2024-UPDATED",
        "court_appearances": "Updated court appearance details",
        "judgment": "GUILTY",
        "judgment_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "sentence_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "sentence_type": "Updated sentence type",
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["court_file_number"] == "CF-2024-UPDATED"
    assert result.json["judgment"]["id"] == JudgmentEnum.GUILTY.name


def test_update_charge_recommendation_with_invalid_id(
    client, auth_header_super_user, created_inspection
):
    """Test updating non-existent charge recommendation."""
    url = urljoin(API_BASE_URL, "9999")
    update_data = {
        "inspection_id": created_inspection.id,
        "status": "DEPUTY_REVIEW",
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_update_charge_recommendation_partial_data(
    client,
    auth_header_super_user,
    created_charge_recommendation,
):
    """Test updating charge recommendation with partial data."""
    url = urljoin(API_BASE_URL, str(created_charge_recommendation.id))
    update_data = {
        "inspection_id": created_charge_recommendation.inspection_id,
        "court_file_number": "CF-2024-PARTIAL",
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["court_file_number"] == "CF-2024-PARTIAL"


def test_delete_charge_recommendation_success(
    client, auth_header_super_user, created_charge_recommendation_drafting, session
):
    """Test deleting a charge recommendation."""
    url = urljoin(API_BASE_URL, str(created_charge_recommendation_drafting.id))
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NO_CONTENT

    # Verify deletion
    deleted_cr = ChargeRecommendation.find_by_id(
        created_charge_recommendation_drafting.id
    )
    assert deleted_cr is None or deleted_cr.is_deleted


def test_delete_charge_recommendation_with_invalid_id(client, auth_header_super_user):
    """Test deleting non-existent charge recommendation."""
    url = urljoin(API_BASE_URL, "9999")
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


# Permission Tests
def test_get_charge_recommendations_unauthorized(client, created_inspection):
    """Test getting charge recommendations without authentication."""
    url = f"{API_BASE_URL}?inspection_id={created_inspection.id}"
    result = client.get(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_create_charge_recommendation_unauthorized(client):
    """Test creating charge recommendation without authentication."""
    url = API_BASE_URL
    cr_data = copy.copy(ChargeRecommendationScenario.default_value.value)

    result = client.post(
        url,
        data=json.dumps(cr_data),
    )
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_update_charge_recommendation_unauthorized(
    client, created_charge_recommendation
):
    """Test updating charge recommendation without authentication."""
    url = urljoin(API_BASE_URL, str(created_charge_recommendation.id))
    update_data = {
        "inspection_id": created_charge_recommendation.inspection_id,
        "status": "DEPUTY_REVIEW",
    }

    headers = {"Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_delete_charge_recommendation_unauthorized(
    client, created_charge_recommendation
):
    """Test deleting charge recommendation without authentication."""
    url = urljoin(API_BASE_URL, str(created_charge_recommendation.id))
    result = client.delete(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_get_charge_recommendation_by_id_unauthorized(
    client, created_charge_recommendation
):
    """Test getting charge recommendation by ID without authentication."""
    url = urljoin(API_BASE_URL, str(created_charge_recommendation.id))
    result = client.get(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_get_charge_recommendation_by_number_unauthorized(
    client, created_charge_recommendation
):
    """Test getting charge recommendation by number without authentication."""
    url = urljoin(
        API_BASE_URL,
        f"by-number/{created_charge_recommendation.charge_recommendation_number}",
    )
    result = client.get(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


# Edge Cases and Business Logic Tests
def test_create_charge_recommendation_with_null_values(
    client, auth_header_super_user, created_inspection
):
    """Test creating charge recommendation with null values for optional fields."""
    url = API_BASE_URL
    cr_data = copy.copy(ChargeRecommendationScenario.minimal_value.value)
    cr_data["inspection_id"] = created_inspection.id
    cr_data["status"] = None
    cr_data["date_to_crown_counsel"] = None

    result = client.post(
        url,
        data=json.dumps(cr_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["status"]["id"] == ChargeRecommendationStatusEnum.DRAFTING.name


def test_charge_recommendation_number_auto_generation(
    client,
    auth_header_super_user,
    created_inspection,
    created_charge_recommendation_inspection_requirement,
):
    """Test that charge recommendation number is auto-generated when not provided."""
    url = API_BASE_URL
    cr_data = copy.copy(ChargeRecommendationScenario.default_value.value)
    cr_data["inspection_id"] = created_inspection.id
    cr_data["inspection_requirement_ids"] = [
        created_charge_recommendation_inspection_requirement.id
    ]
    # Don't provide charge_recommendation_number

    result = client.post(
        url,
        data=json.dumps(cr_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert "charge_recommendation_number" in result.json
    assert result.json["charge_recommendation_number"] is not None
    assert len(result.json["charge_recommendation_number"]) > 0


def test_create_multiple_charge_recommendations_same_inspection(
    client,
    auth_header_super_user,
    created_inspection,
    mocker,
):
    """Test creating multiple charge recommendations for the same inspection with different requirements."""
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
    requirement_data_1["enforcement_action_ids"] = [9]  # Charge Recommendation
    requirement_1 = InspectionRequirementService.create(
        created_inspection.id, requirement_data_1
    )

    requirement_data_2 = copy.copy(InspectionRequirementScenario.default_value.value)
    requirement_data_2["enforcement_action_ids"] = [9]  # Charge Recommendation
    requirement_2 = InspectionRequirementService.create(
        created_inspection.id, requirement_data_2
    )

    url = API_BASE_URL

    # Create first charge recommendation
    cr_data_1 = copy.copy(ChargeRecommendationScenario.default_value.value)
    cr_data_1["inspection_id"] = created_inspection.id
    cr_data_1["inspection_requirement_ids"] = [requirement_1.id]

    result_1 = client.post(
        url,
        data=json.dumps(cr_data_1),
        headers=auth_header_super_user,
    )
    assert result_1.status_code == HTTPStatus.CREATED

    # Create second charge recommendation
    cr_data_2 = copy.copy(ChargeRecommendationScenario.default_value.value)
    cr_data_2["inspection_id"] = created_inspection.id
    cr_data_2["inspection_requirement_ids"] = [requirement_2.id]
    cr_data_2["status"] = "DEPUTY_REVIEW"

    result_2 = client.post(
        url,
        data=json.dumps(cr_data_2),
        headers=auth_header_super_user,
    )
    assert result_2.status_code == HTTPStatus.CREATED

    # Verify both were created successfully
    assert result_1.json["id"] != result_2.json["id"]
    assert (
        result_1.json["charge_recommendation_number"]
        != result_2.json["charge_recommendation_number"]
    )


def test_update_charge_recommendation_with_empty_requirements(
    client,
    auth_header_super_user,
    created_charge_recommendation,
):
    """Test updating charge recommendation with empty requirement list."""
    url = urljoin(API_BASE_URL, str(created_charge_recommendation.id))
    update_data = {
        "inspection_id": created_charge_recommendation.inspection_id,
        "status": "DEPUTY_REVIEW",
        "inspection_requirement_ids": [],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert (
        result.json["status"]["id"] == ChargeRecommendationStatusEnum.DEPUTY_REVIEW.name
    )


def test_charge_recommendation_enum_transformations(
    client, auth_header_super_user, created_charge_recommendation_with_court_details
):
    """Test that enum values are properly transformed in API responses."""
    url = urljoin(
        API_BASE_URL, str(created_charge_recommendation_with_court_details.id)
    )
    result = client.get(url, headers=auth_header_super_user)

    assert result.status_code == HTTPStatus.OK

    # Check status enum transformation
    assert "status" in result.json
    assert "id" in result.json["status"]
    assert "name" in result.json["status"]

    # Check charge_decision enum transformation
    if result.json.get("charge_decision"):
        assert "id" in result.json["charge_decision"]
        assert "name" in result.json["charge_decision"]

    # Check judgment enum transformation
    if result.json.get("judgment"):
        assert "id" in result.json["judgment"]
        assert "name" in result.json["judgment"]
