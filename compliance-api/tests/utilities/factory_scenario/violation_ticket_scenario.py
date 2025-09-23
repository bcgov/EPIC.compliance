"""Violation Ticket scenario for testing."""

import enum
import random
from datetime import datetime, timezone
from decimal import Decimal


def get_unique_ticket_number(prefix="VT-TEST"):
    """Generate a unique ticket number."""
    return f"{prefix}-{random.randint(100000, 999999)}"


class ViolationTicketScenario(enum.Enum):
    """Test scenarios of violation ticket."""

    @property
    def value(self):
        """Return the scenario value with dynamic ticket numbers."""
        base_value = super().value
        if "ticket_number" in base_value:
            # Generate a new unique ticket number each time
            new_value = base_value.copy()
            ticket_number = base_value["ticket_number"]
            if ticket_number == "VT-TEST-DEFAULT":
                new_value["ticket_number"] = get_unique_ticket_number()
            elif ticket_number == "VT-TEST-UPD-TEMPLATE":
                new_value["ticket_number"] = get_unique_ticket_number("VT-TEST-UPD")
            elif ticket_number == "VT-TEST-ISSUED-TEMPLATE":
                new_value["ticket_number"] = get_unique_ticket_number("VT-TEST-ISSUED")
            elif ticket_number == "VT-TEST-PAID-TEMPLATE":
                new_value["ticket_number"] = get_unique_ticket_number("VT-TEST-PAID")
            elif ticket_number == "VT-TEST-DISPUTED-TEMPLATE":
                new_value["ticket_number"] = get_unique_ticket_number(
                    "VT-TEST-DISPUTED"
                )
            elif ticket_number == "VT-TEST-MINIMAL-TEMPLATE":
                new_value["ticket_number"] = get_unique_ticket_number("VT-TEST-MINIMAL")
            elif ticket_number == "CUSTOM-VT-TEST-TEMPLATE":
                new_value["ticket_number"] = get_unique_ticket_number("CUSTOM-VT-TEST")
            elif ticket_number == "VT-TEST-PARTIAL-TEMPLATE":
                new_value["ticket_number"] = get_unique_ticket_number("VT-TEST-PARTIAL")
            elif ticket_number == "VT-TEST-LARGE-TEMPLATE":
                new_value["ticket_number"] = get_unique_ticket_number("VT-TEST-LARGE")
            elif ticket_number == "VT-TEST-ZERO-TEMPLATE":
                new_value["ticket_number"] = get_unique_ticket_number("VT-TEST-ZERO")
            elif ticket_number == "VT-TEST-NO-FINE-TEMPLATE":
                new_value["ticket_number"] = get_unique_ticket_number("VT-TEST-NO-FINE")
            elif ticket_number == "VT-TEST-UPDATE-TEMPLATE":
                new_value["ticket_number"] = get_unique_ticket_number("VT-TEST-UPDATE")
            elif ticket_number == "VT-TEST-UPDATE-LARGE-TEMPLATE":
                new_value["ticket_number"] = get_unique_ticket_number(
                    "VT-TEST-UPDATE-LARGE"
                )
            elif ticket_number == "VT-TEST-UPDATE-ZERO-TEMPLATE":
                new_value["ticket_number"] = get_unique_ticket_number(
                    "VT-TEST-UPDATE-ZERO"
                )
            return new_value
        return base_value

    default_value = {
        "inspection_id": 1,
        "ticket_number": "VT-TEST-DEFAULT",
        "inspection_requirement_ids": [1],
    }

    update_value = {
        "inspection_id": 1,
        "ticket_number": "VT-TEST-UPD-TEMPLATE",
        "date_issued": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "fine_amount": Decimal("250.00"),
        "status": "ISSUED",
        "status_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "inspection_requirement_ids": [1],
    }

    issued_value = {
        "inspection_id": 1,
        "ticket_number": "VT-TEST-ISSUED-TEMPLATE",
        "inspection_requirement_ids": [1],
    }

    paid_value = {
        "inspection_id": 1,
        "ticket_number": "VT-TEST-PAID-TEMPLATE",
        "inspection_requirement_ids": [1],
    }

    disputed_value = {
        "inspection_id": 1,
        "ticket_number": "VT-TEST-DISPUTED-TEMPLATE",
        "inspection_requirement_ids": [1],
    }

    minimal_value = {
        "inspection_id": 1,
        "ticket_number": "VT-TEST-MINIMAL-TEMPLATE",
        "inspection_requirement_ids": [],
    }

    custom_vt_number_value = {
        "inspection_id": 1,
        "ticket_number": "CUSTOM-VT-TEST-TEMPLATE",
        "inspection_requirement_ids": [1],
    }

    partial_update_value = {
        "inspection_id": 1,
        "ticket_number": "VT-TEST-PARTIAL-TEMPLATE",
        "fine_amount": Decimal("200.00"),
    }

    status_transition_value = {
        "status": "PAID",
        "status_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }

    fine_amount_update_value = {
        "fine_amount": Decimal("350.00"),
        "status": "ISSUED",
        "status_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }

    date_issued_update_value = {
        "date_issued": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "status": "ISSUED",
    }

    large_fine_amount_value = {
        "inspection_id": 1,
        "ticket_number": "VT-TEST-LARGE-TEMPLATE",
        "inspection_requirement_ids": [1],
    }

    zero_fine_amount_value = {
        "inspection_id": 1,
        "ticket_number": "VT-TEST-ZERO-TEMPLATE",
        "inspection_requirement_ids": [1],
    }

    no_fine_amount_value = {
        "inspection_id": 1,
        "ticket_number": "VT-TEST-NO-FINE-TEMPLATE",
        "inspection_requirement_ids": [1],
    }

    # Update-specific scenarios (for PATCH operations)
    update_with_fine_value = {
        "inspection_id": 1,
        "ticket_number": "VT-TEST-UPDATE-TEMPLATE",
        "date_issued": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "fine_amount": Decimal("150.00"),
        "status": "ISSUED",
        "status_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "inspection_requirement_ids": [1],
    }

    update_large_fine_value = {
        "inspection_id": 1,
        "ticket_number": "VT-TEST-UPDATE-LARGE-TEMPLATE",
        "date_issued": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "fine_amount": Decimal("9999.99"),
        "status": "ISSUED",
        "status_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "inspection_requirement_ids": [1],
    }

    update_zero_fine_value = {
        "inspection_id": 1,
        "ticket_number": "VT-TEST-UPDATE-ZERO-TEMPLATE",
        "date_issued": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "fine_amount": Decimal("0.00"),
        "status": "ISSUED",
        "status_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "inspection_requirement_ids": [1],
    }
