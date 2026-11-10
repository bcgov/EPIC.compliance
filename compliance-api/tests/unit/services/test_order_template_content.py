"""Tests for the order WHEREAS template inspection dates (COMP-961)."""
import re

import pytest

from compliance_api.services.order.order_template_constant import WHERE_AS
from compliance_api.utils.template_renderer import render_template_with_data


def _render(start_date, end_date):
    data = {
        "project_details": {"has_certificate": False, "proponent_label": "Proponent"},
        "inspection_details": {
            "start_date": start_date,
            "end_date": end_date,
            "inspection_type": "Field",
            "ir_number": "IR001",
        },
        "order_details": {"section": "53"},
        "requirement_details": {},
    }
    return re.sub(r"\s+", " ", render_template_with_data("WHERE_AS", WHERE_AS, data))


@pytest.mark.parametrize("end_date", ["", None, "September 09, 2026"])
def test_single_date_when_no_or_same_end_date(end_date):
    """Blank or same-day end date renders only the start date."""
    text = _render("September 09, 2026", end_date)
    assert "On September 09, 2026, Environmental Assessment" in text
    assert " and ," not in text


def test_date_range_when_end_date_differs():
    """Different end date renders both dates."""
    text = _render("September 09, 2026", "September 11, 2026")
    assert "On September 09, 2026 and September 11, 2026, Environmental Assessment" in text
