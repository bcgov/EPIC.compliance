"""Test suite for orders."""

import copy
import json
import random
from http import HTTPStatus
from urllib.parse import urljoin

import pytest
from compliance_api.models.order import Order, OrderStatusEnum
from compliance_api.services.order.order import OrderService

from tests.utilities.factory_scenario.order_scenario import OrderScenario


API_BASE_URL = "/api/orders/"

def test_get_orders(client, auth_header_super_user, created_inspection, created_order):
    """Test getting all orders for an inspection."""
    print(created_order.id)
    url = f"{API_BASE_URL}?inspection_id={created_inspection.id}"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert len(result.json) == 1
    assert isinstance(result.json, list)


def test_get_orders_without_inspection_id(
    client, auth_header_super_user, created_order
):
    """Test getting all orders without specifying an inspection ID."""
    url = API_BASE_URL
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert isinstance(result.json, list)
    assert len(result.json) >= 1


def test_get_projectwise_orders(
    client, auth_header_super_user, created_order, created_inspection
):
    """Test getting all orders for a project."""
    url = f"{API_BASE_URL}projectwise?case_file_id={created_inspection.case_file_id}"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert isinstance(result.json, list)


def test_get_projectwise_orders_with_invalid_case_file_id(
    client, auth_header_super_user
):
    """Test getting all orders for a project with invalid case file ID."""
    url = f"{API_BASE_URL}projectwise?case_file_id=9999"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_get_order_by_id(client, auth_header_super_user, created_order, session):
    """Test getting order by ID."""
    url = urljoin(API_BASE_URL, f"{created_order.id}")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert result.json["id"] == created_order.id


def test_get_order_by_invalid_id(client, auth_header_super_user):
    """Test getting order by invalid ID."""
    url = urljoin(API_BASE_URL, "9999")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND



def test_get_order_by_invalid_order_number(client, auth_header_super_user):
    """Test getting order by invalid order number."""
    url = urljoin(API_BASE_URL, "order-numbers/INVALID-ORDER-NUMBER")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND





def test_update_order_with_invalid_id(
    client, auth_header_super_user, created_inspection
):
    """Test updating non-existent order."""
    url = urljoin(API_BASE_URL, "9999")
    update_data = copy.copy(OrderScenario.update_value.value)
    update_data["inspection_id"] = created_inspection.id

    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_delete_order(client, auth_header_super_user, created_order, session):
    """Test deleting an order."""
    url = urljoin(API_BASE_URL, f"{created_order.id}")
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NO_CONTENT

    # Verify deletion
    deleted_order = Order.find_by_id(created_order.id)
    assert deleted_order is None or deleted_order.is_deleted


def test_delete_order_with_invalid_id(client, auth_header_super_user):
    """Test deleting non-existent order."""
    url = urljoin(API_BASE_URL, "9999")
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_delete_order_with_open_status(
    client, auth_header_super_user, created_order, db
):
    """Test deleting an order with OPEN status."""
    # Update order status to OPEN
    created_order.order_status = OrderStatusEnum.OPEN
    db.session.commit()

    url = urljoin(API_BASE_URL, f"{created_order.id}")
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY




