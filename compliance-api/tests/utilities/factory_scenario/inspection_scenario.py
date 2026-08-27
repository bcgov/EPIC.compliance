"""Scenario for inspection."""

from enum import Enum

from faker import Faker


fake = Faker()


class InspectionScenario(Enum):
    """Inspection Scenario."""

    default_value = {
        "location_description": "test location description",
        "project_description": "project description",
        "utm": "utm",
        "primary_officer_id": 1,
        "project_status_ids": [13],
        "start_date": "2024-08-28T20:18:55.740Z",
        "end_date": "2024-08-30T20:18:55.741Z",
        "debrief_date": "2024-08-29T20:18:55.741Z",
        "initiation_id": 1,
        "inspection_type_ids": [1],
    }
