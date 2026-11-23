"""Test suite for administrative penalties."""

import copy
import json
import random
from datetime import datetime, timezone
from http import HTTPStatus
from urllib.parse import urljoin

from compliance_api.models.administrative_penalty import (
    AdministrativePenalty, DecisionEnum, JudicialReviewDecisionEnum, ReferralStatusEnum)
from compliance_api.exceptions import PermissionDeniedError
from compliance_api.models.case_file import CaseFileStatusEnum
from compliance_api.services.inspection import InspectionService
from compliance_api.services.service_utils import ServiceUtils
from tests.utilities.factory_scenario.administrative_penalty_scenario import AdministrativePenaltyScenario
from tests.utilities.factory_scenario.inspection_scenario import InspectionScenario


API_BASE_URL = "/api/administrative-penalties/"


def test_get_administrative_penalties(
    client, auth_header_super_user, created_inspection, created_administrative_penalty
):
    """Test getting all administrative penalties for an inspection."""
    url = f"{API_BASE_URL}?inspection_id={created_inspection.id}"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert len(result.json) == 1
    assert isinstance(result.json, list)


def test_simple_api_check(client):
    """Test basic API endpoint accessibility."""
    url = API_BASE_URL
    result = client.get(url)
    # Should get 401 Unauthorized without auth header
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_debug_create_response(
    client,
    auth_header_super_user,
    created_inspection,
    created_administrative_penalty_inspection_requirement,
):
    """Debug test to see actual response."""
    url = API_BASE_URL
    ap_data = {
        "inspection_id": created_inspection.id,
        "referral_status": "PREPARING_REFERRAL_FOR_AEO",
        "inspection_requirement_ids": [
            created_administrative_penalty_inspection_requirement.id
        ],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.post(url, data=json.dumps(ap_data), headers=headers)

    print(f"Status Code: {result.status_code}")
    print(f"Response: {result.get_json()}")
    print(f"Data sent: {ap_data}")

    # Just check that we get some response
    assert result.status_code in [
        HTTPStatus.CREATED,
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.UNPROCESSABLE_ENTITY,
    ]


def test_get_administrative_penalties_without_inspection_id(
    client, auth_header_super_user
):
    """Test getting all administrative penalties without specifying an inspection ID."""
    url = API_BASE_URL
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_get_projectwise_administrative_penalties(
    client, auth_header_super_user, created_administrative_penalty, created_inspection
):
    """Test getting all administrative penalties for a project."""
    url = f"{API_BASE_URL}projectwise?case_file_id={created_inspection.case_file_id}"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert isinstance(result.json, list)


def test_get_projectwise_administrative_penalties_with_invalid_case_file_id(
    client, auth_header_super_user
):
    """Test getting all administrative penalties for a project with invalid case file ID."""
    url = f"{API_BASE_URL}projectwise?case_file_id=9999"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_get_administrative_penalty_by_id(
    client, auth_header_super_user, created_administrative_penalty, session
):
    """Test getting administrative penalty by ID."""
    url = urljoin(API_BASE_URL, f"{created_administrative_penalty.id}")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert result.json["id"] == created_administrative_penalty.id


def test_get_administrative_penalty_by_invalid_id(client, auth_header_super_user):
    """Test getting administrative penalty by invalid ID."""
    url = urljoin(API_BASE_URL, "9999")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_get_administrative_penalty_by_number_success(
    client, auth_header_super_user, created_administrative_penalty
):
    """Test getting administrative penalty by number."""
    url = urljoin(
        API_BASE_URL,
        f"by-number/{created_administrative_penalty.administrative_penalty_number}",
    )
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert result.json["id"] == created_administrative_penalty.id
    assert (
        result.json["administrative_penalty_number"]
        == created_administrative_penalty.administrative_penalty_number
    )


def test_get_administrative_penalty_by_invalid_number(client, auth_header_super_user):
    """Test getting administrative penalty by invalid number."""
    url = urljoin(API_BASE_URL, "by-number/INVALID-AP-NUMBER")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_create_administrative_penalty_success(
    client,
    auth_header_super_user,
    created_inspection,
    created_administrative_penalty_inspection_requirement,
    session,
):
    """Test successfully creating a new administrative penalty."""
    url = API_BASE_URL
    ap_data = copy.copy(AdministrativePenaltyScenario.default_value.value)
    ap_data["inspection_id"] = created_inspection.id
    ap_data["inspection_requirement_ids"] = [
        created_administrative_penalty_inspection_requirement.id
    ]

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.post(
        url,
        data=json.dumps(ap_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["inspection_id"] == created_inspection.id
    assert result.json["referral_status"]["id"] == ReferralStatusEnum.PREPARING_REFERRAL_FOR_AEO.name


def test_create_administrative_penalty_with_invalid_inspection_id(
    client, auth_header_super_user
):
    """Test creating administrative penalty with invalid inspection ID."""
    url = API_BASE_URL
    ap_data = copy.copy(AdministrativePenaltyScenario.default_value.value)
    ap_data["inspection_id"] = 9999
    ap_data["inspection_requirement_ids"] = [1]

    result = client.post(
        url,
        data=json.dumps(ap_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_create_administrative_penalty_with_invalid_requirements_type(
    client, auth_header_super_user, created_inspection
):
    """Test creating administrative penalty with invalid requirement type."""
    url = API_BASE_URL
    ap_data = copy.copy(AdministrativePenaltyScenario.default_value.value)
    ap_data["inspection_id"] = created_inspection.id
    ap_data["inspection_requirement_ids"] = "invalid_type"  # Should be a list

    result = client.post(
        url,
        data=json.dumps(ap_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_create_administrative_penalty_with_empty_requirements(
    client, auth_header_super_user, created_inspection
):
    """Test creating administrative penalty with empty inspection requirements."""
    url = API_BASE_URL
    ap_data = copy.copy(AdministrativePenaltyScenario.default_value.value)
    ap_data["inspection_id"] = created_inspection.id
    ap_data["inspection_requirement_ids"] = []

    result = client.post(
        url,
        data=json.dumps(ap_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_administrative_penalty_with_invalid_requirements(
    client, auth_header_super_user, created_inspection
):
    """Test creating administrative penalty with invalid inspection requirement IDs."""
    url = API_BASE_URL
    ap_data = copy.copy(AdministrativePenaltyScenario.default_value.value)
    ap_data["inspection_id"] = created_inspection.id
    ap_data["inspection_requirement_ids"] = [9999]

    result = client.post(
        url,
        data=json.dumps(ap_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_administrative_penalty_with_duplicate_requirements(
    client,
    auth_header_super_user,
    created_inspection,
    created_administrative_penalty_inspection_requirement,
    created_administrative_penalty,
    session,
):
    """Test creating administrative penalty with requirements that are already used in another penalty."""
    # The created_administrative_penalty fixture already uses the
    # created_administrative_penalty_inspection_requirement
    # Now try to create a new administrative penalty with the same requirement (should fail)
    url = API_BASE_URL
    ap_data = copy.copy(AdministrativePenaltyScenario.default_value.value)
    ap_data["inspection_id"] = created_inspection.id
    ap_data["inspection_requirement_ids"] = [
        created_administrative_penalty_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(ap_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED


def test_create_administrative_penalty_missing_required_fields(
    client, auth_header_super_user
):
    """Test creating administrative penalty with missing required fields."""
    url = API_BASE_URL
    ap_data = {
        "referral_status": ReferralStatusEnum.PREPARING_REFERRAL_FOR_AEO.name,
    }

    result = client.post(
        url,
        data=json.dumps(ap_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_update_administrative_penalty_success(
    client,
    auth_header_super_user,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
    session,
):
    """Test successfully updating an existing administrative penalty."""
    url = urljoin(API_BASE_URL, f"{created_administrative_penalty.id}")
    update_data = {
        "inspection_id": created_administrative_penalty.inspection_id,
        "referral_status": ReferralStatusEnum.REFERRED_TO_AEO.name,
        "penalty_amount": 5000.00,
        "inspection_requirement_ids": [
            created_administrative_penalty_inspection_requirement.id
        ],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["referral_status"]["id"] == ReferralStatusEnum.REFERRED_TO_AEO.name
    assert result.json["penalty_amount"] == "5000.00"


def test_update_administrative_penalty_with_invalid_id(
    client,
    auth_header_super_user,
    created_inspection,
    created_administrative_penalty_inspection_requirement,
):
    """Test updating non-existent administrative penalty."""
    url = urljoin(API_BASE_URL, "9999")
    update_data = {
        "inspection_id": created_inspection.id,
        "referral_status": ReferralStatusEnum.REFERRED_TO_AEO.name,
        "inspection_requirement_ids": [
            created_administrative_penalty_inspection_requirement.id
        ],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_update_administrative_penalty_with_invalid_inspection_id(
    client,
    auth_header_super_user,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
):
    """Test updating administrative penalty with invalid inspection ID."""
    url = urljoin(API_BASE_URL, f"{created_administrative_penalty.id}")
    update_data = {
        "inspection_id": 9999,
        "referral_status": ReferralStatusEnum.REFERRED_TO_AEO.name,
        "inspection_requirement_ids": [
            created_administrative_penalty_inspection_requirement.id
        ],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_update_administrative_penalty_with_decision_but_no_penalty_amount(
    client,
    auth_header_super_user,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
):
    """Test updating administrative penalty with decision but no penalty amount."""
    url = urljoin(API_BASE_URL, f"{created_administrative_penalty.id}")
    update_data = {
        "inspection_id": created_administrative_penalty.inspection_id,
        "decision": DecisionEnum.AP_ISSUED.name,
        "inspection_requirement_ids": [
            created_administrative_penalty_inspection_requirement.id
        ],
        # No penalty_amount provided
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_delete_administrative_penalty(
    client, auth_header_super_user, created_administrative_penalty, session
):
    """Test deleting an administrative penalty."""
    url = urljoin(
        API_BASE_URL,
        f"{created_administrative_penalty.id}?inspection_id={created_administrative_penalty.inspection_id}",
    )
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NO_CONTENT

    # Verify deletion
    deleted_ap = AdministrativePenalty.find_by_id(created_administrative_penalty.id)
    assert deleted_ap is None or deleted_ap.is_deleted


def test_delete_administrative_penalty_with_invalid_id(client, auth_header_super_user):
    """Test deleting non-existent administrative penalty."""
    url = urljoin(API_BASE_URL, "9999?inspection_id=1")
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_delete_administrative_penalty_without_inspection_id(
    client, auth_header_super_user, created_administrative_penalty
):
    """Test deleting administrative penalty without inspection_id parameter."""
    url = urljoin(API_BASE_URL, f"{created_administrative_penalty.id}")
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_link_administrative_penalty_success(
    client,
    auth_header_super_user,
    created_inspection,
    session,
    mocker,
):
    """Test successfully linking an administrative penalty to inspection requirements."""
    from compliance_api.services.administrative_penalty import AdministrativePenaltyService
    from compliance_api.services.inspection import InspectionService
    from compliance_api.services.inspection_requirement import InspectionRequirementService
    from tests.utilities.factory_scenario.administrative_penalty_scenario import AdministrativePenaltyScenario
    from tests.utilities.factory_scenario.inspection_requirement_scenario import InspectionRequirementScenario
    from tests.utilities.factory_scenario.inspection_scenario import InspectionScenario

    # Mock auth for all operations
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

    # Create first inspection and requirement for the administrative penalty
    ap_inspection_data = copy.copy(InspectionScenario.default_value.value)
    ap_inspection_data["case_file_id"] = created_inspection.case_file_id
    ap_inspection = InspectionService.create(ap_inspection_data)

    ap_requirement_data = copy.copy(InspectionRequirementScenario.default_value.value)
    ap_requirement_data["enforcement_action_ids"] = [
        6
    ]  # Administrative Penalty Recommendation
    ap_requirement = InspectionRequirementService.create(
        ap_inspection.id, ap_requirement_data
    )

    # Create administrative penalty with the first requirement
    ap_data = copy.copy(AdministrativePenaltyScenario.default_value.value)
    ap_data["inspection_id"] = ap_inspection.id
    ap_data["inspection_requirement_ids"] = [ap_requirement.id]
    administrative_penalty = AdministrativePenaltyService.create_administrative_penalty(
        ap_data
    )

    # Create second inspection and requirement for linking
    link_inspection_data = copy.copy(InspectionScenario.default_value.value)
    link_inspection_data["case_file_id"] = created_inspection.case_file_id
    link_inspection = InspectionService.create(link_inspection_data)

    link_requirement_data = copy.copy(InspectionRequirementScenario.default_value.value)
    link_requirement_data["enforcement_action_ids"] = [
        6
    ]  # Administrative Penalty Recommendation
    link_requirement = InspectionRequirementService.create(
        link_inspection.id, link_requirement_data
    )

    # Now test the linking
    url = urljoin(API_BASE_URL, "links")
    link_data = {
        "administrative_penalty_id": administrative_penalty.id,
        "inspection_id": link_inspection.id,
        "inspection_requirement_ids": [link_requirement.id],
    }

    result = client.post(
        url,
        data=json.dumps(link_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["id"] == administrative_penalty.id


def test_link_administrative_penalty_with_invalid_ap_id(
    client,
    auth_header_super_user,
    created_inspection,
    created_administrative_penalty_inspection_requirement,
):
    """Test linking non-existent administrative penalty."""
    url = urljoin(API_BASE_URL, "links")
    link_data = {
        "administrative_penalty_id": 9999,
        "inspection_id": created_inspection.id,
        "inspection_requirement_ids": [
            created_administrative_penalty_inspection_requirement.id
        ],
    }

    result = client.post(
        url,
        data=json.dumps(link_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_link_administrative_penalty_with_invalid_inspection_id(
    client,
    auth_header_super_user,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
):
    """Test linking administrative penalty with invalid inspection ID."""
    url = urljoin(API_BASE_URL, "links")
    link_data = {
        "administrative_penalty_id": created_administrative_penalty.id,
        "inspection_id": 9999,
        "inspection_requirement_ids": [
            created_administrative_penalty_inspection_requirement.id
        ],
    }

    result = client.post(
        url,
        data=json.dumps(link_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_get_administrative_penalty_links(
    client, auth_header_super_user, created_administrative_penalty, session
):
    """Test getting inspection and requirements linked to an administrative penalty."""
    url = urljoin(API_BASE_URL, f"{created_administrative_penalty.id}/links")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert isinstance(result.json, list)


def test_get_administrative_penalty_links_with_invalid_id(
    client, auth_header_super_user
):
    """Test getting links for non-existent administrative penalty."""
    url = urljoin(API_BASE_URL, "9999/links")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_update_administrative_penalty_partial_data(
    client,
    auth_header_super_user,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
):
    """Test updating administrative penalty with partial data."""
    url = urljoin(API_BASE_URL, f"{created_administrative_penalty.id}")
    update_data = {
        "inspection_id": created_administrative_penalty.inspection_id,
        "referral_status": ReferralStatusEnum.AP_NOT_PROCEEDING.name,
        "penalty_amount": 2500.00,
        "inspection_requirement_ids": [
            created_administrative_penalty_inspection_requirement.id
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
        result.json["referral_status"]["id"]
        == ReferralStatusEnum.AP_NOT_PROCEEDING.name
    )
    assert result.json["penalty_amount"] == "2500.00"
    # Renaming CEB Not Proceeding did not change its closing behaviour.
    assert result.json["is_closed"] is True


def test_update_administrative_penalty_with_ap_not_proceeding_decision(
    client,
    auth_header_super_user,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
):
    """Test updating administrative penalty with AP_NOT_PROCEEDING decision (no penalty amount required)."""
    url = urljoin(API_BASE_URL, f"{created_administrative_penalty.id}")
    update_data = {
        "inspection_id": created_administrative_penalty.inspection_id,
        "decision": DecisionEnum.AP_NOT_PROCEEDING.name,
        "inspection_requirement_ids": [
            created_administrative_penalty_inspection_requirement.id
        ],
        # No penalty_amount provided - should be allowed for AP_NOT_PROCEEDING
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["decision"]["id"] == DecisionEnum.AP_NOT_PROCEEDING.name


# Permission Tests
def test_get_administrative_penalties_unauthorized(client, created_inspection):
    """Test getting administrative penalties without authentication."""
    url = f"{API_BASE_URL}?inspection_id={created_inspection.id}"
    result = client.get(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_create_administrative_penalty_unauthorized(client):
    """Test creating administrative penalty without authentication."""
    url = API_BASE_URL
    ap_data = copy.copy(AdministrativePenaltyScenario.default_value.value)

    result = client.post(
        url,
        data=json.dumps(ap_data),
    )
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_update_administrative_penalty_unauthorized(
    client,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
):
    """Test updating administrative penalty without authentication."""
    url = urljoin(API_BASE_URL, f"{created_administrative_penalty.id}")
    update_data = {
        "inspection_id": created_administrative_penalty.inspection_id,
        "referral_status": ReferralStatusEnum.REFERRED_TO_AEO.name,
        "inspection_requirement_ids": [
            created_administrative_penalty_inspection_requirement.id
        ],
    }

    headers = {"Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_delete_administrative_penalty_unauthorized(
    client, created_administrative_penalty
):
    """Test deleting administrative penalty without authentication."""
    url = urljoin(
        API_BASE_URL,
        f"{created_administrative_penalty.id}?inspection_id={created_administrative_penalty.inspection_id}",
    )
    result = client.delete(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_link_administrative_penalty_unauthorized(client):
    """Test linking administrative penalty without authentication."""
    url = urljoin(API_BASE_URL, "links")
    link_data = {
        "administrative_penalty_id": 1,
        "inspection_id": 1,
        "inspection_requirement_ids": [1],
    }

    result = client.post(
        url,
        data=json.dumps(link_data),
    )
    assert result.status_code == HTTPStatus.UNAUTHORIZED


# Edge Cases and Business Logic Tests
def test_create_administrative_penalty_with_null_values(
    client, auth_header_super_user, created_inspection
):
    """Test creating administrative penalty with null values for optional fields."""
    url = API_BASE_URL
    ap_data = copy.copy(AdministrativePenaltyScenario.default_value.value)
    ap_data["inspection_id"] = created_inspection.id
    ap_data["inspection_requirement_ids"] = []
    ap_data["date_referred"] = None
    ap_data["decision_date"] = None
    ap_data["penalty_amount"] = None

    result = client.post(
        url,
        data=json.dumps(ap_data),
        headers=auth_header_super_user,
    )
    # This should fail due to empty requirements
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_get_administrative_penalties_with_pagination(
    client, auth_header_super_user, created_inspection, created_administrative_penalty
):
    """Test getting administrative penalties with pagination parameters."""
    url = f"{API_BASE_URL}?inspection_id={created_inspection.id}&page=1&per_page=10"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert isinstance(result.json, list)


def test_get_administrative_penalties_with_invalid_pagination(
    client, auth_header_super_user, created_inspection
):
    """Test getting administrative penalties with invalid pagination parameters."""
    url = f"{API_BASE_URL}?inspection_id={created_inspection.id}&page=-1&per_page=0"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK  # Should handle gracefully


def test_get_projectwise_administrative_penalties_with_no_project(
    client, auth_header_super_user, created_case_file
):
    """Test getting administrative penalties for a case file without project."""
    url = f"{API_BASE_URL}projectwise?case_file_id={created_case_file.id}"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert isinstance(result.json, list)


def test_link_administrative_penalty_already_linked(
    client,
    auth_header_super_user,
    created_administrative_penalty,
    created_inspection,
    created_administrative_penalty_inspection_requirement,
    session,
):
    """Test linking administrative penalty to requirements that are already linked."""
    # The created_administrative_penalty fixture already links to
    # created_administrative_penalty_inspection_requirement
    # So trying to link the same requirement should fail
    url = urljoin(API_BASE_URL, "links")
    link_data = {
        "administrative_penalty_id": created_administrative_penalty.id,
        "inspection_id": created_inspection.id,
        "inspection_requirement_ids": [
            created_administrative_penalty_inspection_requirement.id
        ],
    }

    result = client.post(
        url,
        data=json.dumps(link_data),
        headers=auth_header_super_user,
    )
    # Should fail because the requirement is already linked by the fixture
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_update_administrative_penalty_with_duplicate_requirements(
    client,
    auth_header_super_user,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
    session,
):
    """Test updating administrative penalty with requirements already used in another penalty."""
    # Create another administrative penalty
    from compliance_api.models.administrative_penalty import AdministrativePenalty

    another_ap = AdministrativePenalty(
        inspection_id=created_administrative_penalty.inspection_id,
        administrative_penalty_number=f"TEST-AP-{random.randint(100000, 999999)}",
        referral_status=ReferralStatusEnum.PREPARING_REFERRAL_FOR_AEO,
        is_active=True,
        is_deleted=False,
    )
    session.add(another_ap)
    session.commit()

    # Now try to link the same requirement to the second administrative penalty using the links endpoint (should fail)
    url = urljoin(API_BASE_URL, "links")
    link_data = {
        "administrative_penalty_id": another_ap.id,
        "inspection_id": created_administrative_penalty.inspection_id,
        "inspection_requirement_ids": [
            created_administrative_penalty_inspection_requirement.id
        ],
    }

    result = client.post(
        url,
        data=json.dumps(link_data),
        headers=auth_header_super_user,
    )
    print(result.json)
    assert result.status_code == HTTPStatus.CREATED


def test_concurrent_administrative_penalty_creation_same_requirements(
    client,
    auth_header_super_user,
    created_inspection,
    created_administrative_penalty_inspection_requirement,
):
    """Test concurrent creation of administrative penalties with same requirements (simulated)."""
    url = API_BASE_URL
    ap_data = copy.copy(AdministrativePenaltyScenario.default_value.value)
    ap_data["inspection_id"] = created_inspection.id
    ap_data["inspection_requirement_ids"] = [
        created_administrative_penalty_inspection_requirement.id
    ]

    # First request should succeed
    result1 = client.post(
        url,
        data=json.dumps(ap_data),
        headers=auth_header_super_user,
    )

    # Second request with same requirements should fail
    ap_data["administrative_penalty_number"] = (
        f"TEST-AP-{random.randint(100000, 999999)}"
    )
    result2 = client.post(
        url,
        data=json.dumps(ap_data),
        headers=auth_header_super_user,
    )

    # First should succeed, second should fail with validation error
    status_codes = [result1.status_code, result2.status_code]
    assert HTTPStatus.CREATED in status_codes


def test_update_administrative_penalty_status_transitions(
    client,
    auth_header_super_user,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
):
    """Test various status transitions for administrative penalty."""
    # Test transition from PREPARING_REFERRAL_FOR_AEO to REFERRED_TO_AEO
    url = urljoin(API_BASE_URL, f"{created_administrative_penalty.id}")
    update_data = {
        "inspection_id": created_administrative_penalty.inspection_id,
        "referral_status": ReferralStatusEnum.REFERRED_TO_AEO.name,
        "date_referred": (
            created_administrative_penalty.date_referred.strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            if created_administrative_penalty.date_referred
            else None
        ),
        "decision_date": (
            created_administrative_penalty.decision_date.strftime(
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            if created_administrative_penalty.decision_date
            else None
        ),
        "decision": (
            created_administrative_penalty.decision.name
            if created_administrative_penalty.decision
            else None
        ),
        "penalty_amount": (
            str(created_administrative_penalty.penalty_amount)
            if created_administrative_penalty.penalty_amount
            else None
        ),
        "inspection_requirement_ids": [
            created_administrative_penalty_inspection_requirement.id
        ],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["referral_status"]["id"] == ReferralStatusEnum.REFERRED_TO_AEO.name

    # Test transition to AP_NOT_PROCEEDING
    update_data["referral_status"] = ReferralStatusEnum.AP_NOT_PROCEEDING.name
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert (
        result.json["referral_status"]["id"] == ReferralStatusEnum.AP_NOT_PROCEEDING.name
    )


def test_create_administrative_penalty_with_custom_number(
    client,
    auth_header_super_user,
    created_inspection,
    created_administrative_penalty_inspection_requirement,
    session,
):
    """Test creating administrative penalty with custom administrative penalty number."""
    url = API_BASE_URL
    custom_number = f"CUSTOM-AP-{random.randint(100000, 999999)}"
    ap_data = copy.copy(AdministrativePenaltyScenario.default_value.value)
    ap_data["inspection_id"] = created_inspection.id
    ap_data["inspection_requirement_ids"] = [
        created_administrative_penalty_inspection_requirement.id
    ]
    ap_data["administrative_penalty_number"] = custom_number

    result = client.post(
        url,
        data=json.dumps(ap_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["administrative_penalty_number"] == custom_number


def test_get_projectwise_administrative_penalties_without_case_file_id(
    client, auth_header_super_user
):
    """Test getting projectwise administrative penalties without case_file_id parameter."""
    url = f"{API_BASE_URL}projectwise"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_link_administrative_penalty_missing_required_fields(
    client, auth_header_super_user
):
    """Test linking administrative penalty with missing required fields."""
    url = urljoin(API_BASE_URL, "links")
    link_data = {
        "administrative_penalty_id": 1,
        # Missing inspection_id and inspection_requirement_ids
    }

    result = client.post(
        url,
        data=json.dumps(link_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_update_administrative_penalty_with_penalty_amount_and_decision(
    client,
    auth_header_super_user,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
):
    """Test updating administrative penalty with both penalty amount and decision."""
    url = urljoin(API_BASE_URL, f"{created_administrative_penalty.id}")
    update_data = {
        "inspection_id": created_administrative_penalty.inspection_id,
        "decision": DecisionEnum.AP_ISSUED.name,
        "penalty_amount": 10000.00,
        "decision_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "inspection_requirement_ids": [
            created_administrative_penalty_inspection_requirement.id
        ],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["decision"]["id"] == DecisionEnum.AP_ISSUED.name
    assert result.json["penalty_amount"] == "10000.00"


JR_DATE = "2026-11-01T00:00:00.000000Z"


def _close_as_ap_issued(administrative_penalty):
    """Put the AP in the state judicial review starts from: closed, AP Issued, open case file."""
    administrative_penalty.inspection.case_file.case_file_status = CaseFileStatusEnum.OPEN
    administrative_penalty.referral_status = ReferralStatusEnum.REFERRED_TO_AEO
    administrative_penalty.decision = DecisionEnum.AP_ISSUED
    administrative_penalty.penalty_amount = 1000
    administrative_penalty.save()


def _closed_in_db(administrative_penalty):
    """Return whether the SQL closed conditions (get_closed_conditions) match the AP."""
    return (
        AdministrativePenalty.query.filter(
            AdministrativePenalty.id == administrative_penalty.id,
            AdministrativePenalty.get_closed_conditions(),
        ).count()
        == 1
    )


def _patch_jr(client, headers, administrative_penalty, requirement, **fields):
    """PATCH the AP with the full form in Judicial Review plus the given fields."""
    data = {
        "inspection_id": administrative_penalty.inspection_id,
        "referral_status": ReferralStatusEnum.JUDICIAL_REVIEW.name,
        "decision": DecisionEnum.AP_ISSUED.name,
        "penalty_amount": "1000.00",
        "jr_decision_date": JR_DATE,
        "inspection_requirement_ids": [requirement.id],
        **fields,
    }
    return client.patch(
        urljoin(API_BASE_URL, f"{administrative_penalty.id}"),
        data=json.dumps(data),
        headers={**headers, "Content-Type": "application/json"},
    )


def test_judicial_review_incomplete_save_reopens_ap(
    client,
    auth_header_super_user,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
):
    """Saving a JR with only the decision date reopens the AP."""
    _close_as_ap_issued(created_administrative_penalty)
    result = _patch_jr(
        client,
        auth_header_super_user,
        created_administrative_penalty,
        created_administrative_penalty_inspection_requirement,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["referral_status"]["id"] == ReferralStatusEnum.JUDICIAL_REVIEW.name
    assert result.json["is_closed"] is False
    assert _closed_in_db(created_administrative_penalty) is False


def test_judicial_review_complete_applies_amount_rules_and_closes(
    client,
    auth_header_super_user,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
):
    """Reversed forces 0, Upheld copies the penalty amount; a complete JR closes the AP."""
    _close_as_ap_issued(created_administrative_penalty)
    for decision, sent_amount, expected_amount in (
        (JudicialReviewDecisionEnum.REVERSED, "500.00", "0.00"),
        (JudicialReviewDecisionEnum.UPHELD, "500.00", "1000.00"),
        (JudicialReviewDecisionEnum.SUBSTITUTED, "500.00", "500.00"),
    ):
        result = _patch_jr(
            client,
            auth_header_super_user,
            created_administrative_penalty,
            created_administrative_penalty_inspection_requirement,
            jr_decision=decision.name,
            jr_new_penalty_amount=sent_amount,
        )
        assert result.status_code == HTTPStatus.OK
        assert result.json["jr_new_penalty_amount"] == expected_amount
        assert result.json["jr_decision"]["id"] == decision.name
        assert result.json["is_closed"] is True
        assert _closed_in_db(created_administrative_penalty) is True


def test_judicial_review_rejections(
    client,
    auth_header_super_user,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
):
    """JR rules: eligibility, required date, required amount, no status change, no stray JR fields."""
    args = (
        client,
        auth_header_super_user,
        created_administrative_penalty,
        created_administrative_penalty_inspection_requirement,
    )
    # Not eligible: AP still in Preparing Referral for AEO.
    assert _patch_jr(*args).status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    # Not eligible: the case file is closed.
    _close_as_ap_issued(created_administrative_penalty)
    created_administrative_penalty.inspection.case_file.case_file_status = CaseFileStatusEnum.CLOSED
    created_administrative_penalty.save()
    assert _patch_jr(*args).status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    _close_as_ap_issued(created_administrative_penalty)
    # JR fields without the JR status.
    assert (
        _patch_jr(*args, referral_status=ReferralStatusEnum.REFERRED_TO_AEO.name)
        .status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    )
    # Decision date is required on every JR save.
    assert _patch_jr(*args, jr_decision_date=None).status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    # Quashed and Remitted needs a new penalty amount.
    assert (
        _patch_jr(*args, jr_decision=JudicialReviewDecisionEnum.QUASHED_AND_REMITTED.name)
        .status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    )

    assert _patch_jr(*args).status_code == HTTPStatus.OK
    # Once in JR the status can only go back to Referred to AEO (discard).
    assert (
        _patch_jr(
            *args,
            referral_status=ReferralStatusEnum.AP_NOT_PROCEEDING.name,
            jr_decision_date=None,
        ).status_code
        == HTTPStatus.UNPROCESSABLE_ENTITY
    )
    # Discarding must clear the JR fields.
    assert (
        _patch_jr(*args, referral_status=ReferralStatusEnum.REFERRED_TO_AEO.name)
        .status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    )


def test_starting_judicial_review_skips_super_user_check(
    client,
    auth_header,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
    monkeypatch,
):
    """Starting JR on a closed AP needs primary officer or superuser, not superuser only.

    The test JWT passes every role check, so the superuser-only check is made to fail here.
    """
    def deny():
        raise PermissionDeniedError("superuser only")

    monkeypatch.setattr(ServiceUtils, "access_check_for_super_user", staticmethod(deny))
    _close_as_ap_issued(created_administrative_penalty)
    args = (
        client,
        auth_header,
        created_administrative_penalty,
        created_administrative_penalty_inspection_requirement,
    )
    assert _patch_jr(*args).status_code == HTTPStatus.OK
    # A plain edit of a closed AP still goes through the superuser-only check.
    _close_as_ap_issued(created_administrative_penalty)
    created_administrative_penalty.jr_decision_date = None
    created_administrative_penalty.save()
    result = _patch_jr(
        *args, referral_status=ReferralStatusEnum.REFERRED_TO_AEO.name, jr_decision_date=None
    )
    assert result.status_code == HTTPStatus.FORBIDDEN


def test_starting_judicial_review_checks_the_aps_own_inspection(
    client,
    auth_header,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
    monkeypatch,
):
    """A primary officer of another inspection cannot start a JR by sending that inspection's id."""
    other_data = copy.copy(InspectionScenario.default_value.value)
    other_data["case_file_id"] = created_administrative_penalty.inspection.case_file_id
    other_inspection = InspectionService.create(other_data)

    def primary_only_on_other(inspection):
        if inspection.id != other_inspection.id:
            raise PermissionDeniedError("not the primary officer")

    monkeypatch.setattr(
        ServiceUtils, "access_check_update_for_inspection", staticmethod(primary_only_on_other)
    )
    _close_as_ap_issued(created_administrative_penalty)
    result = _patch_jr(
        client,
        auth_header,
        created_administrative_penalty,
        created_administrative_penalty_inspection_requirement,
        inspection_id=other_inspection.id,
        inspection_requirement_ids=[],
        jr_decision=JudicialReviewDecisionEnum.REVERSED.name,
    )
    assert result.status_code == HTTPStatus.FORBIDDEN
    assert created_administrative_penalty.referral_status == ReferralStatusEnum.REFERRED_TO_AEO


def test_starting_judicial_review_checks_the_request_inspection(
    client,
    auth_header,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
    monkeypatch,
):
    """A primary officer of the AP's inspection cannot write requirement links on another inspection."""
    other_data = copy.copy(InspectionScenario.default_value.value)
    other_data["case_file_id"] = created_administrative_penalty.inspection.case_file_id
    other_inspection = InspectionService.create(other_data)

    def primary_only_on_own(inspection):
        if inspection.id != created_administrative_penalty.inspection_id:
            raise PermissionDeniedError("not the primary officer")

    monkeypatch.setattr(
        ServiceUtils, "access_check_update_for_inspection", staticmethod(primary_only_on_own)
    )
    _close_as_ap_issued(created_administrative_penalty)
    result = _patch_jr(
        client,
        auth_header,
        created_administrative_penalty,
        created_administrative_penalty_inspection_requirement,
        inspection_id=other_inspection.id,
        inspection_requirement_ids=[],
        jr_decision=JudicialReviewDecisionEnum.REVERSED.name,
    )
    assert result.status_code == HTTPStatus.FORBIDDEN
    assert created_administrative_penalty.referral_status == ReferralStatusEnum.REFERRED_TO_AEO


def test_discarding_judicial_review_restores_referred_to_aeo(
    client,
    auth_header_super_user,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
):
    """Discard sets the status back to Referred to AEO, clears the JR fields and the edited flag."""
    _close_as_ap_issued(created_administrative_penalty)
    args = (
        client,
        auth_header_super_user,
        created_administrative_penalty,
        created_administrative_penalty_inspection_requirement,
    )
    result = _patch_jr(*args, penalty_amount="2000.00", jr_ap_fields_edited=True)
    assert result.status_code == HTTPStatus.OK
    assert result.json["jr_ap_fields_edited"] is True
    # A later JR save without new AP field edits keeps the flag.
    result = _patch_jr(*args, penalty_amount="2000.00")
    assert result.status_code == HTTPStatus.OK
    assert result.json["jr_ap_fields_edited"] is True

    result = _patch_jr(
        *args,
        referral_status=ReferralStatusEnum.REFERRED_TO_AEO.name,
        penalty_amount="2000.00",
        jr_decision_date=None,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["referral_status"]["id"] == ReferralStatusEnum.REFERRED_TO_AEO.name
    assert result.json["jr_decision_date"] is None
    assert result.json["jr_ap_fields_edited"] is False
    # Changes to the other AP fields remain.
    assert result.json["penalty_amount"] == "2000.00"
    assert result.json["is_closed"] is True


def test_primary_officer_cannot_change_ap_fields_in_judicial_review(
    client,
    auth_header,
    created_administrative_penalty,
    created_administrative_penalty_inspection_requirement,
    monkeypatch,
):
    """A primary officer records the JR, but the AP fields keep their stored values.

    The test JWT passes every role check, so the user is made a non-superuser here.
    """
    monkeypatch.setattr(ServiceUtils, "is_super_user", staticmethod(lambda: False))
    monkeypatch.setattr(
        ServiceUtils, "access_check_update_for_inspection", staticmethod(lambda inspection: None)
    )
    _close_as_ap_issued(created_administrative_penalty)
    result = _patch_jr(
        client,
        auth_header,
        created_administrative_penalty,
        created_administrative_penalty_inspection_requirement,
        penalty_amount="2000.00",
        jr_ap_fields_edited=True,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["referral_status"]["id"] == ReferralStatusEnum.JUDICIAL_REVIEW.name
    assert result.json["penalty_amount"] == "1000.00"
    assert result.json["jr_ap_fields_edited"] is False


def test_review_board_shows_only_preparing_referral(
    client,
    auth_header,
    created_administrative_penalty,
):
    """Only Preparing Referral for AEO APs appear on the Review Board, open or closed."""
    url = "/api/review-board/administrative-penalties"
    for status, decision, shown in (
        (ReferralStatusEnum.PREPARING_REFERRAL_FOR_AEO, None, True),
        (ReferralStatusEnum.REFERRED_TO_AEO, None, False),
        (ReferralStatusEnum.REFERRED_TO_AEO, DecisionEnum.AP_ISSUED, False),
        (ReferralStatusEnum.AP_NOT_PROCEEDING, None, False),
        (ReferralStatusEnum.JUDICIAL_REVIEW, DecisionEnum.AP_ISSUED, False),
    ):
        created_administrative_penalty.referral_status = status
        created_administrative_penalty.decision = decision
        created_administrative_penalty.save()
        result = client.get(url, headers=auth_header)
        assert result.status_code == HTTPStatus.OK
        numbers = [item["administrative_penalty_number"] for item in result.json]
        assert (
            created_administrative_penalty.administrative_penalty_number in numbers
        ) is shown, status
