"""Fixtures for Violation Ticket tests."""

import copy
import random
from decimal import Decimal

import pytest

from compliance_api.models.violation_ticket import ViolationTicket as ViolationTicketModel
from compliance_api.models.violation_ticket import ViolationTicketInspectionRequirementMap, ViolationTicketStatusEnum
from compliance_api.services.inspection_requirement import InspectionRequirementService
from compliance_api.services.violation_ticket import ViolationTicketService
from tests.utilities.factory_scenario.inspection_requirement_scenario import InspectionRequirementScenario
from tests.utilities.factory_scenario.violation_ticket_scenario import ViolationTicketScenario


@pytest.fixture
def created_violation_ticket_inspection_requirement(app, created_inspection, mocker):
    """Create an inspection requirement for violation ticket testing."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    access_check_fn = mocker.patch(
        "compliance_api.services.service_utils.ServiceUtils.access_check_update_for_inspection"
    )
    access_check_fn.return_value = True
    requirement_data = copy.copy(InspectionRequirementScenario.default_value.value)
    # Ensure the requirement has VIOLATION_TICKET enforcement action (ID 8)
    requirement_data["enforcement_action_ids"] = [8]
    requirement = InspectionRequirementService.create(
        created_inspection.id, requirement_data
    )
    return requirement


@pytest.fixture
def created_violation_ticket(
    created_inspection, created_violation_ticket_inspection_requirement, mocker
):
    """Create and return a Violation Ticket."""
    # Mock the necessary auth and access checks
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

    violation_ticket_data = copy.copy(ViolationTicketScenario.default_value.value)
    violation_ticket_data["inspection_id"] = created_inspection.id
    violation_ticket_data["ticket_number"] = (
        f"VT-FIXTURE-{random.randint(100000, 999999)}"
    )
    violation_ticket_data["inspection_requirement_ids"] = [
        created_violation_ticket_inspection_requirement.id
    ]

    # Use the service layer to create the violation ticket (handles requirements properly)
    violation_ticket = ViolationTicketService.create(violation_ticket_data)
    return violation_ticket


@pytest.fixture
def created_violation_ticket_requirement_map(
    created_violation_ticket, created_inspection_requirement, session
):
    """Create and return a Violation Ticket Inspection Requirement Map."""
    violation_ticket_requirement_map = ViolationTicketInspectionRequirementMap(
        violation_ticket_id=created_violation_ticket.id,
        inspection_requirement_id=created_inspection_requirement.id,
    )
    violation_ticket_requirement_map.save()
    session.commit()
    return violation_ticket_requirement_map


@pytest.fixture
def created_violation_ticket_issued(app, db, created_inspection):
    """Return a violation ticket in ISSUED status."""
    from datetime import datetime, timezone

    violation_ticket = ViolationTicketModel(
        inspection_id=created_inspection.id,
        vt_number=f"TEST-VT-ISSUED-{random.randint(100000, 999999)}",
        ticket_number=f"TICKET-ISSUED-{random.randint(1000, 9999)}",
        date_issued=datetime.now(timezone.utc),
        fine_amount=Decimal("150.00"),
        status=ViolationTicketStatusEnum.ISSUED,
        status_date=datetime.now(timezone.utc),
        is_active=True,
        is_deleted=False,
    )
    db.session.add(violation_ticket)
    db.session.commit()
    return violation_ticket


@pytest.fixture
def created_violation_ticket_paid(app, db, created_inspection):
    """Return a violation ticket in PAID status."""
    from datetime import datetime, timezone

    violation_ticket = ViolationTicketModel(
        inspection_id=created_inspection.id,
        vt_number=f"TEST-VT-PAID-{random.randint(100000, 999999)}",
        ticket_number=f"TICKET-PAID-{random.randint(1000, 9999)}",
        date_issued=datetime.now(timezone.utc),
        fine_amount=Decimal("300.00"),
        status=ViolationTicketStatusEnum.PAID,
        status_date=datetime.now(timezone.utc),
        is_active=True,
        is_deleted=False,
    )
    db.session.add(violation_ticket)
    db.session.commit()
    return violation_ticket


@pytest.fixture
def created_violation_ticket_disputed(app, db, created_inspection):
    """Return a violation ticket in DISPUTED status."""
    from datetime import datetime, timezone

    violation_ticket = ViolationTicketModel(
        inspection_id=created_inspection.id,
        vt_number=f"TEST-VT-DISPUTED-{random.randint(100000, 999999)}",
        ticket_number=f"TICKET-DISPUTED-{random.randint(1000, 9999)}",
        date_issued=datetime.now(timezone.utc),
        fine_amount=Decimal("500.00"),
        status=ViolationTicketStatusEnum.DISPUTED,
        status_date=datetime.now(timezone.utc),
        is_active=True,
        is_deleted=False,
    )
    db.session.add(violation_ticket)
    db.session.commit()
    return violation_ticket


@pytest.fixture
def created_violation_ticket_with_large_fine(app, db, created_inspection):
    """Return a violation ticket with a large fine amount."""
    from datetime import datetime, timezone

    violation_ticket = ViolationTicketModel(
        inspection_id=created_inspection.id,
        vt_number=f"TEST-VT-LARGE-{random.randint(100000, 999999)}",
        ticket_number=f"TICKET-LARGE-{random.randint(1000, 9999)}",
        date_issued=datetime.now(timezone.utc),
        fine_amount=Decimal("9999.99"),
        status=ViolationTicketStatusEnum.ISSUED,
        status_date=datetime.now(timezone.utc),
        is_active=True,
        is_deleted=False,
    )
    db.session.add(violation_ticket)
    db.session.commit()
    return violation_ticket


@pytest.fixture
def created_violation_ticket_zero_fine(app, db, created_inspection):
    """Return a violation ticket with zero fine amount."""
    from datetime import datetime, timezone

    violation_ticket = ViolationTicketModel(
        inspection_id=created_inspection.id,
        vt_number=f"TEST-VT-ZERO-{random.randint(100000, 999999)}",
        ticket_number=f"TICKET-ZERO-{random.randint(1000, 9999)}",
        date_issued=datetime.now(timezone.utc),
        fine_amount=Decimal("0.00"),
        status=ViolationTicketStatusEnum.ISSUED,
        status_date=datetime.now(timezone.utc),
        is_active=True,
        is_deleted=False,
    )
    db.session.add(violation_ticket)
    db.session.commit()
    return violation_ticket


@pytest.fixture
def created_violation_ticket_no_fine(app, db, created_inspection):
    """Return a violation ticket with no fine amount (None)."""
    from datetime import datetime, timezone

    violation_ticket = ViolationTicketModel(
        inspection_id=created_inspection.id,
        vt_number=f"TEST-VT-NO-FINE-{random.randint(100000, 999999)}",
        ticket_number=f"TICKET-NO-FINE-{random.randint(1000, 9999)}",
        date_issued=datetime.now(timezone.utc),
        fine_amount=None,
        status=ViolationTicketStatusEnum.ISSUED,
        status_date=datetime.now(timezone.utc),
        is_active=True,
        is_deleted=False,
    )
    db.session.add(violation_ticket)
    db.session.commit()
    return violation_ticket
