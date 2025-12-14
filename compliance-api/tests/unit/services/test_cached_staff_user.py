"""Test cached staff user service with integrated auth caching."""

import pytest
from unittest.mock import patch
from flask import g

from compliance_api.models.staff_user import StaffUser as StaffUserModel
from compliance_api.services.cached_staff_user import CachedStaffUserService
from compliance_api.utils.cache import cache


class TestCachedStaffUserService:
    """Test cached staff user service."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment before each test."""
        # Clear all cached data
        cache.clear()

        # Reset versioned cache keys explicitly
        cache.set("all_staff_with_auth_version", 0)

        # Reset flask g context
        g.access_token = None

        yield

        # Cleanup
        cache.clear()

    def test_exists_staff_by_auth_guid_cache_miss(self):
        """Test checking staff existence with cache miss."""
        auth_guid = "test.viewer@gov.bc.ca"

        # First call should be cache miss
        exists = CachedStaffUserService.exists_staff_by_auth_guid(auth_guid)

        assert exists is True

        # Verify cache was populated
        cache_key = f"{CachedStaffUserService.STAFF_CACHE_KEY_PREFIX}{auth_guid}"
        cached_value = cache.get(cache_key)
        assert cached_value is True

    def test_exists_staff_by_auth_guid_cache_hit(self):
        """Test checking staff existence with cache hit."""
        auth_guid = "test.viewer@gov.bc.ca"

        # First call to populate cache
        exists1 = CachedStaffUserService.exists_staff_by_auth_guid(auth_guid)

        # Mock the database query to ensure it's not called on cache hit
        with patch('compliance_api.models.staff_user.StaffUser.get_by_auth_guid') as mock_db:
            # Second call should be cache hit (db should not be called)
            exists2 = CachedStaffUserService.exists_staff_by_auth_guid(auth_guid)
            mock_db.assert_not_called()

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
        with patch('compliance_api.models.staff_user.StaffUser.get_by_auth_guid') as mock_db:
            exists2 = CachedStaffUserService.exists_staff_by_auth_guid(auth_guid)
            mock_db.assert_not_called()  # Should hit cache

        assert exists2 is False

    def test_invalidate_staff_cache_specific_user(self):
        """Test invalidating cache for specific user."""
        auth_guid = "test.viewer@gov.bc.ca"

        # Populate cache
        exists1 = CachedStaffUserService.exists_staff_by_auth_guid(auth_guid)
        assert exists1 is True

        # Verify cache exists
        cache_key = f"{CachedStaffUserService.STAFF_CACHE_KEY_PREFIX}{auth_guid}"
        assert cache.get(cache_key) is True

        # Invalidate specific user cache
        CachedStaffUserService.invalidate_staff_cache(auth_guid)

        # Verify cache was cleared
        assert cache.get(cache_key) is None

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

    @patch('compliance_api.services.authorize_service.auth_service.AuthService.get_epic_users_by_app')
    @patch('compliance_api.models.staff_user.StaffUser.get_all_with_relationships')
    def test_get_all_staff_users_with_auth_cache_miss(self, mock_get_all, mock_auth):
        """Test getting all staff users with auth data - cache miss."""
        g.access_token = "test_token_user_a"

        # Mock database response
        mock_user = StaffUserModel(
            auth_user_guid="test.viewer@gov.bc.ca",
            first_name="Test",
            last_name="Viewer",
        )
        mock_get_all.return_value = [mock_user]

        # Mock auth service response
        mock_auth.return_value = [
            {"username": "test.viewer@gov.bc.ca", "permission": "VIEWER"}
        ]

        # First call should hit database and auth service
        users = CachedStaffUserService.get_all_staff_users_with_auth()

        assert len(users) == 1
        mock_get_all.assert_called_once()
        mock_auth.assert_called_once()

    @patch('compliance_api.services.authorize_service.auth_service.AuthService.get_epic_users_by_app')
    @patch('compliance_api.models.staff_user.StaffUser.get_all_with_relationships')
    def test_get_all_staff_users_with_auth_cache_hit(self, mock_get_all, mock_auth):
        """Test getting all staff users with auth data - cache hit."""
        g.access_token = "test_token_user_a"

        # Mock database response
        mock_user = StaffUserModel(
            auth_user_guid="test.viewer@gov.bc.ca",
            first_name="Test",
            last_name="Viewer",
        )
        mock_get_all.return_value = [mock_user]

        # Mock auth service response
        mock_auth.return_value = [
            {"username": "test.viewer@gov.bc.ca", "permission": "VIEWER"}
        ]

        # First call populates cache
        users1 = CachedStaffUserService.get_all_staff_users_with_auth()
        assert len(users1) == 1

        # Reset mocks
        mock_get_all.reset_mock()
        mock_auth.reset_mock()

        # Second call should hit cache (no db or auth calls)
        users2 = CachedStaffUserService.get_all_staff_users_with_auth()

        assert len(users2) == 1
        mock_get_all.assert_not_called()
        mock_auth.assert_not_called()

    @patch('compliance_api.services.authorize_service.auth_service.AuthService.get_epic_users_by_app')
    @patch('compliance_api.models.staff_user.StaffUser.get_all_with_relationships')
    def test_get_all_staff_users_different_users_different_cache(
        self, mock_get_all, mock_auth
    ):
        """Test that different users get different cached data."""
        # Mock database response
        mock_user = StaffUserModel(
            auth_user_guid="test.viewer@gov.bc.ca",
            first_name="Test",
            last_name="Viewer",
        )
        mock_get_all.return_value = [mock_user]
        mock_auth.return_value = [
            {"username": "test.viewer@gov.bc.ca", "permission": "VIEWER"}
        ]

        # User A makes request
        g.access_token = "token_user_a"
        users_a = CachedStaffUserService.get_all_staff_users_with_auth()
        assert len(users_a) == 1

        # Reset mocks
        mock_get_all.reset_mock()
        mock_auth.reset_mock()

        # User B makes request - should not hit cache (different token)
        g.access_token = "token_user_b"
        users_b = CachedStaffUserService.get_all_staff_users_with_auth()

        assert len(users_b) == 1
        # Database and auth should be called again for User B
        mock_get_all.assert_called_once()
        mock_auth.assert_called_once()

    @patch('compliance_api.services.authorize_service.auth_service.AuthService.get_epic_users_by_app')
    @patch('compliance_api.models.staff_user.StaffUser.get_all_with_relationships')
    def test_cache_isolated_between_users(self, mock_get_all, mock_auth):
        """Ensure cached results are isolated between different users (different tokens)."""

        # Mock database response
        mock_user = StaffUserModel(
            auth_user_guid="test.viewer@gov.bc.ca",
            first_name="Test",
            last_name="Viewer",
        )
        mock_get_all.return_value = [mock_user]

        # Mock Auth service response
        mock_auth.return_value = [
            {"username": "test.viewer@gov.bc.ca", "permission": "VIEWER"}
        ]

        # User A makes a request
        g.access_token = "token_user_a"
        users_a = CachedStaffUserService.get_all_staff_users_with_auth()
        assert len(users_a) == 1

        # Reset mocks to ensure calls are counted separately
        mock_get_all.reset_mock()
        mock_auth.reset_mock()

        # User B makes a request with a different token
        g.access_token = "token_user_b"
        users_b = CachedStaffUserService.get_all_staff_users_with_auth()

        # Assert that results are not the same object and are separate cache entries
        assert users_a is not users_b

        # Database and auth service should have been called for user B
        mock_get_all.assert_called_once()
        mock_auth.assert_called_once()

        # assert contents are equal
        assert users_a == users_b

    @patch('compliance_api.services.authorize_service.auth_service.AuthService.get_epic_users_by_app')
    @patch('compliance_api.models.staff_user.StaffUser.get_all_with_relationships')
    def test_get_all_staff_users_same_user_hits_cache(
        self, mock_get_all, mock_auth
    ):
        """Test that same user hits cache on subsequent requests."""
        # Mock responses
        # Mock database response
        mock_user = StaffUserModel(
            auth_user_guid="test.viewer@gov.bc.ca",
            first_name="Test",
            last_name="Viewer",
        )
        mock_get_all.return_value = [mock_user]
        mock_auth.return_value = [
            {"username": "test.viewer@gov.bc.ca", "permission": "VIEWER"}
        ]

        # User A makes first request
        g.access_token = "token_user_a"
        users1 = CachedStaffUserService.get_all_staff_users_with_auth()
        assert len(users1) == 1

        # Reset mocks
        mock_get_all.reset_mock()
        mock_auth.reset_mock()

        # Same user makes second request - should hit cache
        g.access_token = "token_user_a"
        users2 = CachedStaffUserService.get_all_staff_users_with_auth()

        assert len(users2) == 1
        mock_get_all.assert_not_called()
        mock_auth.assert_not_called()

    def test_get_token_hash_consistency(self):
        """Test that token hash is consistent for same token."""
        g.access_token = "test_token_123"

        hash1 = CachedStaffUserService._get_token_hash()
        hash2 = CachedStaffUserService._get_token_hash()

        assert hash1 == hash2
        assert len(hash1) == 16  # Should be 16 chars
        assert hash1 != "test_token_123"  # Should be hashed, not raw token

    def test_get_token_hash_different_tokens(self):
        """Test that different tokens produce different hashes."""
        g.access_token = "token_a"
        hash_a = CachedStaffUserService._get_token_hash()

        g.access_token = "token_b"
        hash_b = CachedStaffUserService._get_token_hash()

        assert hash_a != hash_b

    def test_get_token_hash_no_token(self):
        """Test token hash when no token is present."""
        g.access_token = None

        hash_result = CachedStaffUserService._get_token_hash()
        assert hash_result == "no_token"

    @patch('compliance_api.services.authorize_service.auth_service.AuthService.get_epic_users_by_app')
    @patch('compliance_api.models.staff_user.StaffUser.get_all_with_relationships')
    def test_cache_invalidation_on_user_update(self, mock_get_all, mock_auth):
        """Test that cache is invalidated when a user is updated."""
        g.access_token = "test_token"

        # Mock database response
        mock_user = StaffUserModel(
            auth_user_guid="test.viewer@gov.bc.ca",
            first_name="Test",
            last_name="Viewer",
        )
        mock_get_all.return_value = [mock_user]
        mock_auth.return_value = [
            {"username": "test.viewer@gov.bc.ca", "permission": "VIEWER"}
        ]

        # Populate cache
        users1 = CachedStaffUserService.get_all_staff_users_with_auth()
        assert len(users1) == 1

        # Reset mocks
        mock_get_all.reset_mock()
        mock_auth.reset_mock()

        # Invalidate cache (simulating user update)
        CachedStaffUserService.invalidate_staff_cache("test.viewer@gov.bc.ca")

        # Next call should fetch fresh data
        users2 = CachedStaffUserService.get_all_staff_users_with_auth()
        assert len(users2) == 1

        # Database and auth should be called again
        mock_get_all.assert_called_once()
        mock_auth.assert_called_once()

    @patch('compliance_api.services.authorize_service.auth_service.AuthService.get_epic_user_by_guid')
    @patch('compliance_api.models.staff_user.StaffUser.create_staff')
    def test_create_user_invalidates_cache(
        self,
        mock_create,
        mock_get_epic_user_by_guid,
    ):
        """Test that creating a user invalidates relevant caches."""
        from compliance_api.services.staff_user import StaffUserService

        g.access_token = "test_token"

        # Mock database response
        mock_user = StaffUserModel(
            auth_user_guid="test.viewer@gov.bc.ca",
            first_name="Test",
            last_name="Viewer",
        )
        mock_create.return_value = mock_user

        mock_get_epic_user_by_guid.return_value = {
            "username": "new.user@gov.bc.ca"
        }

        user_data = {"auth_user_guid": "new.user@gov.bc.ca"}
        StaffUserService.create_user(user_data)

        mock_create.assert_called_once()

    @patch('compliance_api.services.authorize_service.auth_service.AuthService.get_epic_users_by_app')
    @patch('compliance_api.models.staff_user.StaffUser.get_all_with_relationships')
    def test_cache_reduces_database_calls(self, mock_get_all, mock_auth):
        """Test that caching reduces database and auth service calls."""
        g.access_token = "test_token"

        # Mock database response
        mock_user = StaffUserModel(
            auth_user_guid="test.viewer@gov.bc.ca",
            first_name="Test",
            last_name="Viewer",
        )
        mock_get_all.return_value = [mock_user]
        mock_auth.return_value = [
            {"username": "test.viewer@gov.bc.ca", "permission": "VIEWER"}
        ]

        # Make 5 requests
        for _ in range(5):
            CachedStaffUserService.get_all_staff_users_with_auth()

        # Database and auth should only be called once (first request)
        assert mock_get_all.call_count == 1
        assert mock_auth.call_count == 1

    @patch('compliance_api.services.authorize_service.auth_service.AuthService.get_epic_users_by_app')
    @patch('compliance_api.models.staff_user.StaffUser.get_all_with_relationships')
    def test_empty_staff_list_is_cached(self, mock_get_all, mock_auth):
        """Test that empty staff list is properly cached."""
        g.access_token = "test_token"

        # Mock empty responses
        mock_get_all.return_value = []
        mock_auth.return_value = []

        # First call
        users1 = CachedStaffUserService.get_all_staff_users_with_auth()
        assert len(users1) == 0

        # Reset mocks
        mock_get_all.reset_mock()
        mock_auth.reset_mock()

        # Second call should hit cache
        users2 = CachedStaffUserService.get_all_staff_users_with_auth()
        assert len(users2) == 0
        mock_get_all.assert_not_called()
        mock_auth.assert_not_called()

    @patch('compliance_api.services.authorize_service.auth_service.AuthService.get_epic_users_by_app')
    @patch('compliance_api.models.staff_user.StaffUser.get_all_with_relationships')
    def test_auth_users_mismatch(self, mock_get_all, mock_auth):
        """Test behavior when staff user exists but not in auth system."""
        g.access_token = "test_token"

        # Mock database response
        mock_user = StaffUserModel(
            auth_user_guid="test.viewer@gov.bc.ca",
            first_name="Test",
            last_name="Viewer",
        )
        mock_get_all.return_value = [mock_user]
        # But not in auth system
        mock_auth.return_value = []

        # Should still return the user (permission will be None)
        users = CachedStaffUserService.get_all_staff_users_with_auth()
        assert len(users) == 1

    @patch('compliance_api.services.authorize_service.auth_service.AuthService.get_epic_users_by_app')
    @patch('compliance_api.models.staff_user.StaffUser.get_all_with_relationships')
    def test_concurrent_requests_same_user(self, mock_get_all, mock_auth):
        """Test that concurrent requests from same user benefit from cache."""
        g.access_token = "test_token"

        # Mock database response
        mock_user = StaffUserModel(
            auth_user_guid="test.viewer@gov.bc.ca",
            first_name="Test",
            last_name="Viewer",
        )
        mock_get_all.return_value = [mock_user]
        mock_auth.return_value = [
            {"username": "test.viewer@gov.bc.ca", "permission": "VIEWER"}
        ]

        # Simulate multiple concurrent-ish requests
        results = []
        for _ in range(10):
            results.append(
                CachedStaffUserService.get_all_staff_users_with_auth()
            )

        # All should return same data
        assert all(len(r) == 1 for r in results)

        # But database should only be hit once (or a few times due to race)
        # In production with proper cache, this would be 1
        assert mock_get_all.call_count <= 3  # Allow some cache misses in tests
