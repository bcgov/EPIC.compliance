"""Charge Recommendation scenario for testing."""

import enum
from datetime import datetime, timezone


class ChargeRecommendationScenario(enum.Enum):
    """Test scenarios of charge recommendation."""

    default_value = {
        "inspection_id": 1,
        "status": "DRAFTING",
        "inspection_requirement_ids": [1],
    }

    update_value = {
        "inspection_id": 1,
        "status": "DEPUTY_REVIEW",
        "date_to_crown_counsel": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "inspection_requirement_ids": [1],
    }

    drafting_value = {
        "inspection_id": 1,
        "status": "DRAFTING",
        "inspection_requirement_ids": [1],
    }

    deputy_review_value = {
        "inspection_id": 1,
        "status": "DEPUTY_REVIEW",
        "date_to_crown_counsel": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "inspection_requirement_ids": [1],
    }

    submitted_to_crown_counsel_value = {
        "inspection_id": 1,
        "status": "SUBMITTED_TO_CROWN_COUNSEL",
        "date_to_crown_counsel": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "charge_decision": "APPROVED",
        "charge_decision_date": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "inspection_requirement_ids": [1],
    }

    ceb_not_proceeding_value = {
        "inspection_id": 1,
        "status": "CEB_NOT_PROCEEDING",
        "charge_decision": "NOT_PROCEEDING",
        "charge_decision_date": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "inspection_requirement_ids": [1],
    }

    with_court_details_value = {
        "inspection_id": 1,
        "status": "SUBMITTED_TO_CROWN_COUNSEL",
        "date_to_crown_counsel": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "charge_decision": "APPROVED",
        "charge_decision_date": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "court_file_number": "CF-2024-001",
        "court_appearances": "Initial appearance scheduled for next month",
        "judgment": "GUILTY",
        "judgment_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "sentence_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "sentence_type": "Fine of $5000",
        "inspection_requirement_ids": [1],
    }

    minimal_value = {
        "inspection_id": 1,
        "inspection_requirement_ids": [],
    }

    custom_number_value = {
        "inspection_id": 1,
        "charge_recommendation_number": "CUSTOM-CR-TEST-001",
        "status": "DRAFTING",
        "inspection_requirement_ids": [1],
    }

    partial_update_value = {
        "inspection_id": 1,
        "status": "DEPUTY_REVIEW",
    }

    status_transition_value = {
        "status": "SUBMITTED_TO_CROWN_COUNSEL",
        "date_to_crown_counsel": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
    }

    court_update_value = {
        "court_file_number": "CF-2024-002",
        "court_appearances": "Updated court appearance details",
        "judgment": "NOT_GUILTY",
        "judgment_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }

    sentence_update_value = {
        "sentence_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "sentence_type": "Community service 100 hours",
    }
