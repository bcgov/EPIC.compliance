"""Requirement sources and condition numbers in enforcement documents follow the dropdown order (COMP-953)."""
from datetime import date
from types import SimpleNamespace

import pytest

from compliance_api.models.inspection.inspection_requirement import InspectionRequirementTypeEnum
from compliance_api.models.requirement_source import RequirementSourceEnum
from compliance_api.services.order import order as order_module
from compliance_api.services.service_utils import ServiceUtils
from compliance_api.services.warning_letter import warning_letter as warning_letter_module


EC_CERTIFICATE = SimpleNamespace(id=RequirementSourceEnum.EAC_CERTIFICATE.value, name="EC Certificate", sort_order=2)
EC_AMENDMENT = SimpleNamespace(id=RequirementSourceEnum.EAC_AMENDMENT.value, name="EC Amendment", sort_order=3)
SCHEDULE_B = SimpleNamespace(id=RequirementSourceEnum.SCHEDULE_B.value, name="Schedule B", sort_order=5)


def _make_req(id, source, condition_number):
    """Return a lightweight stand-in for InspectionRequirement with one requirement source detail."""
    detail = SimpleNamespace(
        requirement_source=source,
        requirement_source_id=source.id,
        condition_number=condition_number,
        section_number=None,
        amendment_number="A1",
        title="title",
        source_title=source.name,
        appendix=None,
        description="description",
        documents=[],
        images=[],
        order=None,
    )
    return SimpleNamespace(
        id=id,
        sort_order=id,
        req_type=InspectionRequirementTypeEnum.REQ,
        findings="finding",
        summary=f"summary {id}",
        compliance_finding=None,
        compliance_finding_id=None,
        enforcement_actions=[],
        requirement_source_details=[detail],
    )


LINKED_REQUIREMENTS = [
    _make_req(1, SCHEDULE_B, "77"),
    _make_req(2, EC_AMENDMENT, "12"),
    _make_req(3, SCHEDULE_B, "17"),
    _make_req(4, SCHEDULE_B, "1"),
    _make_req(5, EC_CERTIFICATE, "1"),
]

INSPECTION = SimpleNamespace(
    id=1,
    case_file=SimpleNamespace(id=1, project_id=1),
    types=[SimpleNamespace(type=SimpleNamespace(name="Field"))],
    start_date=date(2026, 9, 9),
    end_date=None,
    ir_number="ABC_IR001",
    primary_officer=SimpleNamespace(first_name="Pat", last_name="Lee"),
    primary_officer_id=1,
)


@pytest.fixture
def captured(monkeypatch):
    """Stub the database lookups and capture the data each document template is rendered with."""
    rendered = {}

    def fake_render(name, _template, data):
        rendered[name] = data
        return ""

    monkeypatch.setattr(ServiceUtils, "get_project_details", staticmethod(lambda *_: {}))
    for module in (order_module, warning_letter_module):
        monkeypatch.setattr(module, "render_template_with_data", fake_render)
        monkeypatch.setattr(
            module.InspectionRequirementModel,
            "get_requirement_by_ids",
            classmethod(lambda cls, ids: [r for r in rendered["requirements"] if r.id in ids]),
        )
    section = SimpleNamespace(name="53", act="Act")
    monkeypatch.setattr(order_module.SectionModel, "find_by_id", classmethod(lambda cls, _id: section))
    officer = SimpleNamespace(first_name="Pat", last_name="Lee", position=SimpleNamespace(name="Officer"))
    monkeypatch.setattr(warning_letter_module.StaffUserModel, "find_by_id", classmethod(lambda cls, _id: officer))
    department = SimpleNamespace(email="a@b.c", phone="555-5555")
    monkeypatch.setattr(
        warning_letter_module,
        "DepartmentDetailModel",
        SimpleNamespace(query=SimpleNamespace(filter_by=lambda **_: SimpleNamespace(first=lambda: department))),
    )
    rendered["requirements"] = LINKED_REQUIREMENTS
    return rendered


@pytest.mark.parametrize("requirements", [LINKED_REQUIREMENTS, list(reversed(LINKED_REQUIREMENTS))])
def test_warning_letter_condition_lines_follow_dropdown_and_numeric_order(captured, requirements):
    """Sources follow the dropdown order and conditions ascend numerically, whatever order they were linked."""
    captured["requirements"] = requirements

    warning_letter_module._create_content(INSPECTION, [r.id for r in requirements], 1)

    assert captured["WARNING_LETTER_CONTENT"]["condition_lines"] == [
        "Condition 1 of EC Certificate",
        "Condition 12 of EC Amendment",
        "Condition 1, Condition 17, Condition 77 of Schedule B",
    ]


def test_warning_letter_sorts_condition_numbers_numerically_not_as_text(captured):
    """Condition 2 comes before Condition 10 (text sort would put 10 first)."""
    captured["requirements"] = [
        _make_req(1, SCHEDULE_B, "10"),
        _make_req(2, SCHEDULE_B, "9"),
        _make_req(3, SCHEDULE_B, "2"),
    ]

    warning_letter_module._create_content(INSPECTION, [1, 2, 3], 1)

    assert captured["WARNING_LETTER_CONTENT"]["condition_lines"] == [
        "Condition 2, Condition 9, Condition 10 of Schedule B",
    ]


@pytest.mark.parametrize("requirements", [LINKED_REQUIREMENTS, list(reversed(LINKED_REQUIREMENTS))])
def test_order_requirement_details_follow_dropdown_and_numeric_order(captured, requirements):
    """Order WHEREAS lists sources in dropdown order and conditions ascending, whatever order they were linked.

    Asserts the current "{numbers} of {sources}" wording; update if the Order wording changes to grouped lines.
    """
    captured["requirements"] = requirements

    order_module._create_where_as_and_now_therefore(INSPECTION, "ORD001", 1, [r.id for r in requirements])

    details = captured["WHERE_AS"]["requirement_details"]
    assert details["requirement_numbers"].split(", ") == [
        "Condition 1",
        "Condition 12",
        "Condition 1",
        "Condition 17",
        "Condition 77",
    ]
    assert list(dict.fromkeys(details["requirement_sources"].split(", "))) == [
        "EC Certificate",
        "EC Amendment",
        "Schedule B",
    ]
