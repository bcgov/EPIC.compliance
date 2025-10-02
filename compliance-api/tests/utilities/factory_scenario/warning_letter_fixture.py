"""Fixtures for Warning Letter tests."""

import copy
import random
from datetime import datetime, timezone

import pytest

from compliance_api.models.warning_letter import WarningLetter as WarningLetterModel
from compliance_api.models.warning_letter import (
    WarningLetterInspectionRequirementMap, WarningLetterProgressEnum, WarningLetterStatusEnum)
from compliance_api.services.warning_letter.warning_letter import WarningLetterService
from tests.utilities.factory_scenario.warning_letter_scenario import WarningLetterScenario


@pytest.fixture
def created_warning_letter_inspection_requirement(app, db, created_inspection):
    """Create an inspection requirement for warning letter testing."""
    from compliance_api.models import (
        InspectionReqEnforcementMap, InspectionReqSourceDetail, InspectionRequirement, InspectionRequirementTypeEnum,
        RequirementSourceEnum)

    # Create requirement directly in database
    requirement = InspectionRequirement(
        inspection_id=created_inspection.id,
        summary="Warning letter requirement summary",
        topic_id=1,
        req_type=InspectionRequirementTypeEnum.REQ,
        compliance_finding_id=1,
        findings="Warning letter requirement finding",
        sort_order=1,
        is_active=True,
        is_deleted=False,
    )
    db.session.add(requirement)
    db.session.flush()  # Get the ID

    # Add enforcement action mapping for WARNING_LETTER (ID 4)
    enforcement_action_map = InspectionReqEnforcementMap(
        enforcement_action_id=4,  # WARNING_LETTER
        requirement_id=requirement.id,
    )
    db.session.add(enforcement_action_map)

    # Add requirement source details
    source_detail = InspectionReqSourceDetail(
        requirement_id=requirement.id,
        requirement_source_id=RequirementSourceEnum.ACT_2018.value,
        section_number="1.1",
        condition_number="",
        amendment_number="",
        source_title="Warning letter requirement source title",
        description="Warning letter requirement source description",
    )
    db.session.add(source_detail)

    db.session.commit()
    return requirement


@pytest.fixture
def created_warning_letter(
    app, db, created_inspection, created_warning_letter_inspection_requirement, mocker
):
    """Create and return a Warning Letter."""
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

    # Ensure the requirement is committed to the database
    db.session.commit()

    warning_letter_data = copy.copy(WarningLetterScenario.default_value.value)
    warning_letter_data["inspection_id"] = created_inspection.id
    warning_letter_data["warning_letter_number"] = (
        f"WL-FIXTURE-{random.randint(100000, 999999)}"
    )
    warning_letter_data["inspection_requirement_ids"] = [
        created_warning_letter_inspection_requirement.id
    ]
    # Use the service layer to create the warning letter (handles requirements properly)
    warning_letter = WarningLetterService.create_warning_letter(warning_letter_data)
    return warning_letter


@pytest.fixture
def created_warning_letter_requirement_map(
    created_warning_letter, created_inspection_requirement, session
):
    """Create and return a Warning Letter Inspection Requirement Map."""
    warning_letter_requirement_map = WarningLetterInspectionRequirementMap(
        warning_letter_id=created_warning_letter.id,
        inspection_requirement_id=created_inspection_requirement.id,
    )
    warning_letter_requirement_map.save()
    session.commit()
    return warning_letter_requirement_map


@pytest.fixture
def created_warning_letter_created(
    app, db, created_inspection, created_warning_letter_inspection_requirement
):
    """Return a warning letter in CREATED status."""
    warning_letter = WarningLetterModel(
        inspection_id=created_inspection.id,
        warning_letter_number=f"TEST-WL-CREATED-{random.randint(100000, 999999)}",
        issuing_officer_id=created_inspection.primary_officer_id,
        content="Test warning letter content in CREATED status",
        status=WarningLetterStatusEnum.CREATED,
        progress=WarningLetterProgressEnum.DRAFTING,
        is_active=True,
        is_deleted=False,
    )
    db.session.add(warning_letter)
    db.session.flush()

    # Create the requirement mapping
    from compliance_api.models.warning_letter import WarningLetterInspectionRequirementMap

    requirement_map = WarningLetterInspectionRequirementMap(
        warning_letter_id=warning_letter.id,
        inspection_requirement_id=created_warning_letter_inspection_requirement.id,
    )
    db.session.add(requirement_map)
    db.session.commit()
    return warning_letter


