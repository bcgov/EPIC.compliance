"""Condition column on the Requirements Grid shows the Condition/Section number (COMP-963)."""
from types import SimpleNamespace

import pytest

from compliance_api.models.requirement_source import RequirementSourceEnum
from compliance_api.services.service_utils import ServiceUtils


def _detail(source: RequirementSourceEnum, **numbers):
    """Return a stand-in requirement source detail with every number field populated distinctly."""
    fields = {
        "section_number": "S1",
        "condition_number": "C1",
        "clause_number": "CL1",
        "amendment_number": "A1",
        "regulation_number": "R1",
    }
    fields.update(numbers)
    return SimpleNamespace(
        requirement_source_id=source.value,
        order=SimpleNamespace(order_number="O1"),
        **fields,
    )


@pytest.mark.parametrize(
    "source, expected",
    [
        (RequirementSourceEnum.EAC_AMENDMENT, "C1"),
        (RequirementSourceEnum.REGULATION, "S1"),
        # Unchanged sources
        (RequirementSourceEnum.ACT_2002, "S1"),
        (RequirementSourceEnum.ACT_2018, "S1"),
        (RequirementSourceEnum.CERTIFIED_PROJECT_DESCRIPTION, "S1"),
        (RequirementSourceEnum.COMPLIANCE_AGREEMENT, "S1"),
        (RequirementSourceEnum.OTHER, "S1"),
        (RequirementSourceEnum.EAC_CERTIFICATE, "C1"),
        (RequirementSourceEnum.SCHEDULE_B, "C1"),
        (RequirementSourceEnum.ORDER, "O1"),
        (RequirementSourceEnum.EXEMPTION_ORDER, "CL1"),
    ],
)
def test_grid_source_number_field(source, expected):
    """Each requirement source shows its number in the grid Condition column."""
    assert ServiceUtils.get_requirement_grid_source_number_field(_detail(source)) == expected
