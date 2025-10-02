"""Warning Letter scenario for testing."""

import enum
import random
from datetime import datetime, timezone


def get_unique_warning_letter_number(prefix="WL-TEST"):
    """Generate a unique warning letter number."""
    return f"{prefix}-{random.randint(100000, 999999)}"


class WarningLetterScenario(enum.Enum):
    """Test scenarios of warning letter."""

    @property
    def value(self):
        """Return the scenario value with dynamic warning letter numbers."""
        base_value = super().value
        if "warning_letter_number" in base_value:
            # Generate a new unique warning letter number each time
            new_value = base_value.copy()
            warning_letter_number = base_value["warning_letter_number"]
            if warning_letter_number == "WL-TEST-DEFAULT":
                new_value["warning_letter_number"] = get_unique_warning_letter_number()
            elif warning_letter_number == "WL-TEST-UPDATE-TEMPLATE":
                new_value["warning_letter_number"] = get_unique_warning_letter_number(
                    "WL-TEST-UPDATE"
                )
            elif warning_letter_number == "WL-TEST-CREATED-TEMPLATE":
                new_value["warning_letter_number"] = get_unique_warning_letter_number(
                    "WL-TEST-CREATED"
                )
            elif warning_letter_number == "WL-TEST-ISSUED-TEMPLATE":
                new_value["warning_letter_number"] = get_unique_warning_letter_number(
                    "WL-TEST-ISSUED"
                )
            elif warning_letter_number == "WL-TEST-DRAFTING-TEMPLATE":
                new_value["warning_letter_number"] = get_unique_warning_letter_number(
                    "WL-TEST-DRAFTING"
                )
            elif warning_letter_number == "WL-TEST-DEPUTY-TEMPLATE":
                new_value["warning_letter_number"] = get_unique_warning_letter_number(
                    "WL-TEST-DEPUTY"
                )
            elif warning_letter_number == "WL-TEST-APPROVED-TEMPLATE":
                new_value["warning_letter_number"] = get_unique_warning_letter_number(
                    "WL-TEST-APPROVED"
                )
            elif warning_letter_number == "CUSTOM-WL-TEST-TEMPLATE":
                new_value["warning_letter_number"] = get_unique_warning_letter_number(
                    "CUSTOM-WL-TEST"
                )
            elif warning_letter_number == "WL-TEST-MINIMAL-TEMPLATE":
                new_value["warning_letter_number"] = get_unique_warning_letter_number(
                    "WL-TEST-MINIMAL"
                )
            elif warning_letter_number == "WL-TEST-PARTIAL-TEMPLATE":
                new_value["warning_letter_number"] = get_unique_warning_letter_number(
                    "WL-TEST-PARTIAL"
                )
            elif warning_letter_number == "WL-TEST-CONTENT-TEMPLATE":
                new_value["warning_letter_number"] = get_unique_warning_letter_number(
                    "WL-TEST-CONTENT"
                )
            elif warning_letter_number == "WL-TEST-OFFICER-TEMPLATE":
                new_value["warning_letter_number"] = get_unique_warning_letter_number(
                    "WL-TEST-OFFICER"
                )
            return new_value
        return base_value

    default_value = {
        "inspection_id": 1,
        "warning_letter_number": "WL-TEST-DEFAULT",
        "inspection_requirement_ids": [1],
    }

    update_value = {
        "inspection_id": 1,
        "warning_letter_number": "WL-TEST-UPDATE-TEMPLATE",
        "issuing_officer_id": 1,
        "intended_issuance_date": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "content": "Updated warning letter content for testing purposes.",
        "inspection_requirement_ids": [1],
    }

    created_value = {
        "inspection_id": 1,
        "warning_letter_number": "WL-TEST-CREATED-TEMPLATE",
        "issuing_officer_id": 1,
        "inspection_requirement_ids": [1],
    }

    issued_value = {
        "inspection_id": 1,
        "warning_letter_number": "WL-TEST-ISSUED-TEMPLATE",
        "issuing_officer_id": 1,
        "inspection_requirement_ids": [1],
    }

    drafting_value = {
        "inspection_id": 1,
        "warning_letter_number": "WL-TEST-DRAFTING-TEMPLATE",
        "issuing_officer_id": 1,
        "content": "Warning letter in drafting status for testing.",
        "inspection_requirement_ids": [1],
    }

    deputy_review_value = {
        "inspection_id": 1,
        "warning_letter_number": "WL-TEST-DEPUTY-TEMPLATE",
        "issuing_officer_id": 1,
        "content": "Warning letter in deputy review status for testing.",
        "inspection_requirement_ids": [1],
    }

    approved_value = {
        "inspection_id": 1,
        "warning_letter_number": "WL-TEST-APPROVED-TEMPLATE",
        "issuing_officer_id": 1,
        "content": "Warning letter in approved status for testing.",
        "intended_issuance_date": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "inspection_requirement_ids": [1],
    }

    minimal_value = {
        "inspection_id": 1,
        "warning_letter_number": "WL-TEST-MINIMAL-TEMPLATE",
        "inspection_requirement_ids": [],
    }

    custom_warning_letter_number_value = {
        "inspection_id": 1,
        "warning_letter_number": "CUSTOM-WL-TEST-TEMPLATE",
        "issuing_officer_id": 1,
        "content": "Custom warning letter number for testing.",
        "inspection_requirement_ids": [1],
    }

    partial_update_value = {
        "inspection_id": 1,
        "warning_letter_number": "WL-TEST-PARTIAL-TEMPLATE",
        "content": "Partially updated warning letter content.",
    }

    progress_transition_value = {
        "progress": "DEPUTY_REVIEW",
    }

    status_transition_value = {
        "status": "ISSUED",
    }

    content_update_value = {
        "content": "Updated content for warning letter testing purposes.",
    }

    officer_update_value = {
        "issuing_officer_id": 2,
    }

    intended_date_update_value = {
        "intended_issuance_date": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
    }

    issue_warning_letter_value = {
        "date_issued": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }

    reset_content_value = {
        "field_name": "content",
    }

    with_content_value = {
        "inspection_id": 1,
        "warning_letter_number": "WL-TEST-CONTENT-TEMPLATE",
        "issuing_officer_id": 1,
        "content": "This is a test warning letter content with specific details for compliance testing.",
        "intended_issuance_date": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "inspection_requirement_ids": [1],
    }

    with_officer_value = {
        "inspection_id": 1,
        "warning_letter_number": "WL-TEST-OFFICER-TEMPLATE",
        "issuing_officer_id": 2,
        "content": "Warning letter with specific issuing officer for testing.",
        "inspection_requirement_ids": [1],
    }

    auto_number_value = {
        "inspection_id": 1,
        "issuing_officer_id": 1,
        "content": "Warning letter with auto-generated number for testing.",
        "inspection_requirement_ids": [1],
    }
