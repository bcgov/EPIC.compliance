"""Service for user management with integrated caching."""

import logging

from compliance_api.exceptions import ResourceExistsError, ResourceNotFoundError
from compliance_api.models.staff_user import StaffUser as StaffUserModel
from compliance_api.utils.constant import AUTH_APP
from compliance_api.utils.enum import PermissionEnum

from .authorize_service.auth_service import AuthService


class StaffUserService:
    """User management service with integrated caching."""

    @classmethod
    def get_user_by_id(cls, user_id):
        """Get user by id with auth data."""
        staff_user = StaffUserModel.find_by_id(user_id)
        if staff_user:
            # AuthService has its own caching
            auth_user = AuthService.get_epic_user_by_guid(staff_user.auth_user_guid)
            staff_user = _set_permission_level_in_compliance_user_obj(
                staff_user, auth_user
            )
        return staff_user

    @classmethod
    def get_user_by_auth_guid(cls, auth_user_guid: str):
        """Get user by auth_user_guid with auth data."""
        staff_user = StaffUserModel.get_by_auth_guid(auth_user_guid)
        if staff_user:
            # AuthService has its own caching
            auth_user = AuthService.get_epic_user_by_guid(staff_user.auth_user_guid)
            staff_user = _set_permission_level_in_compliance_user_obj(
                staff_user, auth_user
            )
        return staff_user

    @classmethod
    def get_all_staff_users(cls):
        """
        Get all users with caching.

        This returns serialized data from CachedStaffUserService.
        """
        #  Flagged by static analysis, but fine at runtime because of lazy importing
        #  pylint: disable=cyclic-import, import-outside-toplevel
        from .cached_staff_user import CachedStaffUserService

        return CachedStaffUserService.get_all_staff_users_with_auth()

    @staticmethod
    def create_user(user_data):
        """
        Create a user.

        Args:
            user_data: Dictionary containing user data including:
                - auth_user_guid: The auth user GUID
                - position_id: Position ID
                - deputy_director_id: Deputy director ID (optional)
                - supervisor_id: Supervisor ID (optional)
                - permission: Permission level (optional)

        Returns:
            Created staff user object
        """
        auth_user_guid = user_data.get("auth_user_guid")

        # Validate that staff user doesn't already exist
        _validate_staff_user_existence(auth_user_guid)

        # Get user from auth service to validate they exist
        auth_user = AuthService.get_epic_user_by_guid(auth_user_guid)
        if not auth_user:
            raise ResourceNotFoundError(
                f"User with auth_user_guid {auth_user_guid} not found in auth service"
            )

        # Create the staff user object with data from auth service
        staff_user_data = _create_staff_user_object(user_data, auth_user)

        # Create in database
        created_user = StaffUserModel.create_staff(staff_user_data)

        # Handle permission assignment if provided
        permission = user_data.get("permission")
        if permission and created_user:
            try:
                # Update user group in auth service
                AuthService.update_user_group(
                    auth_user_guid,
                    {"group_name": permission, "app_name": AUTH_APP}
                )
            except (AttributeError, RuntimeError) as e:
                # Log the error but don't fail the user creation
                # The user exists in compliance DB, just without the permission in auth
                logging.error("Failed to update user group in auth service: %s", e)

        return created_user

    @staticmethod
    def update_user(user_id, user_data):
        """
        Update a user.

        Args:
            user_id: The staff user ID to update
            user_data: Dictionary containing fields to update

        Returns:
            Updated staff user object or None if not found
        """
        # Get existing user to check auth_guid before update
        existing_user = StaffUserModel.find_by_id(user_id)
        if not existing_user:
            return None

        # If auth_user_guid is being changed, validate new one doesn't exist
        new_auth_guid = user_data.get("auth_user_guid")
        if new_auth_guid and new_auth_guid != existing_user.auth_user_guid:
            _validate_staff_user_existence(new_auth_guid, staff_user_id=user_id)

        # Update the user
        updated_user = StaffUserModel.update_staff(user_id, user_data)

        if updated_user:
            # Handle permission (group) assignment
            permission = user_data.get("permission")
            if permission:
                auth_guid_to_update = new_auth_guid if new_auth_guid else existing_user.auth_user_guid
                try:
                    # Update user group
                    AuthService.update_user_group(
                        auth_guid_to_update,
                        {"group_name": permission, "app_name": AUTH_APP}
                    )
                except (AttributeError, RuntimeError) as e:
                    logging.error("Failed to update user group in auth service: %s", e)

            # Return the latest user object. Fetch by id rather than auth guid:
            # get_by_auth_guid filters out inactive users, which would make
            # deactivation updates look like the user was not found.
            return StaffUserService.get_user_by_id(user_id)

        return updated_user

    @staticmethod
    def delete_user(user_id):
        """
        Delete a user (soft delete).

        Args:
            user_id: The staff user ID to delete

        Returns:
            Deleted staff user object or None if not found
        """
        # Get user before deleting to capture auth_guid
        user = StaffUserModel.find_by_id(user_id)
        if not user:
            return None

        # Soft delete the user
        deleted_user = StaffUserModel.delete_staff_user(user_id)

        return deleted_user

    @classmethod
    def get_permission_levels(cls):
        """List all the permission levels."""
        return [{"id": perm.name, "name": perm.value} for perm in PermissionEnum]


