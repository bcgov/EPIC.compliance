"""Fixtures for Charge Recommendation tests."""

import copy
import random

import pytest

from compliance_api.models.charge_recommendation import ChargeRecommendation as ChargeRecommendationModel
from compliance_api.models.charge_recommendation import (
    ChargeRecommendationInspectionRequirementMap, ChargeRecommendationStatusEnum)
from compliance_api.services.charge_recommendation import ChargeRecommendationService
from compliance_api.services.inspection_requirement import InspectionRequirementService
from tests.utilities.factory_scenario.charge_recommendation_scenario import ChargeRecommendationScenario
from tests.utilities.factory_scenario.inspection_requirement_scenario import InspectionRequirementScenario


@pytest.fixture
def created_charge_recommendation_inspection_requirement(
    app, created_inspection, mocker
):
    """Create an inspection requirement for charge recommendation testing."""
    contains_role = mocker.patch("compliance_api.auth.jwt.contains_role")
    contains_role.return_value = True
    access_check_fn = mocker.patch(
        "compliance_api.services.service_utils.ServiceUtils.access_check_update_for_inspection"
    )
    access_check_fn.return_value = True
    requirement_data = copy.copy(InspectionRequirementScenario.default_value.value)
    # Ensure the requirement has CHARGE_RECOMMENDATION enforcement action (ID 9)
    requirement_data["enforcement_action_ids"] = [9]
    requirement = InspectionRequirementService.create(
        created_inspection.id, requirement_data
    )
    return requirement


@pytest.fixture
def created_charge_recommendation(
    created_inspection, created_charge_recommendation_inspection_requirement, mocker
):
    """Create and return a Charge Recommendation."""
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

    charge_recommendation_data = copy.copy(
        ChargeRecommendationScenario.default_value.value
    )
    charge_recommendation_data["inspection_id"] = created_inspection.id
    charge_recommendation_data["inspection_requirement_ids"] = [
        created_charge_recommendation_inspection_requirement.id
    ]

    # Use the service layer to create the charge recommendation (handles requirements properly)
    charge_recommendation = ChargeRecommendationService.create_charge_recommendation(
        charge_recommendation_data
    )
    return charge_recommendation


@pytest.fixture
def created_charge_recommendation_requirement_map(
    created_charge_recommendation, created_inspection_requirement, session
):
    """Create and return a Charge Recommendation Inspection Requirement Map."""
    charge_recommendation_requirement_map = (
        ChargeRecommendationInspectionRequirementMap(
            charge_recommendation_id=created_charge_recommendation.id,
            inspection_requirement_id=created_inspection_requirement.id,
        )
    )
    charge_recommendation_requirement_map.save()
    session.commit()
    return charge_recommendation_requirement_map


@pytest.fixture
def created_charge_recommendation_drafting(app, db, created_inspection):
    """Return a charge recommendation in DRAFTING status."""
    charge_recommendation = ChargeRecommendationModel(
        inspection_id=created_inspection.id,
        charge_recommendation_number=f"TEST-CR-DRAFT-{random.randint(100000, 999999)}",
        status=ChargeRecommendationStatusEnum.DRAFTING,
        is_active=True,
        is_deleted=False,
    )
    db.session.add(charge_recommendation)
    db.session.commit()
    return charge_recommendation


@pytest.fixture
def created_charge_recommendation_deputy_review(app, db, created_inspection):
    """Return a charge recommendation in DEPUTY_REVIEW status."""
    from datetime import datetime, timezone

    charge_recommendation = ChargeRecommendationModel(
        inspection_id=created_inspection.id,
        charge_recommendation_number=f"TEST-CR-DEPUTY-{random.randint(100000, 999999)}",
        status=ChargeRecommendationStatusEnum.DEPUTY_REVIEW,
        date_to_crown_counsel=datetime.now(timezone.utc),
        is_active=True,
        is_deleted=False,
    )
    db.session.add(charge_recommendation)
    db.session.commit()
    return charge_recommendation


