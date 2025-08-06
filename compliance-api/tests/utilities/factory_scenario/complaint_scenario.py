"""Various test data for complaint."""

from enum import Enum

from faker import Faker


fake = Faker()


class ComplaintScenario(Enum):
    """ComplaintScenario."""

    complaint_default = {
        "concern_description": fake.word(),
        "location_description": fake.word(),
        "primary_officer_id": 1,
        "case_file_id": 3,
        "date_received": "2024-09-24T16:41:28.088Z",
        "source_type_id": 4,
        "complaint_source_contact": {
            "description": fake.text(max_nb_chars=50),
            "full_name": fake.word(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "comment": fake.text(max_nb_chars=50),
        },
    }

    complaint_with_requirement_details = {
        "concern_description": fake.word(),
        "location_description": fake.word(),
        "primary_officer_id": 1,
        "case_file_id": 3,
        "date_received": "2024-09-24T16:41:28.088Z",
        "source_type_id": 4,
        "complaint_source_contact": {
            "description": fake.text(max_nb_chars=50),
            "full_name": fake.word(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "comment": fake.text(max_nb_chars=50),
        },
        "requirement_source_id": 2,
        "requirement_source_details": {"order_number": fake.word()},
    }
