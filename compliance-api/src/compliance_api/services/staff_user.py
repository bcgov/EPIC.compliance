"""Service for user management."""

from compliance_api.exceptions import ResourceExistsError, ResourceNotFoundError, UnprocessableEntityError
from compliance_api.models.db import session_scope
from compliance_api.models.staff_user import StaffUser as StaffUserModel
from compliance_api.utils.constant import AUTH_APP
from compliance_api.utils.enum import PermissionEnum

from .authorize_service.auth_service import AuthService
from .cached_staff_user import CachedStaffUserService


class StaffUserService:
    """User management service."""

    @classmethod
    def get_user_by_id(cls, user_id):
        """Get user by id."""
        staff_user = StaffUserModel.find_by_id(user_id)
        if staff_user:
            auth_user = AuthService.get_epic_user_by_guid(staff_user.auth_user_guid)
            staff_user = _set_permission_level_in_compliance_user_obj(
                staff_user, auth_user
            )
        return staff_user

    @classmethod
    def get_user_by_auth_guid(cls, auth_user_guid: str):
        """Get user by auth_user_guid."""
        staff_user = StaffUserModel.get_by_auth_guid(auth_user_guid)
        if staff_user:
            auth_user = AuthService.get_epic_user_by_guid(staff_user.auth_user_guid)
            staff_user = _set_permission_level_in_compliance_user_obj(
                staff_user, auth_user
            )
        return staff_user

    @classmethod
    def get_all_staff_users(cls):
        """Get all users."""
        # Get users from compliance database
        users = StaffUserModel.get_all(default_filters=False)
        # Get compliance users from epic system
        auth_users = AuthService.get_epic_users_by_app()
        # Merge the two sets of users to set the permission in the result
        index_auth_users = {user["username"]: user for user in auth_users}
        for user in users:
            auth_user = index_auth_users.get(user.auth_user_guid, None)
            user = _set_permission_level_in_compliance_user_obj(user, auth_user)
        return users

    @classmethod
    def create_user(cls, user_data: dict):
        """Create user."""
        auth_user_guid = user_data.get("auth_user_guid", None)
        _validate_staff_user_existence(auth_user_guid)
        auth_user = AuthService.get_epic_user_by_guid(auth_user_guid)
        if not auth_user:
            raise UnprocessableEntityError(
                f"No user found from EPIC.Authorize corresponding to the given {auth_user_guid}"
            )
        user_obj = _create_staff_user_object(user_data, auth_user)
        group_payload = {
            "app_name": AUTH_APP,
            "group_name": user_data.get("permission", None),
        }
        with session_scope() as session:
            created_user = StaffUserModel.create_staff(user_obj, session)
            AuthService.update_user_group(auth_user_guid, group_payload)
            # Invalidate cache for the new user
            CachedStaffUserService.invalidate_staff_cache(auth_user_guid)
        return created_user

    @classmethod
    def update_user(cls, user_id, user_data):
        """Update staff user."""
        user = StaffUserModel.find_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("Staff with given id doesn't exist")
        auth_user_guid = user.auth_user_guid
        _validate_staff_user_existence(auth_user_guid, staff_user_id=user_id)
        auth_user = AuthService.get_epic_user_by_guid(auth_user_guid)
        if not auth_user:
            raise UnprocessableEntityError(
                f"No user found from EPIC.Authorize corresponding to the given {auth_user_guid}"
            )
        group_payload = {
            "app_name": AUTH_APP,
            "group_name": user_data.get("permission", None),
        }
        with session_scope() as session:
            permission = user_data.get("permission")
            user_data.pop("permission")
            updated_user = StaffUserModel.update_staff(user_id, user_data, session)
            if not user_data.get("is_active"):
                AuthService.delete_user_group(user.auth_user_guid, AUTH_APP)
            else:
                AuthService.update_user_group(auth_user_guid, group_payload)
                setattr(updated_user, "permission", permission)
            # Invalidate cache for the updated user
            CachedStaffUserService.invalidate_staff_cache(auth_user_guid)
        return updated_user

    @classmethod
    def delete_user(cls, user_id):
        """Delete the staff user entity permenantly from database."""
        with session_scope() as session:
            user = StaffUserModel.delete_staff_user(user_id, session)
            #  Here we have to delete all the AUTH_APP(COMPLIANEC) level permission from keycloak
            AuthService.delete_user_group(user.auth_user_guid, group=AUTH_APP)
            # Invalidate cache for the deleted user
            CachedStaffUserService.invalidate_staff_cache(user.auth_user_guid)
        return user

    @classmethod
    def get_permission_levels(cls):
        """List all the permission levels."""
        return [{"id": perm.name, "name": perm.value} for perm in PermissionEnum]


def _create_staff_user_object(user_data: dict, auth_user: dict):
    """Create a staff user object."""
    return {
        "first_name": auth_user.get("first_name", None),
        "last_name": auth_user.get("last_name", None),
        "position_id": user_data.get("position_id", None),
        "deputy_director_id": user_data.get("deputy_director_id"),
        "supervisor_id": user_data.get("supervisor_id", None),
        "auth_user_guid": auth_user.get("username", None),
        "is_active": auth_user.get("is_active"),
    }


def _get_level(group):
    """Get the level from the group, defaulting to 0 if not valid."""
    # Safely retrieve the level attribute and default to 0 if not valid
    level_str = group.get("level", 0)
    try:
        return int(level_str)
    except (ValueError, TypeError):
        return 0


def _set_permission_level_in_compliance_user_obj(
    compliance_user: StaffUserModel, auth_user: dict
) -> StaffUserModel:
    """Set the permission level in compliance user."""
    if auth_user and auth_user.get("groups", None):
        sorted_groups = sorted(auth_user.get("groups", None), key=_get_level)
        if (
            sorted_groups[-1]
            and sorted_groups[-1]["name"]
            and sorted_groups[-1]["name"] in [p.name for p in PermissionEnum]
        ):
            setattr(compliance_user, "permission", sorted_groups[-1]["name"])
    return compliance_user


def _validate_staff_user_existence(auth_user_guid: str, staff_user_id: int = None):
    """Check if the staff user exists."""
    existing_staff_user = StaffUserModel.get_by_auth_guid(auth_user_guid)
    if existing_staff_user and (
        not staff_user_id or existing_staff_user.id != staff_user_id
    ):
        raise ResourceExistsError(f"Staff user with the guid {auth_user_guid} exists")
