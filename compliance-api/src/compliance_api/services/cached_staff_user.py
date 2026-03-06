"""
CachedStaffUserService provides methods for staff user data retrieval.

NOTE:
Staff caching has been intentionally removed for in production.
This service always fetches fresh data to avoid cross-pod
permission inconsistencies.
Re-enable only with a shared cache, not a Simple cache.
"""

from flask import current_app

from compliance_api.models.staff_user import StaffUser as StaffUserModel
from compliance_api.schemas.staff_user import StaffUserSchema
from compliance_api.services.authorize_service.auth_service import AuthService


class CachedStaffUserService:
    """Cached staff user service for performance optimization during token validation."""

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

        current_app.logger.debug(
            f"Fetching staff existence from DB for auth_guid={auth_guid}"
        )

        staff_user = StaffUserModel.get_by_auth_guid(auth_guid)
        return bool(staff_user)

    @staticmethod
    def get_all_staff_users_with_auth():
        """
        Get all staff users with merged auth data.

        Returns:
            List of serialized staff user dictionaries
        """
        # pylint: disable=import-outside-toplevel
        from .staff_user import _set_permission_level_in_compliance_user_obj

        current_app.logger.debug(
            "Fetching all staff users with auth data (no cache)"
        )

        users = StaffUserModel.get_all_with_relationships(default_filters=False)

        auth_users = AuthService.get_epic_users_by_app()
        index_auth_users = {user["username"]: user for user in auth_users}

        for user in users:
            auth_user = index_auth_users.get(user.auth_user_guid)
            _set_permission_level_in_compliance_user_obj(user, auth_user)

        user_schema = StaffUserSchema(many=True)
        return user_schema.dump(users)
