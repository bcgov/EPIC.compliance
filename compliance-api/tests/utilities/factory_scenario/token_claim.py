"""Scenarios for different token claims."""

from enum import Enum

from compliance_api.config import get_named_config


CONFIG = get_named_config("testing")


class TokenJWTClaims(dict, Enum):
    """Token claims."""

    default = {
        "iss": CONFIG.JWT_OIDC_TEST_ISSUER,
        "sub": "f7a4a1d3-73a8-4cbc-a40f-bb1145302065",
        "firstname": "Test",
        "lastname": "Viewer",
        "preferred_username": "test.viewer@gov.bc.ca",
        "groups": ["/COMPLIANCE/VIEWER"],
        "realm_access": {"roles": []},
        "resource_access": {"epic-compliance": {"roles": ["viewer"]}},
    }
    super_user = {
        "iss": CONFIG.JWT_OIDC_TEST_ISSUER,
        "sub": "f7a4a1d3-73a8-4cbc-a40f-bb1145302065",
        "firstname": "Test",
        "lastname": "SuperUser",
        "preferred_username": "test.superuser@gov.bc.ca",
        "groups": ["/COMPLIANCE/SUPERUSER"],
        "realm_access": {"roles": []},
        "resource_access": {"epic-compliance": {"roles": ["super_user"]}},
    }
