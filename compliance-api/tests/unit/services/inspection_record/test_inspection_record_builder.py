"""Tests for InspectionRecordDataBuilder enforcement summary generation."""
from compliance_api.models import db
from compliance_api.models.administrative_penalty import (
    AdministrativePenalty,
    AdministrativePenaltyInspectionRequirementMap,
    ReferralStatusEnum,
)
from compliance_api.models.inspection import InspectionRequirement, InspectionRequirementTypeEnum
from compliance_api.models.inspection.inspection_req_enforcement_map import InspectionReqEnforcementMap
from compliance_api.models.inspection.inspection_req_source_detail import InspectionReqSourceDetail
from compliance_api.models.inspection_record import IRStatusEnum
from compliance_api.models.requirement_source import RequirementSourceEnum
from compliance_api.services.inspection_record.inspection_record_builder import InspectionRecordDataBuilder


class TestEnforcementSummaryAPHandling:
    """Tests for standalone vs. combined AP phrasing in build_enforcement_summary."""

    _PROJECT_DETAILS = {
        "proponent": "Test Mining Ltd.",
        "eac_certificate": "M99-01",
        "name": "Test Mine Project",
    }

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _create_ap_requirement(self, inspection_id, sort_order=1):
        """Create a non-compliant requirement with AP enforcement action and source details."""
        requirement = InspectionRequirement(
            inspection_id=inspection_id,
            summary="AP requirement summary",
            topic_id=1,
            req_type=InspectionRequirementTypeEnum.REQ,
            compliance_finding_id=1,
            findings="AP requirement finding",
            sort_order=sort_order,
            is_active=True,
            is_deleted=False,
        )
        db.session.add(requirement)
        db.session.flush()

        db.session.add(InspectionReqEnforcementMap(
            enforcement_action_id=6,  # ADMINISTRATIVE_PENALTY_RECOMMENDATION
            requirement_id=requirement.id,
        ))

        # SCHEDULE_B yields "Condition <condition_number>" via get_requirement_source_number_field
        db.session.add(InspectionReqSourceDetail(
            requirement_id=requirement.id,
            requirement_source_id=RequirementSourceEnum.SCHEDULE_B.value,
            condition_number="21",
            source_title="Schedule B - Table of Conditions",
            description="AP source description",
        ))

        db.session.commit()
        return requirement

    def _create_ap_record(self, inspection_id, requirement_id):
        """Create an AdministrativePenalty linked to the given requirement."""
        ap = AdministrativePenalty(
            inspection_id=inspection_id,
            referral_status=ReferralStatusEnum.PREPARING_REFERRAL_FOR_AEO,
        )
        db.session.add(ap)
        db.session.flush()

        db.session.add(AdministrativePenaltyInspectionRequirementMap(
            administrative_penalty_id=ap.id,
            inspection_requirement_id=requirement_id,
        ))
        db.session.commit()
        return ap

    def _create_wl_requirement(self, inspection_id, sort_order=2):
        """Create a requirement with WARNING_LETTER enforcement action (no WL record needed)."""
        requirement = InspectionRequirement(
            inspection_id=inspection_id,
            summary="WL requirement summary",
            topic_id=1,
            req_type=InspectionRequirementTypeEnum.REQ,
            compliance_finding_id=1,
            findings="WL requirement finding",
            sort_order=sort_order,
            is_active=True,
            is_deleted=False,
        )
        db.session.add(requirement)
        db.session.flush()

        db.session.add(InspectionReqEnforcementMap(
            enforcement_action_id=4,  # WARNING_LETTER
            requirement_id=requirement.id,
        ))
        db.session.commit()
        return requirement

    def _build_enforcement_summary(self, inspection):
        """Instantiate the builder, pre-populate project_details, and run build_enforcement_summary."""
        builder = InspectionRecordDataBuilder(inspection, IRStatusEnum.FINAL.value)
        builder.data["project_details"] = self._PROJECT_DETAILS
        builder.build_enforcement_summary()
        return builder.data.get("enforcement_summary", "")

    # -------------------------------------------------------------------------
    # Scenario 1a: Standalone AP — no AP record created yet
    # -------------------------------------------------------------------------

    def test_standalone_ap_no_record_omits_in_addition(self, created_inspection, mocker):
        """Standalone AP with no AP record must not use additive phrasing."""
        mocker.patch("compliance_api.auth.jwt.contains_role", return_value=True)

        self._create_ap_requirement(created_inspection.id)

        summary = self._build_enforcement_summary(created_inspection)

        assert "In Addition" not in summary

    def test_standalone_ap_no_record_includes_non_compliance_statement(self, created_inspection, mocker):
        """Standalone AP with no AP record must generate a full non-compliance statement."""
        mocker.patch("compliance_api.auth.jwt.contains_role", return_value=True)

        self._create_ap_requirement(created_inspection.id)

        summary = self._build_enforcement_summary(created_inspection)

        # Template wraps between "is not" and "compliant with", so check each side of the break
        assert "is not" in summary
        assert "compliant with" in summary
        assert "may be referred to a decision maker" in summary
        assert "Administrative Penalty" in summary

    # -------------------------------------------------------------------------
    # Scenario 1b: Standalone AP — AP record exists
    # -------------------------------------------------------------------------

    def test_standalone_ap_with_record_omits_in_addition(self, created_inspection, mocker):
        """Standalone AP with an AP record must still not use additive phrasing."""
        mocker.patch("compliance_api.auth.jwt.contains_role", return_value=True)

        requirement = self._create_ap_requirement(created_inspection.id)
        self._create_ap_record(created_inspection.id, requirement.id)

        summary = self._build_enforcement_summary(created_inspection)

        assert "In Addition" not in summary

    def test_standalone_ap_with_record_references_requirement_number(self, created_inspection, mocker):
        """Standalone AP summary must reference the correct requirement position number."""
        mocker.patch("compliance_api.auth.jwt.contains_role", return_value=True)

        # Create two plain REQ requirements before the AP requirement so the AP
        # requirement ends up as the 3rd REQ when numbered by position.
        for sort_order in (1, 2):
            req = InspectionRequirement(
                inspection_id=created_inspection.id,
                summary=f"Plain requirement {sort_order}",
                topic_id=1,
                req_type=InspectionRequirementTypeEnum.REQ,
                compliance_finding_id=1,
                findings="finding",
                sort_order=sort_order,
                is_active=True,
                is_deleted=False,
            )
            db.session.add(req)
        db.session.commit()

        requirement = self._create_ap_requirement(created_inspection.id, sort_order=3)
        self._create_ap_record(created_inspection.id, requirement.id)

        summary = self._build_enforcement_summary(created_inspection)

        assert "Requirement 3" in summary

    # -------------------------------------------------------------------------
    # Scenario 2: AP alongside another special enforcement action
    # -------------------------------------------------------------------------

    def test_ap_with_warning_letter_uses_additive_phrasing(self, created_inspection, mocker):
        """AP present alongside WARNING_LETTER must retain 'In Addition' phrasing."""
        mocker.patch("compliance_api.auth.jwt.contains_role", return_value=True)

        ap_requirement = self._create_ap_requirement(created_inspection.id, sort_order=1)
        self._create_ap_record(created_inspection.id, ap_requirement.id)
        self._create_wl_requirement(created_inspection.id, sort_order=2)

        summary = self._build_enforcement_summary(created_inspection)

        assert "In Addition" in summary