@pytest.fixture
def created_warning_letter_issued(
    app, db, created_inspection, created_warning_letter_inspection_requirement
):
    """Return a warning letter in ISSUED status."""
    warning_letter = WarningLetterModel(
        inspection_id=created_inspection.id,
        warning_letter_number=f"TEST-WL-ISSUED-{random.randint(100000, 999999)}",
        issuing_officer_id=created_inspection.primary_officer_id,
        content="Test warning letter content in ISSUED status",
        date_issued=datetime.now(timezone.utc),
        intended_issuance_date=datetime.now(timezone.utc),
        status=WarningLetterStatusEnum.ISSUED,
        progress=WarningLetterProgressEnum.ISSUED,
        is_active=True,
        is_deleted=False,
    )
    db.session.add(warning_letter)
    db.session.flush()

    # Create the requirement mapping
    from compliance_api.models.warning_letter import WarningLetterInspectionRequirementMap

    requirement_map = WarningLetterInspectionRequirementMap(
        warning_letter_id=warning_letter.id,
        inspection_requirement_id=created_warning_letter_inspection_requirement.id,
    )
    db.session.add(requirement_map)
    db.session.commit()
    return warning_letter


@pytest.fixture
def created_warning_letter_drafting(
    app, db, created_inspection, created_warning_letter_inspection_requirement
):
    """Return a warning letter in DRAFTING progress."""
    warning_letter = WarningLetterModel(
        inspection_id=created_inspection.id,
        warning_letter_number=f"TEST-WL-DRAFTING-{random.randint(100000, 999999)}",
        issuing_officer_id=created_inspection.primary_officer_id,
        content="Test warning letter content in DRAFTING progress",
        status=WarningLetterStatusEnum.CREATED,
        progress=WarningLetterProgressEnum.DRAFTING,
        is_active=True,
        is_deleted=False,
    )
    db.session.add(warning_letter)
    db.session.flush()

    # Create the requirement mapping
    from compliance_api.models.warning_letter import WarningLetterInspectionRequirementMap

    requirement_map = WarningLetterInspectionRequirementMap(
        warning_letter_id=warning_letter.id,
        inspection_requirement_id=created_warning_letter_inspection_requirement.id,
    )
    db.session.add(requirement_map)
    db.session.commit()
    return warning_letter


@pytest.fixture
def created_warning_letter_deputy_review(
    app, db, created_inspection, created_warning_letter_inspection_requirement
):
    """Return a warning letter in DEPUTY_REVIEW progress."""
    warning_letter = WarningLetterModel(
        inspection_id=created_inspection.id,
        warning_letter_number=f"TEST-WL-DEPUTY-{random.randint(100000, 999999)}",
        issuing_officer_id=created_inspection.primary_officer_id,
        content="Test warning letter content in DEPUTY_REVIEW progress",
        status=WarningLetterStatusEnum.CREATED,
        progress=WarningLetterProgressEnum.DEPUTY_REVIEW,
        is_active=True,
        is_deleted=False,
    )
    db.session.add(warning_letter)
    db.session.flush()

    # Create the requirement mapping
    from compliance_api.models.warning_letter import WarningLetterInspectionRequirementMap

    requirement_map = WarningLetterInspectionRequirementMap(
        warning_letter_id=warning_letter.id,
        inspection_requirement_id=created_warning_letter_inspection_requirement.id,
    )
    db.session.add(requirement_map)
    db.session.commit()
    return warning_letter


