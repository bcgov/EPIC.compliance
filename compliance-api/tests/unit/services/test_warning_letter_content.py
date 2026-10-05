"""Tests for the warning letter default content template."""
import re

from compliance_api.services.warning_letter.warning_letter_template_constant import WARNING_LETTER_CONTENT
from compliance_api.utils.template_renderer import render_template_with_data


def test_inspection_paragraph_references_certificate():
    """The inspection paragraph names the EA Certificate, not the requirement sources (COMP-937)."""
    data = {
        "project_details": {
            "name": "Eagle Mountain - Woodfibre Gas Pipeline",
            "eac_certificate": "E16-01",
            "proponent": "FortisBC",
            "proponent_label": "Certificate Holder",
        },
        "inspection_details": {
            "start_date": "September 09, 2026",
            "officer_position": "Deputy Director, Compliance & Enforcement Operations",
            "primary_officer_name": "Maria Kuzmenko",
            "inspection_type": "Field",
            "ir_number": "IR001",
        },
        "department_details": {"email": "a@b.c", "phone": "555-5555"},
        "requirement_details": [
            {"requirement_source_number": "Condition 5", "requirement_summary": "do things"}
        ],
        "condition_lines": ["Condition 5 of Schedule B"],
    }
    html = render_template_with_data("WARNING_LETTER_CONTENT", WARNING_LETTER_CONTENT, data)
    text = re.sub(r"\s+", " ", html)

    assert (
        "of the Eagle Mountain - Woodfibre Gas Pipeline (Project) against the requirements of "
        "Environmental Assessment Certificate #E16-01 (Certificate)." in text
    )
