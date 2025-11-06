"""Cached service for staff user validation during token authentication."""

from flask import current_app

from compliance_api.models.staff_user import StaffUser as StaffUserModel
from compliance_api.utils.cache import cache


class CachedStaffUserService:
    """Cached staff user service for performance optimization during token validation."""

    CACHE_TIMEOUT = 3600  # 1 hour
    STAFF_CACHE_KEY_PREFIX = "staff_user:"
    ALL_STAFF_CACHE_KEY = "all_staff_users"

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

    @classmethod
    def invalidate_staff_cache(cls, auth_guid: str = None):
        """
        Invalidate cached staff user data.

        Args:
            auth_guid: Specific auth_guid to invalidate, or None to clear all staff cache
        """
        if auth_guid:
            cache_key = f"{cls.STAFF_CACHE_KEY_PREFIX}{auth_guid}"
            cache.delete(cache_key)
            current_app.logger.info(f"Invalidated cache for staff user: {auth_guid}")
        else:
            cls._clear_all_staff_cache()
            current_app.logger.info("Invalidated all staff user cache")

    @classmethod
    def _clear_all_staff_cache(cls):
        """Clear all staff-related cache entries."""
        try:
            cache.clear()
            current_app.logger.info("Cleared all cache (simple cache type)")
        except (AttributeError, RuntimeError) as e:
            current_app.logger.error(f"Error clearing cache: {str(e)}")
