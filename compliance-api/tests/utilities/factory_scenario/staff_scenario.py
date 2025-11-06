"""Various test data for topics."""

from enum import Enum

from faker import Faker

from compliance_api.models import StaffUser as StaffUserModel


fake = Faker()


class StaffScenario(Enum):
    """Staff scenario."""

    default_data = {
        "first_name": fake.word(),
        "last_name": fake.word(),
        "position_id": 1,
        "auth_user_guid": fake.word(),
    }

    # Staff data that matches JWT token claims for testing
    test_viewer_staff = {
        "first_name": "Test",
        "last_name": "Viewer",
        "position_id": 1,
        "auth_user_guid": "test.viewer@gov.bc.ca",
        "is_active": True,
        "is_deleted": False,
    }

    test_superuser_staff = {
        "first_name": "Test",
        "last_name": "SuperUser",
        "position_id": 1,
        "auth_user_guid": "test.superuser@gov.bc.ca",
        "is_active": True,
        "is_deleted": False,
    }

    epic_auth_users = [
        {
            "id": "5bca57e4-1b39-498c-8872-732d3da4beaf",
            "first_name": "Shaelyn",
            "last_name": "Tolk",
            "email_address": "shaelyn.tolk@gov.bc.ca",
            "username": f"{fake.text(max_nb_chars=20)}",
            "groups": [
                {
                    "id": "b872cb25-2a8b-4b98-8aff-1c8ac1c47b40",
                    "name": "VIEWER",
                    "path": "COMPLIANCE/VIEWER",
                    "level": 0,
                    "display_name": "",
                },
                {
                    "id": "6f94f250-c4bf-4dc6-9158-fc64e8083edc",
                    "name": "USER",
                    "path": "COMPLIANCE/USER",
                    "level": 1,
                    "display_name": "",
                },
            ],
        },
        {
            "id": "34413651-fd5a-4253-b205-5acac3611915",
            "first_name": "Abhinav",
            "last_name": "Sharma",
            "email_address": "abhinav.sharma@gov.bc.ca",
            "username": f"{fake.text(max_nb_chars=20)}",
            "groups": [
                {
                    "id": "6f94f250-c4bf-4dc6-9158-fc64e8083edc",
                    "name": "USER",
                    "path": "COMPLIANCE/USER",
                    "level": 1,
                    "display_name": "",
                }
            ],
        },
    ]

    @staticmethod
    def create(data: dict) -> StaffUserModel:
        """Create staff user."""
        user = StaffUserModel.create_staff(data)
        print("staff user created")
        return user
