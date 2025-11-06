"""Test cached staff user service."""

from compliance_api.services.cached_staff_user import CachedStaffUserService
from compliance_api.utils.cache import cache


class TestCachedStaffUserService:
    """Test cached staff user service."""

    def test_get_staff_by_auth_guid_cache_miss(self):
        """Test getting staff by auth guid with cache miss."""
        # Clear cache first to ensure cache miss
        cache.clear()

        auth_guid = "test.viewer@gov.bc.ca"

        # First call should be cache miss
        staff = CachedStaffUserService.get_staff_by_auth_guid(auth_guid)

        assert staff is not None
        assert staff.auth_user_guid == auth_guid
        assert staff.first_name == "Test"
        assert staff.last_name == "Viewer"

    def test_get_staff_by_auth_guid_cache_hit(self):
        """Test getting staff by auth guid with cache hit."""
        auth_guid = "test.viewer@gov.bc.ca"

        # First call to populate cache
        staff1 = CachedStaffUserService.get_staff_by_auth_guid(auth_guid)

        # Second call should be cache hit (same object)
        staff2 = CachedStaffUserService.get_staff_by_auth_guid(auth_guid)

        assert staff1 is not None
        assert staff2 is not None
        assert staff1.auth_user_guid == staff2.auth_user_guid

    def test_get_staff_by_auth_guid_nonexistent(self):
        """Test getting nonexistent staff by auth guid."""
        # Clear cache first
        cache.clear()

        auth_guid = "nonexistent.user@gov.bc.ca"

        # Should return None for nonexistent user
        staff = CachedStaffUserService.get_staff_by_auth_guid(auth_guid)

        assert staff is None

        # Second call should also return None (cached False value)
        staff2 = CachedStaffUserService.get_staff_by_auth_guid(auth_guid)
        assert staff2 is None

    def test_invalidate_staff_cache_specific_user(self):
        """Test invalidating cache for specific user."""
        auth_guid = "test.viewer@gov.bc.ca"

        # Populate cache
        staff1 = CachedStaffUserService.get_staff_by_auth_guid(auth_guid)
        assert staff1 is not None

        # Invalidate specific user cache
        CachedStaffUserService.invalidate_staff_cache(auth_guid)

        # Should still work (will fetch from database)
        staff2 = CachedStaffUserService.get_staff_by_auth_guid(auth_guid)
        assert staff2 is not None
        assert staff2.auth_user_guid == auth_guid

    def test_invalidate_staff_cache_all_users(self):
        """Test invalidating all staff cache."""
        # Populate cache for both users
        viewer_staff = CachedStaffUserService.get_staff_by_auth_guid(
            "test.viewer@gov.bc.ca"
        )
        superuser_staff = CachedStaffUserService.get_staff_by_auth_guid(
            "test.superuser@gov.bc.ca"
        )

        assert viewer_staff is not None
        assert superuser_staff is not None

        # Invalidate all cache
        CachedStaffUserService.invalidate_staff_cache()

        # Both should still work (will fetch from database)
        viewer_staff2 = CachedStaffUserService.get_staff_by_auth_guid(
            "test.viewer@gov.bc.ca"
        )
        superuser_staff2 = CachedStaffUserService.get_staff_by_auth_guid(
            "test.superuser@gov.bc.ca"
        )

        assert viewer_staff2 is not None
        assert superuser_staff2 is not None

    def test_get_staff_by_auth_guid_empty_guid(self):
        """Test getting staff with empty auth guid."""
        staff = CachedStaffUserService.get_staff_by_auth_guid("")
        assert staff is None

        staff = CachedStaffUserService.get_staff_by_auth_guid(None)
        assert staff is None
