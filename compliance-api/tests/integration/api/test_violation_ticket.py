"""Test suite for violation tickets."""

import copy
import json
import random
from datetime import datetime, timezone
from http import HTTPStatus
from urllib.parse import urljoin

from compliance_api.models.violation_ticket import ViolationTicket, ViolationTicketStatusEnum
from tests.utilities.factory_scenario.violation_ticket_scenario import ViolationTicketScenario


API_BASE_URL = "/api/violation-tickets/"


def test_get_violation_tickets(
    client, auth_header_super_user, created_inspection, created_violation_ticket
):
    """Test getting all violation tickets for an inspection."""
    url = f"{API_BASE_URL}?inspection_id={created_inspection.id}"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert len(result.json) == 1
    assert isinstance(result.json, list)


def test_get_violation_tickets_without_inspection_id(client, auth_header_super_user):
    """Test getting violation tickets without inspection_id parameter."""
    url = API_BASE_URL
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert isinstance(result.json, list)


def test_get_violation_tickets_with_invalid_inspection_id(
    client, auth_header_super_user
):
    """Test getting violation tickets with invalid inspection ID."""
    url = f"{API_BASE_URL}?inspection_id=9999"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert result.json == []


def test_get_violation_ticket_by_id(
    client, auth_header_super_user, created_violation_ticket
):
    """Test getting a violation ticket by ID."""
    url = urljoin(API_BASE_URL, str(created_violation_ticket.id))
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert result.json["id"] == created_violation_ticket.id


def test_get_violation_ticket_by_invalid_id(client, auth_header_super_user):
    """Test getting a violation ticket with invalid ID."""
    url = urljoin(API_BASE_URL, "9999")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_get_violation_ticket_by_vt_number(
    client, auth_header_super_user, created_violation_ticket
):
    """Test getting a violation ticket by VT number."""
    url = urljoin(API_BASE_URL, f"vt-number/{created_violation_ticket.vt_number}")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert result.json["vt_number"] == created_violation_ticket.vt_number