def _create_staff_user_object(user_data: dict, auth_user: dict):
    """
    Create a staff user object from user data and auth service data.

    Args:
        user_data: Data from the API request
        auth_user: Data from the auth service

    Returns:
        Dictionary with staff user fields ready for database insertion
    """
    return {
        "first_name": auth_user.get("first_name", None),
        "last_name": auth_user.get("last_name", None),
        "position_id": user_data.get("position_id", None),
        "deputy_director_id": user_data.get("deputy_director_id"),
        "supervisor_id": user_data.get("supervisor_id", None),
        "auth_user_guid": auth_user.get("username", None),
        "is_active": auth_user.get("is_active", True),
    }


def _get_level(group):
    """
    Get the level from the group, defaulting to 0 if not valid.

    Used for sorting permission groups by level.
    """
    level_str = group.get("level", 0)
    try:
        return int(level_str)
    except (ValueError, TypeError):
        return 0


def _set_permission_level_in_compliance_user_obj(
    compliance_user: StaffUserModel, auth_user: dict
) -> StaffUserModel:
    """
    Set the permission level in compliance user object from auth service data.

    Extracts the highest-level permission group from auth service
    and sets it as an attribute on the staff user object.

    Args:
        compliance_user: The staff user model instance
        auth_user: Auth service user data containing groups

    Returns:
        The staff user object with permission attribute set
    """
    if auth_user and auth_user.get("groups", None):
        sorted_groups = sorted(auth_user.get("groups", []), key=_get_level)
        if sorted_groups:
            highest_group = sorted_groups[-1]
            group_name = highest_group.get("name")

            # Only set permission if it's a valid PermissionEnum
            if group_name and group_name in [p.name for p in PermissionEnum]:
                setattr(compliance_user, "permission", group_name)

    return compliance_user


def _validate_staff_user_existence(auth_user_guid: str, staff_user_id: int = None):
    """
    Check if a staff user with the given auth_user_guid already exists.

    Args:
        auth_user_guid: The auth user GUID to check
        staff_user_id: Optional staff user ID to exclude from check (for updates)

    Raises:
        ResourceExistsError: If a staff user with this auth_user_guid already exists
    """
    existing_staff_user = StaffUserModel.get_by_auth_guid(auth_user_guid)

    # If found, check if it's a different user than the one being updated
    if existing_staff_user and (
        not staff_user_id or existing_staff_user.id != staff_user_id
    ):
        raise ResourceExistsError(
            f"Staff user with the auth_user_guid {auth_user_guid} already exists"
        )
