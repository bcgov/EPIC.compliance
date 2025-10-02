"""Restorative Justice scenario for testing."""

import enum
from datetime import datetime, timezone


class RestorativeJusticeScenario(enum.Enum):
    """Test scenarios of restorative justice."""

    default_value = {
        "inspection_id": 1,
        "restitution_details": "Test restitution details for environmental restoration",
        "inspection_requirement_ids": [1],
    }

    update_value = {
        "inspection_id": 1,
        "restitution_details": "Updated restitution details with additional requirements",
        "date_restitution_complete": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "inspection_requirement_ids": [1],
    }

    drafting_value = {
        "inspection_id": 1,
        "inspection_requirement_ids": [1],
        # No restitution_details or date_restitution_complete - should be DRAFTING
    }

    open_value = {
        "inspection_id": 1,
        "restitution_details": "Restitution work has begun",
        "inspection_requirement_ids": [1],
        # Has restitution_details but no completion date - should be OPEN
    }

    closed_value = {
        "inspection_id": 1,
        "restitution_details": "All restitution work completed successfully",
        "date_restitution_complete": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "inspection_requirement_ids": [1],
        # Has both details and completion date - should be CLOSED
    }

    minimal_value = {
        "inspection_id": 1,
        "inspection_requirement_ids": [],
    }

    custom_number_value = {
        "inspection_id": 1,
        "restorative_justice_number": "CUSTOM-RJ-TEST-001",
        "restitution_details": "Custom numbered restorative justice",
        "inspection_requirement_ids": [1],
    }

    partial_update_value = {
        "inspection_id": 1,
        "restitution_details": "Partially updated restitution details",
    }

    status_transition_value = {
        "restitution_details": "Work in progress",
        "date_restitution_complete": None,
    }
