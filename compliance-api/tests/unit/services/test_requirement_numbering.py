"""Tests verifying Regulatory Considerations do not affect Requirement display numbering."""
from types import SimpleNamespace

from compliance_api.models.inspection.inspection_requirement import InspectionRequirementTypeEnum
from compliance_api.services.service_utils import ServiceUtils


def _make_req(id, sort_order, req_type=InspectionRequirementTypeEnum.REQ):
    """Return a lightweight stand-in for InspectionRequirement with the fields ServiceUtils reads."""
    return SimpleNamespace(
        id=id,
        sort_order=sort_order,
        req_type=req_type,
        findings="finding",
        summary="summary",
        compliance_finding=None,
        compliance_finding_id=None,
        enforcement_actions=[],
        requirement_source_details=[],
    )


class TestRequirementNumberingExcludesRegulatoryConsiderations:
    """get_formatted_requirement_details must number only REQ types, starting at 1."""

    def test_reg_created_first_does_not_shift_req_numbers(self):
        """Scenario 2 from the bug report: REG before REQ must not push REQ to number 2."""
        requirements = [
            _make_req(id=1, sort_order=1, req_type=InspectionRequirementTypeEnum.REG),
            _make_req(id=2, sort_order=2, req_type=InspectionRequirementTypeEnum.REQ),
        ]

        result = ServiceUtils.get_formatted_requirement_details(requirements)

        assert len(result) == 1
        assert result[0]["sort_order"] == 1

    def test_reg_after_reqs_does_not_affect_numbering(self):
        """REG appended after REQs must not appear in results or disturb numbering."""
        requirements = [
            _make_req(id=1, sort_order=1, req_type=InspectionRequirementTypeEnum.REQ),
            _make_req(id=2, sort_order=2, req_type=InspectionRequirementTypeEnum.REQ),
            _make_req(id=3, sort_order=3, req_type=InspectionRequirementTypeEnum.REG),
        ]

        result = ServiceUtils.get_formatted_requirement_details(requirements)

        assert len(result) == 2
        assert result[0]["sort_order"] == 1
        assert result[1]["sort_order"] == 2

    def test_reg_between_reqs_preserves_sequential_numbering(self):
        """REG sandwiched between REQs must not create a gap in the requirement numbers."""
        requirements = [
            _make_req(id=1, sort_order=1, req_type=InspectionRequirementTypeEnum.REQ),
            _make_req(id=2, sort_order=2, req_type=InspectionRequirementTypeEnum.REG),
            _make_req(id=3, sort_order=3, req_type=InspectionRequirementTypeEnum.REQ),
        ]

        result = ServiceUtils.get_formatted_requirement_details(requirements)

        assert len(result) == 2
        assert result[0]["sort_order"] == 1
        assert result[1]["sort_order"] == 2

    def test_reg_not_included_in_result(self):
        """REG type must never appear in the formatted requirement details."""
        requirements = [
            _make_req(id=1, sort_order=1, req_type=InspectionRequirementTypeEnum.REG),
            _make_req(id=2, sort_order=2, req_type=InspectionRequirementTypeEnum.REQ),
        ]

        result = ServiceUtils.get_formatted_requirement_details(requirements)

        requirement_ids = [r["requirement_id"] for r in result]
        assert 1 not in requirement_ids  # REG id
        assert 2 in requirement_ids      # REQ id

    def test_multiple_reqs_with_reg_first_numbered_correctly(self):
        """Three REQs preceded by a REG must be numbered 1, 2, 3."""
        requirements = [
            _make_req(id=1, sort_order=1, req_type=InspectionRequirementTypeEnum.REG),
            _make_req(id=2, sort_order=2, req_type=InspectionRequirementTypeEnum.REQ),
            _make_req(id=3, sort_order=3, req_type=InspectionRequirementTypeEnum.REQ),
            _make_req(id=4, sort_order=4, req_type=InspectionRequirementTypeEnum.REQ),
        ]

        result = ServiceUtils.get_formatted_requirement_details(requirements)

        assert len(result) == 3
        assert [r["sort_order"] for r in result] == [1, 2, 3]