@pytest.fixture
def created_charge_recommendation_submitted(app, db, created_inspection):
    """Return a charge recommendation in SUBMITTED_TO_CROWN_COUNSEL status."""
    from datetime import datetime, timezone

    from compliance_api.models.charge_recommendation import ChargeDecisionEnum

    charge_recommendation = ChargeRecommendationModel(
        inspection_id=created_inspection.id,
        charge_recommendation_number=f"TEST-CR-SUBMIT-{random.randint(100000, 999999)}",
        status=ChargeRecommendationStatusEnum.SUBMITTED_TO_CROWN_COUNSEL,
        date_to_crown_counsel=datetime.now(timezone.utc),
        charge_decision=ChargeDecisionEnum.APPROVED,
        charge_decision_date=datetime.now(timezone.utc),
        is_active=True,
        is_deleted=False,
    )
    db.session.add(charge_recommendation)
    db.session.commit()
    return charge_recommendation


@pytest.fixture
def created_charge_recommendation_not_proceeding(app, db, created_inspection):
    """Return a charge recommendation in CEB_NOT_PROCEEDING status."""
    from datetime import datetime, timezone

    from compliance_api.models.charge_recommendation import ChargeDecisionEnum

    charge_recommendation = ChargeRecommendationModel(
        inspection_id=created_inspection.id,
        charge_recommendation_number=f"TEST-CR-NOTPROC-{random.randint(100000, 999999)}",
        status=ChargeRecommendationStatusEnum.CEB_NOT_PROCEEDING,
        charge_decision=ChargeDecisionEnum.NOT_PROCEEDING,
        charge_decision_date=datetime.now(timezone.utc),
        is_active=True,
        is_deleted=False,
    )
    db.session.add(charge_recommendation)
    db.session.commit()
    return charge_recommendation


@pytest.fixture
def created_charge_recommendation_with_court_details(app, db, created_inspection):
    """Return a charge recommendation with complete court details."""
    from datetime import datetime, timezone

    from compliance_api.models.charge_recommendation import ChargeDecisionEnum, CourtDecisionEnum
    from compliance_api.models.cr_sentence_type_mapping import CRSentenceTypeMapping
    from compliance_api.models.sentence_type_option import SentenceTypeOption

    charge_recommendation = ChargeRecommendationModel(
        inspection_id=created_inspection.id,
        charge_recommendation_number=f"TEST-CR-COURT-{random.randint(100000, 999999)}",
        status=ChargeRecommendationStatusEnum.SUBMITTED_TO_CROWN_COUNSEL,
        date_to_crown_counsel=datetime.now(timezone.utc),
        charge_decision=ChargeDecisionEnum.APPROVED,
        charge_decision_date=datetime.now(timezone.utc),
        court_file_number="CF-2024-TEST-001",
        court_decision=CourtDecisionEnum.GUILTY,
        court_decision_date=datetime.now(timezone.utc),
        sentence_date=datetime.now(timezone.utc),
        is_active=True,
        is_deleted=False,
    )
    db.session.add(charge_recommendation)
    db.session.commit()

    # Create sentence type mappings (assuming Fine option exists with ID 1)
    # Get or create a sentence type option for testing
    sentence_type_option = (
        db.session.query(SentenceTypeOption).filter_by(name="Fine").first()
    )
    if not sentence_type_option:
        sentence_type_option = SentenceTypeOption(
            name="Fine",
            sort_order=1,
            is_active=True,
            is_deleted=False,
            created_by="system",
            updated_by="system",
        )
        db.session.add(sentence_type_option)
        db.session.commit()

    # Create the mapping between charge recommendation and sentence type
    sentence_mapping = CRSentenceTypeMapping(
        charge_recommendation_id=charge_recommendation.id,
        sentence_type_option_id=sentence_type_option.id,
        is_active=True,
        is_deleted=False,
        created_by="system",
        updated_by="system",
    )
    db.session.add(sentence_mapping)
    db.session.commit()

    return charge_recommendation
