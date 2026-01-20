"""Integrated caching strategy for staff users."""

import hashlib
from flask import current_app, g

from compliance_api.models.staff_user import StaffUser as StaffUserModel
from compliance_api.schemas.staff_user import StaffUserSchema
from compliance_api.services.authorize_service.auth_service import AuthService
from compliance_api.utils.cache import cache


class CachedStaffUserService:
    """Cached staff user service for performance optimization during token validation."""

    CACHE_TIMEOUT = 3600  # 1 hour
    STAFF_CACHE_KEY_PREFIX = "staff_user:"
    ALL_STAFF_CACHE_KEY = "all_staff_users"
    ALL_STAFF_WITH_AUTH_PREFIX = "all_staff_with_auth:"
    CACHE_VERSION_KEY = "all_staff_with_auth_version"

    @classmethod
    def exists_staff_by_auth_guid(cls, auth_guid: str) -> bool:
        """
        Check if staff user exists by auth_guid with caching.

        This is an optimized method that only checks existence without
        fetching the full user data from database on cache hit.

        Args:
            auth_guid: The auth_user_guid from token (preferred_username)

        Returns:
            True if staff user exists and is active, False otherwise
        """
        if not auth_guid:
            return False

        cache_key = f"{cls.STAFF_CACHE_KEY_PREFIX}{auth_guid}"

        cached_staff_exists = cache.get(cache_key)
        if cached_staff_exists is not None:
            current_app.logger.debug(
                f"Cache hit for staff existence check: {auth_guid}"
            )
            return bool(cached_staff_exists)

        current_app.logger.debug(f"Cache miss for staff existence check: {auth_guid}")
        staff_user = StaffUserModel.get_by_auth_guid(auth_guid)

        cache_value = bool(staff_user)
        cache.set(cache_key, cache_value, timeout=cls.CACHE_TIMEOUT)

        return cache_value

    @staticmethod
    def get_all_staff_users_with_auth():
        """
        Get all staff users with merged auth data (cached as serialized data).

        Returns:
            List of serialized staff user dictionaries
        """
        # pylint: disable=import-outside-toplevel
        from compliance_api.services.staff_user import _set_permission_level_in_compliance_user_obj

        # Get current version
        version = cache.get(CachedStaffUserService.CACHE_VERSION_KEY)
        if version is None:
            version = 0

        # Create cache key that includes token hash AND version
        token_hash = CachedStaffUserService._get_token_hash()
        cache_key = (
            f"{CachedStaffUserService.ALL_STAFF_WITH_AUTH_PREFIX}"
            f"{token_hash}:v{version}"
        )

        cached_result = cache.get(cache_key)
        if cached_result is not None:
            current_app.logger.debug("Cache hit for all staff users with auth data")
            return cached_result

        current_app.logger.debug("Cache miss for all staff users with auth data")

        # Get users from compliance database with eager loading
        users = StaffUserModel.get_all_with_relationships(default_filters=False)

        # Get compliance users from epic system
        auth_users = AuthService.get_epic_users_by_app()

        # Merge the two sets of users to set the permission in the result
        index_auth_users = {user["username"]: user for user in auth_users}
        for user in users:
            auth_user = index_auth_users.get(user.auth_user_guid, None)
            user = _set_permission_level_in_compliance_user_obj(user, auth_user)

        # Serialize the data BEFORE caching to avoid detached instance issues
        user_schema = StaffUserSchema(many=True)
        serialized_users = user_schema.dump(users)

        # Cache the serialized data
        cache.set(cache_key, serialized_users, timeout=300)  # 5 minutes

        return serialized_users

    @staticmethod
    def invalidate_staff_cache(auth_guid: str = None):
        """
        Invalidate cached staff user data.

        Args:
            auth_guid: Specific auth_guid to invalidate, or None to clear all staff cache
        """
        if auth_guid:
            cache_key = f"{CachedStaffUserService.STAFF_CACHE_KEY_PREFIX}{auth_guid}"
            cache.delete(cache_key)
            current_app.logger.info(f"Invalidated cache for staff user: {auth_guid}")

        # Always invalidate the aggregate cache when any staff user changes
        CachedStaffUserService._invalidate_all_staff_with_auth_cache()

    @staticmethod
    def _invalidate_all_staff_with_auth_cache():
        """
        Invalidate all staff+auth cache by bumping version number.

        This invalidates cache for all tokens/users since the version
        is part of every cache key.
        """
        try:
            current_version = cache.get(CachedStaffUserService.CACHE_VERSION_KEY)
            if current_version is None:
                current_version = 0

            new_version = current_version + 1
            cache.set(CachedStaffUserService.CACHE_VERSION_KEY, new_version)
            current_app.logger.info(
                f"Bumped staff+auth cache version from {current_version} to {new_version}"
            )
        except (AttributeError, RuntimeError) as e:
            current_app.logger.error(f"Error invalidating staff+auth cache: {e}")

    @classmethod
    def _clear_all_staff_cache(cls):
        """Clear all staff-related cache entries."""
        try:
            cache.clear()
            current_app.logger.info("Cleared all cache (simple cache type)")
        except (AttributeError, RuntimeError) as e:
            current_app.logger.error(f"Error clearing cache: {str(e)}")

    @staticmethod
    def _get_token_hash():
        """
        Generate a cache key suffix based on the current user's token.

        This ensures different users get different cached data while
        not exposing the actual token in cache keys.
        """
        token = getattr(g, "access_token", None)
        if not token:
            return "no_token"

        # Use first 16 chars of SHA256 hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
        return token_hash
