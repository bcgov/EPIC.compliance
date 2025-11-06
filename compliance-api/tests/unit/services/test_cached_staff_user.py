"""Test cached staff user service."""

from compliance_api.services.cached_staff_user import CachedStaffUserService
from compliance_api.utils.cache import cache


class TestCachedStaffUserService:
    """Test cached staff user service."""

    def test_exists_staff_by_auth_guid_cache_miss(self):
        """Test checking staff existence with cache miss."""
        # Clear cache first to ensure cache miss
        cache.clear()

        auth_guid = "test.viewer@gov.bc.ca"

        # First call should be cache miss
        exists = CachedStaffUserService.exists_staff_by_auth_guid(auth_guid)

        assert exists is True

    def test_exists_staff_by_auth_guid_cache_hit(self):
        """Test checking staff existence with cache hit."""
        auth_guid = "test.viewer@gov.bc.ca"

        # First call to populate cache
        exists1 = CachedStaffUserService.exists_staff_by_auth_guid(auth_guid)

        # Second call should be cache hit
        exists2 = CachedStaffUserService.exists_staff_by_auth_guid(auth_guid)

        assert exists1 is True
        assert exists2 is True

    def test_exists_staff_by_auth_guid_nonexistent(self):
        """Test checking existence for nonexistent staff."""
        # Clear cache first
        cache.clear()

        auth_guid = "nonexistent.user@gov.bc.ca"

        # Should return False for nonexistent user
        exists = CachedStaffUserService.exists_staff_by_auth_guid(auth_guid)

        assert exists is False

        # Second call should also return False (cached False value)
        exists2 = CachedStaffUserService.exists_staff_by_auth_guid(auth_guid)
        assert exists2 is False

    def test_invalidate_staff_cache_specific_user(self):
        """Test invalidating cache for specific user."""
        auth_guid = "test.viewer@gov.bc.ca"

        # Populate cache
        exists1 = CachedStaffUserService.exists_staff_by_auth_guid(auth_guid)
        assert exists1 is True

        # Invalidate specific user cache
        CachedStaffUserService.invalidate_staff_cache(auth_guid)

        # Should still work (will fetch from database)
        exists2 = CachedStaffUserService.exists_staff_by_auth_guid(auth_guid)
        assert exists2 is True

    def test_invalidate_staff_cache_all_users(self):
        """Test invalidating all staff cache."""
        # Populate cache for both users
        viewer_exists = CachedStaffUserService.exists_staff_by_auth_guid(
            "test.viewer@gov.bc.ca"
        )
        superuser_exists = CachedStaffUserService.exists_staff_by_auth_guid(
            "test.superuser@gov.bc.ca"
        )

        assert viewer_exists is True
        assert superuser_exists is True

        # Invalidate all cache
        CachedStaffUserService.invalidate_staff_cache()

        # Both should still work (will fetch from database)
        viewer_exists2 = CachedStaffUserService.exists_staff_by_auth_guid(
            "test.viewer@gov.bc.ca"
        )
        superuser_exists2 = CachedStaffUserService.exists_staff_by_auth_guid(
            "test.superuser@gov.bc.ca"
        )

        assert viewer_exists2 is True
        assert superuser_exists2 is True

    def test_exists_staff_by_auth_guid_empty_guid(self):
        """Test checking staff existence with empty auth guid."""
        exists = CachedStaffUserService.exists_staff_by_auth_guid("")
        assert exists is False

        exists = CachedStaffUserService.exists_staff_by_auth_guid(None)
        assert exists is False
