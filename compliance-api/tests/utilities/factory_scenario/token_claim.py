"""Scenarios for different token claims."""

from enum import Enum

from faker import Faker

from compliance_api.config import get_named_config


fake = Faker()
CONFIG = get_named_config("testing")


class TokenJWTClaims(dict, Enum):
    """Token claims."""

    default = {
        "iss": CONFIG.JWT_OIDC_TEST_ISSUER,
        "sub": "f7a4a1d3-73a8-4cbc-a40f-bb1145302065",
        "firstname": fake.first_name(),
        "lastname": fake.last_name(),
        "preferred_username": fake.user_name(),
        "groups": ["/COMPLIANCE/VIEWER"],
        "realm_access": {"roles": []},
    }