@pytest.fixture
def created_warning_letter_approved(
    app, db, created_inspection, created_warning_letter_inspection_requirement
):
    """Return a warning letter in APPROVED progress."""
    warning_letter = WarningLetterModel(
        inspection_id=created_inspection.id,
        warning_letter_number=f"TEST-WL-APPROVED-{random.randint(100000, 999999)}",
        issuing_officer_id=created_inspection.primary_officer_id,
        content="Test warning letter content in APPROVED progress",
        intended_issuance_date=datetime.now(timezone.utc),
        status=WarningLetterStatusEnum.CREATED,
        progress=WarningLetterProgressEnum.APPROVED,
        is_active=True,
        is_deleted=False,
    )
    db.session.add(warning_letter)
    db.session.flush()

    # Create the requirement mapping
    from compliance_api.models.warning_letter import WarningLetterInspectionRequirementMap

    requirement_map = WarningLetterInspectionRequirementMap(
        warning_letter_id=warning_letter.id,
        inspection_requirement_id=created_warning_letter_inspection_requirement.id,
    )
    db.session.add(requirement_map)
    db.session.commit()
    return warning_letter


@pytest.fixture
def created_warning_letter_with_content(
    app, db, created_inspection, created_warning_letter_inspection_requirement
):
    """Return a warning letter with specific content."""
    warning_letter = WarningLetterModel(
        inspection_id=created_inspection.id,
        warning_letter_number=f"TEST-WL-CONTENT-{random.randint(100000, 999999)}",
        issuing_officer_id=created_inspection.primary_officer_id,
        content="This is a detailed warning letter content for testing purposes with specific compliance requirements.",
        intended_issuance_date=datetime.now(timezone.utc),
        status=WarningLetterStatusEnum.CREATED,
        progress=WarningLetterProgressEnum.DRAFTING,
        is_active=True,
        is_deleted=False,
    )
    db.session.add(warning_letter)
    db.session.flush()

    # Create the requirement mapping
    from compliance_api.models.warning_letter import WarningLetterInspectionRequirementMap

    requirement_map = WarningLetterInspectionRequirementMap(
        warning_letter_id=warning_letter.id,
        inspection_requirement_id=created_warning_letter_inspection_requirement.id,
    )
    db.session.add(requirement_map)
    db.session.commit()
    return warning_letter


@pytest.fixture
def created_warning_letter_with_officer(
    app,
    db,
    created_inspection,
    created_staff,
    created_warning_letter_inspection_requirement,
):
    """Return a warning letter with specific issuing officer."""
    warning_letter = WarningLetterModel(
        inspection_id=created_inspection.id,
        warning_letter_number=f"TEST-WL-OFFICER-{random.randint(100000, 999999)}",
        issuing_officer_id=created_staff.id,
        content="Warning letter with specific issuing officer for testing.",
        status=WarningLetterStatusEnum.CREATED,
        progress=WarningLetterProgressEnum.DRAFTING,
        is_active=True,
        is_deleted=False,
    )
    db.session.add(warning_letter)
    db.session.flush()

    # Create the requirement mapping
    from compliance_api.models.warning_letter import WarningLetterInspectionRequirementMap

    requirement_map = WarningLetterInspectionRequirementMap(
        warning_letter_id=warning_letter.id,
        inspection_requirement_id=created_warning_letter_inspection_requirement.id,
    )
    db.session.add(requirement_map)
    db.session.commit()
    return warning_letter


@pytest.fixture
def created_warning_letter_minimal(
    app, db, created_inspection, created_warning_letter_inspection_requirement
):
    """Return a minimal warning letter for testing."""
    warning_letter = WarningLetterModel(
        inspection_id=created_inspection.id,
        warning_letter_number=f"TEST-WL-MINIMAL-{random.randint(100000, 999999)}",
        issuing_officer_id=created_inspection.primary_officer_id,
        content="Minimal warning letter content for testing.",
        status=WarningLetterStatusEnum.CREATED,
        progress=WarningLetterProgressEnum.DRAFTING,
        is_active=True,
        is_deleted=False,
    )
    db.session.add(warning_letter)
    db.session.flush()

    # Create the requirement mapping
    from compliance_api.models.warning_letter import WarningLetterInspectionRequirementMap

    requirement_map = WarningLetterInspectionRequirementMap(
        warning_letter_id=warning_letter.id,
        inspection_requirement_id=created_warning_letter_inspection_requirement.id,
    )
    db.session.add(requirement_map)
    db.session.commit()
    return warning_letter