def test_get_violation_ticket_by_invalid_vt_number(client, auth_header_super_user):
    """Test getting a violation ticket with invalid VT number."""
    url = urljoin(API_BASE_URL, "vt-number/INVALID-VT-NUMBER")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_create_violation_ticket_success(
    client,
    auth_header_super_user,
    created_inspection,
    created_violation_ticket_inspection_requirement,
):
    """Test successfully creating a violation ticket."""
    url = API_BASE_URL
    vt_data = copy.copy(ViolationTicketScenario.default_value.value)
    vt_data["inspection_id"] = created_inspection.id
    vt_data["ticket_number"] = f"VT-TEST-SUCCESS-{random.randint(100000, 999999)}"
    vt_data["inspection_requirement_ids"] = [
        created_violation_ticket_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(vt_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["inspection_id"] == created_inspection.id
    assert "vt_number" in result.json
    assert result.json["ticket_number"] == vt_data["ticket_number"]


def test_create_violation_ticket_issued_status(
    client,
    auth_header_super_user,
    created_inspection,
    created_violation_ticket_inspection_requirement,
):
    """Test creating a violation ticket (status will be set by system)."""
    url = API_BASE_URL
    vt_data = copy.copy(ViolationTicketScenario.issued_value.value)
    vt_data["inspection_id"] = created_inspection.id
    vt_data["ticket_number"] = f"VT-TEST-ISSUED-{random.randint(100000, 999999)}"
    vt_data["inspection_requirement_ids"] = [
        created_violation_ticket_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(vt_data, default=str),
        headers=auth_header_super_user,
    )
    print("issued status", result.json)
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["inspection_id"] == created_inspection.id
    assert "vt_number" in result.json


def test_create_violation_ticket_basic(
    client,
    auth_header_super_user,
    created_inspection,
    created_violation_ticket_inspection_requirement,
):
    """Test creating a basic violation ticket (fine amount set via update)."""
    url = API_BASE_URL
    vt_data = copy.copy(ViolationTicketScenario.large_fine_amount_value.value)
    vt_data["inspection_id"] = created_inspection.id
    vt_data["ticket_number"] = f"VT-TEST-LARGE-{random.randint(100000, 999999)}"
    vt_data["inspection_requirement_ids"] = [
        created_violation_ticket_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(vt_data, default=str),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["inspection_id"] == created_inspection.id


def test_create_violation_ticket_minimal(
    client,
    auth_header_super_user,
    created_inspection,
    created_violation_ticket_inspection_requirement,
):
    """Test creating a minimal violation ticket."""
    url = API_BASE_URL
    vt_data = copy.copy(ViolationTicketScenario.zero_fine_amount_value.value)
    vt_data["inspection_id"] = created_inspection.id
    vt_data["ticket_number"] = f"VT-TEST-ZERO-{random.randint(100000, 999999)}"
    vt_data["inspection_requirement_ids"] = [
        created_violation_ticket_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(vt_data, default=str),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["inspection_id"] == created_inspection.id


def test_create_violation_ticket_without_inspection_id(client, auth_header_super_user):
    """Test creating violation ticket without inspection_id."""
    url = API_BASE_URL
    vt_data = copy.copy(ViolationTicketScenario.default_value.value)
    vt_data.pop("inspection_id")

    result = client.post(
        url,
        data=json.dumps(vt_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_create_violation_ticket_without_ticket_number(client, auth_header_super_user):
    """Test creating violation ticket without ticket_number."""
    url = API_BASE_URL
    vt_data = copy.copy(ViolationTicketScenario.default_value.value)
    vt_data.pop("ticket_number")

    result = client.post(
        url,
        data=json.dumps(vt_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_create_violation_ticket_without_requirements(
    client, auth_header_super_user, created_inspection
):
    """Test creating violation ticket without inspection requirements."""
    url = API_BASE_URL
    vt_data = copy.copy(ViolationTicketScenario.minimal_value.value)
    vt_data["inspection_id"] = created_inspection.id

    result = client.post(
        url,
        data=json.dumps(vt_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_violation_ticket_with_duplicate_requirements(
    client,
    auth_header_super_user,
    created_inspection,
    created_violation_ticket_inspection_requirement,
    created_violation_ticket,
):
    """Test creating violation ticket with requirements that are already used."""
    url = API_BASE_URL
    vt_data = copy.copy(ViolationTicketScenario.default_value.value)
    vt_data["inspection_id"] = created_inspection.id
    vt_data["ticket_number"] = f"VT-TEST-DUPLICATE-{random.randint(100000, 999999)}"
    vt_data["inspection_requirement_ids"] = [
        created_violation_ticket_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(vt_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_update_violation_ticket_success(
    client,
    auth_header_super_user,
    created_violation_ticket,
    created_violation_ticket_inspection_requirement,
):
    """Test successfully updating an existing violation ticket."""
    url = urljoin(API_BASE_URL, str(created_violation_ticket.id))
    update_data = {
        "inspection_id": created_violation_ticket.inspection_id,
        "ticket_number": created_violation_ticket.ticket_number,
        "date_issued": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "fine_amount": "250.00",
        "status": "ISSUED",
        "status_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "inspection_requirement_ids": [
            created_violation_ticket_inspection_requirement.id
        ],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["fine_amount"] == "250.00"
    assert result.json["status"]["id"] == ViolationTicketStatusEnum.ISSUED.name


def test_update_violation_ticket_with_large_fine(
    client,
    auth_header_super_user,
    created_violation_ticket,
    created_violation_ticket_inspection_requirement,
):
    """Test updating violation ticket with large fine amount."""
    url = urljoin(API_BASE_URL, str(created_violation_ticket.id))
    update_data = copy.copy(ViolationTicketScenario.update_large_fine_value.value)
    update_data["inspection_id"] = created_violation_ticket.inspection_id
    update_data["ticket_number"] = created_violation_ticket.ticket_number
    update_data["inspection_requirement_ids"] = [
        created_violation_ticket_inspection_requirement.id
    ]

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data, default=str),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["fine_amount"] == "9999.99"
    assert result.json["status"]["id"] == ViolationTicketStatusEnum.ISSUED.name


def test_update_violation_ticket_with_zero_fine(
    client,
    auth_header_super_user,
    created_violation_ticket,
    created_violation_ticket_inspection_requirement,
):
    """Test updating violation ticket with zero fine amount."""
    url = urljoin(API_BASE_URL, str(created_violation_ticket.id))
    update_data = copy.copy(ViolationTicketScenario.update_zero_fine_value.value)
    update_data["inspection_id"] = created_violation_ticket.inspection_id
    update_data["ticket_number"] = created_violation_ticket.ticket_number
    update_data["inspection_requirement_ids"] = [
        created_violation_ticket_inspection_requirement.id
    ]

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data, default=str),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["fine_amount"] == "0.00"
    assert result.json["status"]["id"] == ViolationTicketStatusEnum.ISSUED.name


def test_update_violation_ticket_status_transitions(
    client, auth_header_super_user, created_violation_ticket_issued
):
    """Test updating violation ticket through status transitions."""
    url = urljoin(API_BASE_URL, str(created_violation_ticket_issued.id))

    # Update: ISSUED -> PAID
    update_data = {
        "inspection_id": created_violation_ticket_issued.inspection_id,
        "ticket_number": created_violation_ticket_issued.ticket_number,
        "status": "PAID",
        "status_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "inspection_requirement_ids": [],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["status"]["id"] == ViolationTicketStatusEnum.PAID.name


def test_update_violation_ticket_to_disputed(
    client, auth_header_super_user, created_violation_ticket_issued
):
    """Test updating violation ticket to DISPUTED status."""
    url = urljoin(API_BASE_URL, str(created_violation_ticket_issued.id))
    update_data = {
        "inspection_id": created_violation_ticket_issued.inspection_id,
        "ticket_number": created_violation_ticket_issued.ticket_number,
        "status": "DISPUTED",
        "status_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "inspection_requirement_ids": [],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["status"]["id"] == ViolationTicketStatusEnum.DISPUTED.name


def test_update_violation_ticket_paid_status_restriction(
    client, auth_header_super_user, created_violation_ticket_paid
):
    """Test that PAID violation tickets cannot be updated."""
    url = urljoin(API_BASE_URL, str(created_violation_ticket_paid.id))
    update_data = {
        "inspection_id": created_violation_ticket_paid.inspection_id,
        "ticket_number": created_violation_ticket_paid.ticket_number,
        "fine_amount": "500.00",
        "status": "ISSUED",
        "inspection_requirement_ids": [],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_update_violation_ticket_with_invalid_id(
    client, auth_header_super_user, created_inspection
):
    """Test updating non-existent violation ticket."""
    url = urljoin(API_BASE_URL, "9999")
    update_data = {
        "inspection_id": created_inspection.id,
        "ticket_number": "VT-TEST-UPDATE-001",
        "status": "ISSUED",
        "inspection_requirement_ids": [],
    }

    headers = {**auth_header_super_user, "Content-Type": "application/json"}
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=headers,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_delete_violation_ticket_success(
    client, auth_header_super_user, created_violation_ticket_issued
):
    """Test deleting a violation ticket in ISSUED status."""
    url = urljoin(API_BASE_URL, str(created_violation_ticket_issued.id))
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NO_CONTENT

    # Verify deletion
    deleted_vt = ViolationTicket.find_by_id(created_violation_ticket_issued.id)
    assert deleted_vt is None or deleted_vt.is_deleted


def test_delete_violation_ticket_paid_status_restriction(
    client, auth_header_super_user, created_violation_ticket_paid
):
    """Test that PAID violation tickets cannot be deleted."""
    url = urljoin(API_BASE_URL, str(created_violation_ticket_paid.id))
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_delete_violation_ticket_disputed_status_restriction(
    client, auth_header_super_user, created_violation_ticket_disputed
):
    """Test that DISPUTED violation tickets cannot be deleted."""
    url = urljoin(API_BASE_URL, str(created_violation_ticket_disputed.id))
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_delete_violation_ticket_with_invalid_id(client, auth_header_super_user):
    """Test deleting non-existent violation ticket."""
    url = urljoin(API_BASE_URL, "9999")
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


# Permission Tests
def test_get_violation_tickets_unauthorized(client, created_inspection):
    """Test getting violation tickets without authentication."""
    url = f"{API_BASE_URL}?inspection_id={created_inspection.id}"
    result = client.get(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_create_violation_ticket_unauthorized(client):
    """Test creating violation ticket without authentication."""
    url = API_BASE_URL
    vt_data = copy.copy(ViolationTicketScenario.default_value.value)

    result = client.post(url, data=json.dumps(vt_data))
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_update_violation_ticket_unauthorized(client, created_violation_ticket):
    """Test updating violation ticket without authentication."""
    url = urljoin(API_BASE_URL, str(created_violation_ticket.id))
    update_data = {
        "inspection_id": created_violation_ticket.inspection_id,
        "ticket_number": created_violation_ticket.ticket_number,
        "status": "PAID",
        "inspection_requirement_ids": [],
    }

    headers = {"Content-Type": "application/json"}
    result = client.patch(url, data=json.dumps(update_data), headers=headers)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_delete_violation_ticket_unauthorized(client, created_violation_ticket):
    """Test deleting violation ticket without authentication."""
    url = urljoin(API_BASE_URL, str(created_violation_ticket.id))
    result = client.delete(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_get_violation_ticket_by_id_unauthorized(client, created_violation_ticket):
    """Test getting violation ticket by ID without authentication."""
    url = urljoin(API_BASE_URL, str(created_violation_ticket.id))
    result = client.get(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_get_violation_ticket_by_vt_number_unauthorized(
    client, created_violation_ticket
):
    """Test getting violation ticket by VT number without authentication."""
    url = urljoin(API_BASE_URL, f"vt-number/{created_violation_ticket.vt_number}")
    result = client.get(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


# Edge Cases and Business Logic Tests
def test_vt_number_generation(
    client,
    auth_header_super_user,
    created_inspection,
    created_violation_ticket_inspection_requirement,
):
    """Test that VT number is auto-generated."""
    url = API_BASE_URL
    vt_data = copy.copy(ViolationTicketScenario.default_value.value)
    vt_data["inspection_id"] = created_inspection.id
    vt_data["ticket_number"] = f"VT-TEST-GEN-{random.randint(100000, 999999)}"
    vt_data["inspection_requirement_ids"] = [
        created_violation_ticket_inspection_requirement.id
    ]

    result = client.post(
        url,
        data=json.dumps(vt_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert "vt_number" in result.json
    assert result.json["vt_number"] is not None
    assert len(result.json["vt_number"]) > 0


def test_violation_ticket_enum_transformations(
    client, auth_header_super_user, created_violation_ticket_issued
):
    """Test that enum values are properly transformed in API responses."""
    url = urljoin(API_BASE_URL, str(created_violation_ticket_issued.id))
    result = client.get(url, headers=auth_header_super_user)

    assert result.status_code == HTTPStatus.OK
    assert "status" in result.json
    assert "id" in result.json["status"]
    assert "name" in result.json["status"]
    assert result.json["status"]["id"] == ViolationTicketStatusEnum.ISSUED.name
    assert result.json["status"]["name"] == ViolationTicketStatusEnum.ISSUED.value


def test_create_multiple_violation_tickets_same_inspection(
    client, auth_header_super_user, created_inspection, mocker
):
    """Test creating multiple violation tickets for the same inspection with different requirements."""
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
    requirement_data_1["enforcement_action_ids"] = [8]  # Violation Ticket
    requirement_1 = InspectionRequirementService.create(
        created_inspection.id, requirement_data_1
    )

    requirement_data_2 = copy.copy(InspectionRequirementScenario.default_value.value)
    requirement_data_2["enforcement_action_ids"] = [8]  # Violation Ticket
    requirement_2 = InspectionRequirementService.create(
        created_inspection.id, requirement_data_2
    )

    url = API_BASE_URL

    # Create first violation ticket
    vt_data_1 = copy.copy(ViolationTicketScenario.default_value.value)
    vt_data_1["inspection_id"] = created_inspection.id
    vt_data_1["ticket_number"] = f"VT-TEST-MULTI-{random.randint(100000, 999999)}"
    vt_data_1["inspection_requirement_ids"] = [requirement_1.id]

    result_1 = client.post(
        url,
        data=json.dumps(vt_data_1),
        headers=auth_header_super_user,
    )
    assert result_1.status_code == HTTPStatus.CREATED

    # Create second violation ticket
    vt_data_2 = copy.copy(ViolationTicketScenario.default_value.value)
    vt_data_2["inspection_id"] = created_inspection.id
    vt_data_2["ticket_number"] = f"VT-TEST-MULTI2-{random.randint(100000, 999999)}"
    vt_data_2["inspection_requirement_ids"] = [requirement_2.id]

    result_2 = client.post(
        url,
        data=json.dumps(vt_data_2),
        headers=auth_header_super_user,
    )
    assert result_2.status_code == HTTPStatus.CREATED

    # Verify both were created successfully
    assert result_1.json["id"] != result_2.json["id"]
    assert result_1.json["vt_number"] != result_2.json["vt_number"]
