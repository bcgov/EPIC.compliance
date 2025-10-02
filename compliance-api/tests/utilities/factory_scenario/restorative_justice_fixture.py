"""Fixtures for Restorative Justice tests."""

import copy
import random

import pytest

from compliance_api.models.restorative_justice import RestorativeJustice as RestorativeJusticeModel
from compliance_api.models.restorative_justice import (
    RestorativeJusticeInspectionRequirementMap, RestorativeJusticeStatusEnum)
from compliance_api.services.inspection_requirement import InspectionRequirementService
from compliance_api.services.restorative_justice import RestorativeJusticeService
from tests.utilities.factory_scenario.inspection_requirement_scenario import InspectionRequirementScenario
from tests.utilities.factory_scenario.restorative_justice_scenario import RestorativeJusticeScenario


@pytest.fixture
def created_restorative_justice_inspection_requirement(app, created_inspection, mocker):
    """Create an inspection requirement for restorative justice testing."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    access_check_fn = mocker.patch(
        "compliance_api.services.service_utils.ServiceUtils.access_check_update_for_inspection"
    )
    access_check_fn.return_value = True
    requirement_data = copy.copy(InspectionRequirementScenario.default_value.value)
    # Ensure the requirement has RESTORATIVE_JUSTICE enforcement action (ID 12)
    requirement_data["enforcement_action_ids"] = [12]
    requirement = InspectionRequirementService.create(
        created_inspection.id, requirement_data
    )
    return requirement


@pytest.fixture
def created_restorative_justice(
    created_inspection, created_restorative_justice_inspection_requirement, mocker
):
    """Create and return a Restorative Justice."""
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

    restorative_justice_data = copy.copy(RestorativeJusticeScenario.default_value.value)
    restorative_justice_data["inspection_id"] = created_inspection.id
    restorative_justice_data["inspection_requirement_ids"] = [
        created_restorative_justice_inspection_requirement.id
    ]

    # Use the service layer to create the restorative justice (handles requirements properly)
    restorative_justice = RestorativeJusticeService.create_restorative_justice(
        restorative_justice_data
    )
    return restorative_justice


@pytest.fixture
def created_restorative_justice_requirement_map(
    created_restorative_justice, created_inspection_requirement, session
):
    """Create and return a Restorative Justice Inspection Requirement Map."""
    restorative_justice_requirement_map = RestorativeJusticeInspectionRequirementMap(
        restorative_justice_id=created_restorative_justice.id,
        inspection_requirement_id=created_inspection_requirement.id,
    )
    restorative_justice_requirement_map.save()
    session.commit()
    return restorative_justice_requirement_map


@pytest.fixture
def created_restorative_justice_drafting(app, db, created_inspection):
    """Return a restorative justice in DRAFTING status."""
    restorative_justice = RestorativeJusticeModel(
        inspection_id=created_inspection.id,
        restorative_justice_number=f"TEST-RJ-DRAFT-{random.randint(100000, 999999)}",
        status=RestorativeJusticeStatusEnum.DRAFTING,
        is_active=True,
        is_deleted=False,
    )
    db.session.add(restorative_justice)
    db.session.commit()
    return restorative_justice


@pytest.fixture
def created_restorative_justice_open(app, db, created_inspection):
    """Return a restorative justice in OPEN status."""
    restorative_justice = RestorativeJusticeModel(
        inspection_id=created_inspection.id,
        restorative_justice_number=f"TEST-RJ-OPEN-{random.randint(100000, 999999)}",
        status=RestorativeJusticeStatusEnum.OPEN,
        restitution_details="Work in progress",
        is_active=True,
        is_deleted=False,
    )
    db.session.add(restorative_justice)
    db.session.commit()
    return restorative_justice


@pytest.fixture
def created_restorative_justice_closed(app, db, created_inspection):
    """Return a restorative justice in CLOSED status."""
    from datetime import datetime, timezone

    restorative_justice = RestorativeJusticeModel(
        inspection_id=created_inspection.id,
        restorative_justice_number=f"TEST-RJ-CLOSED-{random.randint(100000, 999999)}",
        status=RestorativeJusticeStatusEnum.CLOSED,
        restitution_details="All work completed",
        date_restitution_complete=datetime.now(timezone.utc),
        is_active=True,
        is_deleted=False,
    )
    db.session.add(restorative_justice)
    db.session.commit()
    return restorative_justice
