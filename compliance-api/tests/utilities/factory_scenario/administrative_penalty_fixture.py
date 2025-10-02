"""Fixtures for Administrative Penalty tests."""

import copy

import pytest

from compliance_api.models.administrative_penalty import AdministrativePenaltyInspectionRequirementMap
from compliance_api.services.administrative_penalty import AdministrativePenaltyService
from compliance_api.services.inspection_requirement import InspectionRequirementService
from tests.utilities.factory_scenario.administrative_penalty_scenario import AdministrativePenaltyScenario
from tests.utilities.factory_scenario.inspection_requirement_scenario import InspectionRequirementScenario


@pytest.fixture
def created_administrative_penalty_inspection_requirement(
    app, created_inspection, mocker
):
    """Create an inspection requirement for administrative penalty testing."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    access_check_fn = mocker.patch(
        "compliance_api.services.service_utils.ServiceUtils.access_check_update_for_inspection"
    )
    access_check_fn.return_value = True
    requirement_data = copy.copy(InspectionRequirementScenario.default_value.value)
    # Ensure the requirement has ADMINISTRATIVE_PENALTY_RECOMMENDATION enforcement action (ID 6)
    requirement_data["enforcement_action_ids"] = [6]
    requirement = InspectionRequirementService.create(
        created_inspection.id, requirement_data
    )
    return requirement


@pytest.fixture
def created_administrative_penalty(
    created_inspection, created_administrative_penalty_inspection_requirement, mocker
):
    """Create and return an Administrative Penalty."""
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

    administrative_penalty_data = copy.copy(
        AdministrativePenaltyScenario.default_value.value
    )
    administrative_penalty_data["inspection_id"] = created_inspection.id
    administrative_penalty_data["inspection_requirement_ids"] = [
        created_administrative_penalty_inspection_requirement.id
    ]

    # Use the service layer to create the administrative penalty (handles requirements properly)
    administrative_penalty = AdministrativePenaltyService.create_administrative_penalty(
        administrative_penalty_data
    )
    return administrative_penalty


@pytest.fixture
def created_administrative_penalty_requirement_map(
    created_administrative_penalty, created_inspection_requirement, session
):
    """Create and return an Administrative Penalty Inspection Requirement Map."""
    administrative_penalty_requirement_map = (
        AdministrativePenaltyInspectionRequirementMap(
            administrative_penalty_id=created_administrative_penalty.id,
            inspection_requirement_id=created_inspection_requirement.id,
        )
    )
    administrative_penalty_requirement_map.save()
    session.commit()
    return administrative_penalty_requirement_map