class TestRequirementNumberingWithRegulatoryConsideration:
    """Regulatory Considerations must not consume a Requirement number in enforcement summaries."""

    _PROJECT_DETAILS = {
        "proponent": "Test Mining Ltd.",
        "eac_certificate": "M99-01",
        "name": "Test Mine Project",
    }

    def _create_reg_consideration(self, inspection_id, sort_order):
        """Create a Regulatory Consideration (REG type) with no enforcement action."""
        reg = InspectionRequirement(
            inspection_id=inspection_id,
            summary="Regulatory consideration summary",
            topic_id=1,
            req_type=InspectionRequirementTypeEnum.REG,
            compliance_finding_id=1,
            findings="Regulatory findings",
            sort_order=sort_order,
            is_active=True,
            is_deleted=False,
        )
        db.session.add(reg)
        db.session.commit()
        return reg

    def _create_ap_requirement(self, inspection_id, sort_order):
        """Create a REQ with AP enforcement action and a Schedule B source detail."""
        requirement = InspectionRequirement(
            inspection_id=inspection_id,
            summary="AP requirement summary",
            topic_id=1,
            req_type=InspectionRequirementTypeEnum.REQ,
            compliance_finding_id=1,
            findings="AP requirement finding",
            sort_order=sort_order,
            is_active=True,
            is_deleted=False,
        )
        db.session.add(requirement)
        db.session.flush()

        db.session.add(InspectionReqEnforcementMap(
            enforcement_action_id=6,  # ADMINISTRATIVE_PENALTY_RECOMMENDATION
            requirement_id=requirement.id,
        ))
        db.session.add(InspectionReqSourceDetail(
            requirement_id=requirement.id,
            requirement_source_id=RequirementSourceEnum.SCHEDULE_B.value,
            condition_number="5",
            source_title="Schedule B - Table of Conditions",
            description="Source description",
        ))
        db.session.commit()
        return requirement

    def _create_ap_record(self, inspection_id, requirement_id):
        """Create an AdministrativePenalty linked to the given requirement."""
        ap = AdministrativePenalty(
            inspection_id=inspection_id,
            referral_status=ReferralStatusEnum.PREPARING_REFERRAL_FOR_AEO,
        )
        db.session.add(ap)
        db.session.flush()
        db.session.add(AdministrativePenaltyInspectionRequirementMap(
            administrative_penalty_id=ap.id,
            inspection_requirement_id=requirement_id,
        ))
        db.session.commit()
        return ap

    def _build_enforcement_summary(self, inspection):
        builder = InspectionRecordDataBuilder(inspection, IRStatusEnum.FINAL.value)
        builder.data["project_details"] = self._PROJECT_DETAILS
        builder.build_enforcement_summary()
        return builder.data.get("enforcement_summary", "")

    def test_reg_created_before_req_does_not_shift_requirement_number(
        self, created_inspection, mocker
    ):
        """Scenario 2 from the bug report: REG at sort_order=1 must not push the first REQ to 'Requirement 2'."""
        mocker.patch("compliance_api.auth.jwt.contains_role", return_value=True)

        # REG is created first and gets sort_order=1
        self._create_reg_consideration(created_inspection.id, sort_order=1)
        # The only REQ gets sort_order=2, but it is the 1st REQ by position
        req = self._create_ap_requirement(created_inspection.id, sort_order=2)
        self._create_ap_record(created_inspection.id, req.id)

        summary = self._build_enforcement_summary(created_inspection)

        assert "Requirement 1" in summary
        assert "Requirement 2" not in summary

    def test_reg_in_middle_does_not_create_numbering_gap(
        self, created_inspection, mocker
    ):
        """REG between two REQs must not skip a number — second REQ must be 'Requirement 2'."""
        mocker.patch("compliance_api.auth.jwt.contains_role", return_value=True)

        # First REQ (no AP)
        plain_req = InspectionRequirement(
            inspection_id=created_inspection.id,
            summary="Plain requirement",
            topic_id=1,
            req_type=InspectionRequirementTypeEnum.REQ,
            compliance_finding_id=1,
            findings="finding",
            sort_order=1,
            is_active=True,
            is_deleted=False,
        )
        db.session.add(plain_req)
        db.session.commit()

        # REG in the middle
        self._create_reg_consideration(created_inspection.id, sort_order=2)

        # Second REQ with AP gets sort_order=3 but is the 2nd REQ by position
        req = self._create_ap_requirement(created_inspection.id, sort_order=3)
        self._create_ap_record(created_inspection.id, req.id)

        summary = self._build_enforcement_summary(created_inspection)

        assert "Requirement 2" in summary
        assert "Requirement 3" not in summary

    def test_reg_only_produces_no_enforcement_summary(
        self, created_inspection, mocker
    ):
        """A Regulatory Consideration with no Enforcement Action must not produce an enforcement summary."""
        mocker.patch("compliance_api.auth.jwt.contains_role", return_value=True)

        self._create_reg_consideration(created_inspection.id, sort_order=1)

        summary = self._build_enforcement_summary(created_inspection)

        assert summary == ""

    def test_reg_is_not_referenced_alongside_enforcement_action(
        self, created_inspection, mocker
    ):
        """The enforcement summary must not reference Regulatory Considerations even when an action exists."""
        mocker.patch("compliance_api.auth.jwt.contains_role", return_value=True)

        self._create_reg_consideration(created_inspection.id, sort_order=1)
        req = self._create_ap_requirement(created_inspection.id, sort_order=2)
        self._create_ap_record(created_inspection.id, req.id)

        summary = self._build_enforcement_summary(created_inspection)

        assert "Regulatory Considerations" not in summary
