"""Cached service for staff user validation during token authentication."""

import logging
from typing import Optional

from compliance_api.models.staff_user import StaffUser as StaffUserModel
from compliance_api.utils.cache import cache


logger = logging.getLogger(__name__)


class CachedStaffUserService:
    """Cached staff user service for performance optimization during token validation."""

    CACHE_TIMEOUT = 3600  # 1 hour
    STAFF_CACHE_KEY_PREFIX = "staff_user:"
    ALL_STAFF_CACHE_KEY = "all_staff_users"

    @classmethod
    def get_staff_by_auth_guid(cls, auth_guid: str) -> Optional[StaffUserModel]:
        """
        Get staff user by auth_guid with caching.

        This method is optimized for token validation performance.
        It first checks cache, then falls back to database if not found.

        Args:
            auth_guid: The auth_user_guid from token (preferred_username)

        Returns:
            StaffUser model instance if found and active, None otherwise
        """
        if not auth_guid:
            return None

        cache_key = f"{cls.STAFF_CACHE_KEY_PREFIX}{auth_guid}"

        # Try to get from cache first
        cached_staff = cache.get(cache_key)
        if cached_staff is not None:
            logger.debug(f"Cache hit for staff user: {auth_guid}")
            # Return None if cached value is explicitly False (user doesn't exist)
            return cached_staff if cached_staff else None

        # Cache miss - fetch from database
        logger.debug(f"Cache miss for staff user: {auth_guid}")
        staff_user = StaffUserModel.get_by_auth_guid(auth_guid)

        # Cache the result (cache False if user doesn't exist to avoid repeated DB calls)
        cache_value = staff_user if staff_user else False
        cache.set(cache_key, cache_value, timeout=cls.CACHE_TIMEOUT)

        return staff_user

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
            logger.info(f"Invalidated cache for staff user: {auth_guid}")
        else:
            # Clear all staff-related cache
            cls._clear_all_staff_cache()
            logger.info("Invalidated all staff user cache")

    @classmethod
    def _clear_all_staff_cache(cls):
        """Clear all staff-related cache entries."""
        try:
            cache.clear()
            logger.info("Cleared all cache (simple cache type)")
        except (AttributeError, RuntimeError) as e:
            logger.error(f"Error clearing cache: {str(e)}")