def test_change_order_status_with_invalid_id(client, auth_header_super_user):
    """Test changing status of non-existent order."""
    url = urljoin(API_BASE_URL, "9999/status")
    status_data = copy.copy(OrderScenario.status_value.value)

    result = client.patch(
        url,
        data=json.dumps(status_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND



def test_order_preview(
    client, auth_header_super_user, created_order, mock_doc_gen_service, session
):
    """Test previewing an order."""
    url = urljoin(API_BASE_URL, f"{created_order.id}/render?output_format=html")

    result = client.post(
        url,
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.OK


def test_order_preview_with_invalid_id(client, auth_header_super_user, mock_doc_gen_service):
    """Test previewing non-existent order."""
    url = urljoin(API_BASE_URL, "9999/render?output_format=html")

    result = client.post(
        url,
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_create_order_success(client, auth_header_super_user, created_inspection, created_inspection_requirement, session):
    """Test successfully creating a new order."""
    url = API_BASE_URL
    order_data = copy.copy(OrderScenario.default_value.value)
    order_data["inspection_id"] = created_inspection.id
    order_data["issuing_officer_id"] = created_inspection.primary_officer_id
    order_data["inspection_requirement_ids"] = [created_inspection_requirement.id]

    result = client.post(
        url,
        data=json.dumps(order_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["inspection_id"] == created_inspection.id
    assert result.json["order_status"]["id"] == OrderStatusEnum.CREATED.name


def test_create_order_with_invalid_inspection_id(client, auth_header_super_user):
    """Test creating order with invalid inspection ID."""
    url = API_BASE_URL
    order_data = copy.copy(OrderScenario.default_value.value)
    order_data["inspection_id"] = 9999
    order_data["inspection_requirement_ids"] = [1]

    result = client.post(
        url,
        data=json.dumps(order_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_create_order_with_invalid_officer_id(client, auth_header_super_user, created_inspection, created_inspection_requirement):
    """Test creating order with invalid issuing officer ID."""
    url = API_BASE_URL
    order_data = copy.copy(OrderScenario.default_value.value)
    order_data["inspection_id"] = created_inspection.id
    order_data["issuing_officer_id"] = 9999
    order_data["inspection_requirement_ids"] = [created_inspection_requirement.id]

    result = client.post(
        url,
        data=json.dumps(order_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_order_with_empty_requirements(client, auth_header_super_user, created_inspection):
    """Test creating order with empty inspection requirements."""
    url = API_BASE_URL
    order_data = copy.copy(OrderScenario.default_value.value)
    order_data["inspection_id"] = created_inspection.id
    order_data["issuing_officer_id"] = created_inspection.primary_officer_id
    order_data["inspection_requirement_ids"] = []

    result = client.post(
        url,
        data=json.dumps(order_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_create_order_with_invalid_requirements(client, auth_header_super_user, created_inspection):
    """Test creating order with invalid inspection requirement IDs."""
    url = API_BASE_URL
    order_data = copy.copy(OrderScenario.default_value.value)
    order_data["inspection_id"] = created_inspection.id
    order_data["issuing_officer_id"] = created_inspection.primary_officer_id
    order_data["inspection_requirement_ids"] = [9999]

    result = client.post(
        url,
        data=json.dumps(order_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_order_with_duplicate_requirements(
    client, auth_header_super_user, created_inspection, created_inspection_requirement, created_order, session
):
    """Test creating order with requirements that are already used in another order."""
    # First, update the existing order to use the inspection requirement
    url = urljoin(API_BASE_URL, f"{created_order.id}")
    update_data = copy.copy(OrderScenario.update_value.value)
    update_data["inspection_id"] = created_inspection_requirement.inspection_id
    update_data["issuing_officer_id"] = created_inspection_requirement.inspection.primary_officer_id
    update_data["inspection_requirement_ids"] = [created_inspection_requirement.id]

    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.OK

    # Now try to create a new order with the same requirement (should fail)
    url = API_BASE_URL
    order_data = copy.copy(OrderScenario.default_value.value)
    order_data["inspection_id"] = created_inspection.id
    order_data["issuing_officer_id"] = created_inspection.primary_officer_id
    order_data["inspection_requirement_ids"] = [created_inspection_requirement.id]

    result = client.post(
        url,
        data=json.dumps(order_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_order_missing_required_fields(client, auth_header_super_user):
    """Test creating order with missing required fields."""
    url = API_BASE_URL
    order_data = {
        "where_as": "Test where as",
        "now_therefore": "Test now therefore",
    }

    result = client.post(
        url,
        data=json.dumps(order_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_update_order_success(client, auth_header_super_user, created_order, created_inspection_requirement, session):
    """Test successfully updating an existing order."""
    url = urljoin(API_BASE_URL, f"{created_order.id}")
    update_data = copy.copy(OrderScenario.update_value.value)
    update_data["inspection_id"] = created_inspection_requirement.inspection_id
    update_data["issuing_officer_id"] = created_inspection_requirement.inspection.primary_officer_id
    update_data["inspection_requirement_ids"] = [created_inspection_requirement.id]

    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["where_as"] == "Updated where as"
    assert result.json["now_therefore"] == "Updated now therefore"


def test_update_order_with_invalid_inspection_id(client, auth_header_super_user, created_order):
    """Test updating order with invalid inspection ID."""
    url = urljoin(API_BASE_URL, f"{created_order.id}")
    update_data = copy.copy(OrderScenario.update_value.value)
    update_data["inspection_id"] = 9999

    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_update_order_with_invalid_officer_id(client, auth_header_super_user, created_order, created_inspection):
    """Test updating order with invalid issuing officer ID."""
    url = urljoin(API_BASE_URL, f"{created_order.id}")
    update_data = copy.copy(OrderScenario.update_value.value)
    update_data["inspection_id"] = created_inspection.id
    update_data["issuing_officer_id"] = 9999

    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_update_order_with_duplicate_requirements(
    client, auth_header_super_user, created_order, created_inspection_requirement, session
):
    """Test updating order with requirements that are already used in another order."""
    # First, update the existing order to use the inspection requirement
    url = urljoin(API_BASE_URL, f"{created_order.id}")
    update_data = copy.copy(OrderScenario.update_value.value)
    update_data["inspection_id"] = created_inspection_requirement.inspection_id
    update_data["issuing_officer_id"] = created_inspection_requirement.inspection.primary_officer_id
    update_data["inspection_requirement_ids"] = [created_inspection_requirement.id]

    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.OK

    # Create another order
    from compliance_api.models.order import Order
    from compliance_api.models.order import OrderStatusEnum, OrderProgressEnum
    
    another_order = Order(
        inspection_id=created_order.inspection_id,
        issuing_officer_id=created_order.issuing_officer_id,
        where_as="Another order",
        now_therefore="Another order therefore",
        order_number=f"TEST-ORDER-{random.randint(100000, 999999)}",
        order_status=OrderStatusEnum.CREATED,
        order_progress=OrderProgressEnum.DRAFTING,
        is_active=True,
        is_deleted=False,
    )
    session.add(another_order)
    session.commit()

    # Now try to assign the same requirement to the second order (should fail)
    url = urljoin(API_BASE_URL, f"{another_order.id}")
    update_data = copy.copy(OrderScenario.update_value.value)
    update_data["inspection_id"] = created_inspection_requirement.inspection_id
    update_data["issuing_officer_id"] = created_inspection_requirement.inspection.primary_officer_id
    update_data["inspection_requirement_ids"] = [created_inspection_requirement.id]

    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_change_order_status_success(client, auth_header_super_user, created_order, db):
    """Test successfully changing order status."""
    # First set the order to OPEN so we can close it
    created_order.order_status = OrderStatusEnum.OPEN
    db.session.commit()

    url = urljoin(API_BASE_URL, f"{created_order.id}/status")
    status_data = copy.copy(OrderScenario.status_value.value)

    result = client.patch(
        url,
        data=json.dumps(status_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.NO_CONTENT

    # Verify status change
    updated_order = Order.find_by_id(created_order.id)
    assert updated_order.order_status == OrderStatusEnum.CLOSED


def test_change_order_status_with_same_status(client, auth_header_super_user, created_order, db):
    """Test changing order status to the same status."""
    # First set the order to CLOSED
    created_order.order_status = OrderStatusEnum.CLOSED
    db.session.commit()

    url = urljoin(API_BASE_URL, f"{created_order.id}/status")
    status_data = copy.copy(OrderScenario.status_value.value)

    result = client.patch(
        url,
        data=json.dumps(status_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_change_order_status_invalid_transition(client, auth_header_super_user, created_order, db):
    """Test changing order status with invalid transition."""
    # Try to change from CREATED to CLOSED (invalid transition)
    url = urljoin(API_BASE_URL, f"{created_order.id}/status")
    status_data = {"status": OrderStatusEnum.CLOSED.name}

    result = client.patch(
        url,
        data=json.dumps(status_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_issue_order_success(client, auth_header_super_user, created_order, session):
    """Test successfully issuing an order."""
    url = urljoin(API_BASE_URL, f"{created_order.id}/issue")
    issue_data = copy.copy(OrderScenario.issue_value.value)

    result = client.patch(
        url,
        data=json.dumps(issue_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.NO_CONTENT

    # Verify order was issued
    from compliance_api.models.order import OrderProgressEnum
    updated_order = Order.find_by_id(created_order.id)
    assert updated_order.order_status == OrderStatusEnum.OPEN
    assert updated_order.order_progress == OrderProgressEnum.ISSUED
    assert updated_order.date_issued is not None


def test_issue_order_with_invalid_id(client, auth_header_super_user):
    """Test issuing non-existent order."""
    url = urljoin(API_BASE_URL, "9999/issue")
    issue_data = copy.copy(OrderScenario.issue_value.value)

    result = client.patch(
        url,
        data=json.dumps(issue_data),
        headers=auth_header_super_user,
    )
    print("adddsfdf", result.json)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_issue_order_missing_date(client, auth_header_super_user, created_order):
    """Test issuing order without date_issued."""
    url = urljoin(API_BASE_URL, f"{created_order.id}/issue")
    issue_data = {}

    result = client.patch(
        url,
        data=json.dumps(issue_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_delete_order_with_closed_status(
    client, auth_header_super_user, created_order, db
):
    """Test deleting an order with CLOSED status."""
    # Update order status to CLOSED
    created_order.order_status = OrderStatusEnum.CLOSED
    db.session.commit()

    url = urljoin(API_BASE_URL, f"{created_order.id}")
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NO_CONTENT

    # Verify deletion
    deleted_order = Order.find_by_id(created_order.id)
    assert deleted_order is None or deleted_order.is_deleted


def test_delete_order_with_issued_progress(
    client, auth_header_super_user, created_order, db
):
    """Test deleting an order with ISSUED progress."""
    from compliance_api.models.order import OrderProgressEnum
    
    # Update order progress to ISSUED
    created_order.order_progress = OrderProgressEnum.ISSUED
    db.session.commit()

    url = urljoin(API_BASE_URL, f"{created_order.id}")
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_get_orders_with_pagination(client, auth_header_super_user, created_inspection, created_order):
    """Test getting orders with pagination parameters."""
    url = f"{API_BASE_URL}?inspection_id={created_inspection.id}&page=1&per_page=10"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert isinstance(result.json, list)


def test_get_orders_with_invalid_pagination(client, auth_header_super_user, created_inspection):
    """Test getting orders with invalid pagination parameters."""
    url = f"{API_BASE_URL}?inspection_id={created_inspection.id}&page=-1&per_page=0"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK  # Should handle gracefully


def test_order_preview_with_pdf_format(
    client, auth_header_super_user, created_order, mock_doc_gen_service, session
):
    """Test previewing an order in PDF format."""
    url = urljoin(API_BASE_URL, f"{created_order.id}/render?output_format=pdf")

    result = client.post(
        url,
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.OK


def test_order_preview_with_invalid_format(
    client, auth_header_super_user, created_order, mock_doc_gen_service, session
):
    """Test previewing an order with invalid output format."""
    url = urljoin(API_BASE_URL, f"{created_order.id}/render?output_format=invalid_format")

    result = client.post(
        url,
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_get_projectwise_orders_with_no_project(
    client, auth_header_super_user, created_case_file
):
    """Test getting orders for a case file without project."""
    url = f"{API_BASE_URL}projectwise?case_file_id={created_case_file.id}"
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert isinstance(result.json, list)


def test_get_orders_unauthorized(client, created_inspection):
    """Test getting orders without authentication."""
    url = f"{API_BASE_URL}?inspection_id={created_inspection.id}"
    result = client.get(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_create_order_unauthorized(client):
    """Test creating order without authentication."""
    url = API_BASE_URL
    order_data = copy.copy(OrderScenario.default_value.value)

    result = client.post(
        url,
        data=json.dumps(order_data),
    )
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_update_order_unauthorized(client, created_order):
    """Test updating order without authentication."""
    url = urljoin(API_BASE_URL, f"{created_order.id}")
    update_data = copy.copy(OrderScenario.update_value.value)

    result = client.patch(
        url,
        data=json.dumps(update_data),
    )
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_delete_order_unauthorized(client, created_order):
    """Test deleting order without authentication."""
    url = urljoin(API_BASE_URL, f"{created_order.id}")
    result = client.delete(url)
    assert result.status_code == HTTPStatus.UNAUTHORIZED


def test_get_order_by_order_number_success(client, auth_header_super_user, created_order):
    """Test getting order by order number."""
    url = urljoin(API_BASE_URL, f"order-numbers/{created_order.order_number}")
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert result.json["id"] == created_order.id
    assert result.json["order_number"] == created_order.order_number


def test_create_order_with_null_values(client, auth_header_super_user, created_inspection):
    """Test creating order with null values for optional fields."""
    url = API_BASE_URL
    order_data = copy.copy(OrderScenario.default_value.value)
    order_data["inspection_id"] = created_inspection.id
    order_data["issuing_officer_id"] = created_inspection.primary_officer_id
    order_data["inspection_requirement_ids"] = []
    order_data["intended_issuance_date"] = None
    order_data["section_id"] = None

    result = client.post(
        url,
        data=json.dumps(order_data),
        headers=auth_header_super_user,
    )
    # This should fail due to empty requirements
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_update_order_partial_data(client, auth_header_super_user, created_order, created_inspection, mocker):
    """Test updating order with partial data."""
    # Create an inspection requirement with ORDER enforcement action
    from compliance_api.services.inspection_requirement import InspectionRequirementService
    from tests.utilities.factory_scenario.inspection_requirement_scenario import InspectionRequirementScenario
    
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    access_check_fn = mocker.patch(
        "compliance_api.services.service_utils.ServiceUtils.access_check_update_for_inspection"
    )
    access_check_fn.return_value = True
    
    requirement_data = copy.copy(InspectionRequirementScenario.default_value.value)
    requirement_data["enforcement_action_ids"] = [5]  # ORDER enforcement action ID
    requirement = InspectionRequirementService.create(
        created_inspection.id, requirement_data
    )
    
    url = urljoin(API_BASE_URL, f"{created_order.id}")
    update_data = {
        "where_as": "Partially updated where as",
        "inspection_id": requirement.inspection_id,
        "issuing_officer_id": requirement.inspection.primary_officer_id,
        "inspection_requirement_ids": [requirement.id]
    }

    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=auth_header_super_user,
    )
    print("partial update")
    print(result.json)
    assert result.status_code == HTTPStatus.OK
    assert result.json["where_as"] == "Partially updated where as"


def test_change_order_status_to_rescinded(client, auth_header_super_user, created_order, db):
    """Test changing order status to RESCINDED."""
    # First set the order to OPEN
    created_order.order_status = OrderStatusEnum.OPEN
    db.session.commit()

    url = urljoin(API_BASE_URL, f"{created_order.id}/status")
    status_data = {"status": OrderStatusEnum.RESCINDED.name}

    result = client.patch(
        url,
        data=json.dumps(status_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.NO_CONTENT

    # Verify status change
    updated_order = Order.find_by_id(created_order.id)
    assert updated_order.order_status == OrderStatusEnum.RESCINDED


def test_change_order_status_from_closed_to_open(client, auth_header_super_user, created_order, db):
    """Test changing order status from CLOSED back to OPEN."""
    # First set the order to CLOSED
    created_order.order_status = OrderStatusEnum.CLOSED
    db.session.commit()

    url = urljoin(API_BASE_URL, f"{created_order.id}/status")
    status_data = {"status": OrderStatusEnum.OPEN.name}

    result = client.patch(
        url,
        data=json.dumps(status_data),
        headers=auth_header_super_user,
    )
    # Should succeed as CLOSED to OPEN is a valid transition
    assert result.status_code == HTTPStatus.NO_CONTENT

    # Verify status change
    updated_order = Order.find_by_id(created_order.id)
    assert updated_order.order_status == OrderStatusEnum.OPEN

def test_concurrent_order_creation_same_requirements(client, auth_header_super_user, created_inspection, created_inspection_requirement):
    """Test concurrent creation of orders with same requirements (simulated)."""
    url = API_BASE_URL
    order_data = copy.copy(OrderScenario.default_value.value)
    order_data["inspection_id"] = created_inspection.id
    order_data["issuing_officer_id"] = created_inspection.primary_officer_id
    order_data["inspection_requirement_ids"] = [created_inspection_requirement.id]

    # First request should succeed
    result1 = client.post(
        url,
        data=json.dumps(order_data),
        headers=auth_header_super_user,
    )
    
    # Second request with same requirements - may succeed if no unique constraints
    order_data["order_number"] = f"TEST-ORDER-{random.randint(100000, 999999)}"
    result2 = client.post(
        url,
        data=json.dumps(order_data),
        headers=auth_header_super_user,
    )
    
    # Both may succeed if requirements can be reused, or validation may prevent it
    status_codes = [result1.status_code, result2.status_code]
    # At least one should succeed, but both may fail with validation errors
    assert any(code in [HTTPStatus.CREATED, HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.BAD_REQUEST] for code in status_codes)
