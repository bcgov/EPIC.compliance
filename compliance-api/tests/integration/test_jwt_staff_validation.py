"""Test JWT token staff validation integration."""

from tests.utilities.factory_scenario import TokenJWTClaims
from tests.utilities.factory_utils import factory_auth_header


class TestJWTStaffValidation:
    """Test JWT token staff validation."""

    def test_default_token_has_valid_staff(self, client, jwt):
        """Test that default JWT token has corresponding staff user."""
        # Use the default token claims
        headers = factory_auth_header(jwt=jwt, claims=TokenJWTClaims.default.value)

        # Try to access any endpoint that requires authentication
        response = client.get("/api/positions", headers=headers)

        # Should not fail with staff validation error
        # (may fail with other errors, but not "No valid staff user found")
        assert (
            response.status_code != 403
            or "No valid staff user found" not in response.get_json().get("message", "")
        )

    def test_super_user_token_has_valid_staff(self, client, jwt):
        """Test that super user JWT token has corresponding staff user."""
        # Use the super user token claims
        headers = factory_auth_header(jwt=jwt, claims=TokenJWTClaims.super_user.value)

        # Try to access any endpoint that requires authentication
        response = client.get("/api/positions", headers=headers)

        # Should not fail with staff validation error
        assert (
            response.status_code != 403
            or "No valid staff user found" not in response.get_json().get("message", "")
        )

    def test_nonexistent_staff_token_fails(self, client, jwt):
        """Test that token with nonexistent staff user fails."""
        # Create token with nonexistent staff
        invalid_claims = TokenJWTClaims.default.value.copy()
        invalid_claims["preferred_username"] = "nonexistent.user@gov.bc.ca"

        headers = factory_auth_header(jwt=jwt, claims=invalid_claims)

        # Should fail with staff validation error
        response = client.get("/api/positions", headers=headers)

        assert response.status_code == 403
        assert "No valid staff user found" in response.get_json().get("message", "")
