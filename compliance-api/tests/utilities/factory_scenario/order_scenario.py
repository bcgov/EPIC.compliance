"""Order scenario for testing."""

import enum
from datetime import datetime, timezone

from compliance_api.models.order import OrderStatusEnum


class OrderScenario(enum.Enum):
    """Test scenarios of order."""

    default_value = {
        "inspection_id": 1,
        "issuing_officer_id": 1,
        "where_as": "Test where as",
        "now_therefore": "Test now therefore",
        "intended_issuance_date": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "inspection_requirement_ids": [1],
    }

    update_value = {
        "inspection_id": 1,
        "issuing_officer_id": 1,
        "where_as": "Updated where as",
        "now_therefore": "Updated now therefore",
        "intended_issuance_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "inspection_requirement_ids": [1],
    }

    issue_value = {"date_issued": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")}

    status_value = {"status": OrderStatusEnum.CLOSED.name}

    reset_field_value = {"field_name": "where_as"}
