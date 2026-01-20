"""Service to call epic.authorize endpoints."""

import requests
from flask import current_app, g

from compliance_api.exceptions import BusinessError
from compliance_api.utils.cache import cache
from compliance_api.utils.constant import AUTH_APP
from compliance_api.utils.enum import HttpMethod

from .constant import API_REQUEST_TIMEOUT


class AuthService:
    """Handle service request for epic.authorize with integrated cache management."""

    @staticmethod
    def get_epic_user_by_guid(auth_user_guid: str):
        """
        Return the user representation from epic.authorize (cached).

        This is called frequently for individual user lookups,
        so we cache it with the user's token hash for security.
        """
        from compliance_api.services.cached_staff_user import CachedStaffUserService

        # Include token hash in cache key for security
        token_hash = CachedStaffUserService._get_token_hash()
        cache_key = f"auth_user:{auth_user_guid}:{token_hash}"

        cached_result = cache.get(cache_key)
        if cached_result is not None:
            current_app.logger.debug(f"Cache hit for auth user {auth_user_guid}")
            return cached_result

        current_app.logger.debug(f"Cache miss for auth user {auth_user_guid}")

        auth_user_response = _request_auth_service(f"users/{auth_user_guid}")
        if auth_user_response.status_code != 200:
            raise BusinessError(
                f"Error finding user with ID {auth_user_guid} from auth server"
            )

        result = auth_user_response.json()
        cache.set(cache_key, result, timeout=180)  # 3 minutes
        return result

    @staticmethod
    def get_epic_users_by_app():
        """
        Return all users belonging to COMPLIANCE app with caching.

        This caches per-user to prevent data leakage.
        """
        from compliance_api.services.cached_staff_user import CachedStaffUserService
        from compliance_api.utils.constant import AUTH_APP
        from compliance_api.exceptions import BusinessError

        # Include token hash in cache key for security
        token_hash = CachedStaffUserService._get_token_hash()
        cache_key = f"auth_users_app:{AUTH_APP}:{token_hash}"

        cached_result = cache.get(cache_key)
        if cached_result is not None:
            current_app.logger.debug("Cache hit for auth users by app")
            return cached_result

        current_app.logger.debug("Cache miss for auth users by app")

        # Fetch from auth service
        auth_users_response = _request_auth_service(f"users?app_name={AUTH_APP}")
        if auth_users_response.status_code != 200:
            raise BusinessError(f"Error fetching users for the app {AUTH_APP}")

        result = auth_users_response.json()
        cache.set(cache_key, result, timeout=180)  # 3 minutes
        return result

    @staticmethod
    def update_user_group(auth_user_guid: str, payload: dict):
        """Update user group and invalidate all related caches."""
        from compliance_api.services.cached_staff_user import CachedStaffUserService
        from compliance_api.utils.enum import HttpMethod
        from compliance_api.exceptions import BusinessError

        update_group_response = _request_auth_service(
            f"users/{auth_user_guid}/groups", HttpMethod.PUT, payload
        )
        if update_group_response.status_code != 204:
            raise BusinessError(
                f"Update group in the auth server failed for user : {auth_user_guid}"
            )

        # Invalidate auth caches for this specific user
        AuthService._invalidate_auth_user_cache(auth_user_guid)

        # Invalidate the "all users by app" cache since this user's groups changed
        AuthService._invalidate_auth_users_by_app_cache()

        # Invalidate ALL staff caches since permissions changed
        CachedStaffUserService.invalidate_staff_cache(auth_user_guid)

        return update_group_response

    @staticmethod
    def delete_user_group(auth_user_guid: str, group: str, del_sub_group_mappings=True):
        """Delete user group and invalidate all related caches."""
        from compliance_api.services.cached_staff_user import CachedStaffUserService
        from compliance_api.utils.enum import HttpMethod
        from compliance_api.exceptions import BusinessError

        delete_response = _request_auth_service(
            f"users/{auth_user_guid}/groups/{group}?del_sub_group_mappings={del_sub_group_mappings}",
            HttpMethod.DELETE,
        )
        if delete_response.status_code != 204:
            raise BusinessError("Delete group mapping failed")

        # Invalidate auth caches for this specific user
        AuthService._invalidate_auth_user_cache(auth_user_guid)

        # Invalidate the "all users by app" cache since this user's groups changed
        AuthService._invalidate_auth_users_by_app_cache()

        # Invalidate ALL staff caches since permissions changed
        CachedStaffUserService.invalidate_staff_cache(auth_user_guid)

        return delete_response

    @staticmethod
    def _invalidate_auth_user_cache(auth_user_guid: str):
        """
        Invalidate the individual auth user cache.

        Since cache keys include token hashes, we can't delete all variations.
        Instead, we use a pattern-based approach or accept that cache will expire naturally.
        """
        from compliance_api.services.cached_staff_user import CachedStaffUserService

        # Get current token hash
        token_hash = CachedStaffUserService._get_token_hash()
        cache_key = f"auth_user:{auth_user_guid}:{token_hash}"

        cache.delete(cache_key)
        current_app.logger.info(f"Invalidated auth user cache for {auth_user_guid}")

    @staticmethod
    def _invalidate_auth_users_by_app_cache():
        """
        Invalidate the "all users by app" cache.

        Since cache keys include token hashes, we can't delete all variations.
        Instead, we delete for the current token.
        """
        from compliance_api.services.cached_staff_user import CachedStaffUserService

        # Get current token hash
        token_hash = CachedStaffUserService._get_token_hash()
        cache_key = f"auth_users_app:{AUTH_APP}:{token_hash}"

        cache.delete(cache_key)
        current_app.logger.info("Invalidated auth users by app cache")


def _request_auth_service(
    relative_url, http_method: HttpMethod = HttpMethod.GET, data=None
):
    """REST Api call to authorize service."""
    token = getattr(g, "access_token", None)
    if not token:
        raise BusinessError("No access token found", 401)
    auth_base_url = current_app.config["AUTH_BASE_URL"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "App-Id": AUTH_APP,
    }

    url = f"{auth_base_url}/api/{relative_url}"

    if http_method == HttpMethod.GET:
        response = requests.get(url, headers=headers, timeout=API_REQUEST_TIMEOUT)
    elif http_method == HttpMethod.PUT:
        response = requests.put(
            url, headers=headers, json=data, timeout=API_REQUEST_TIMEOUT
        )
    elif http_method == HttpMethod.PATCH:
        response = requests.patch(
            url, headers=headers, json=data, timeout=API_REQUEST_TIMEOUT
        )
    elif http_method == HttpMethod.DELETE:
        response = requests.delete(url, headers=headers, timeout=API_REQUEST_TIMEOUT)
    else:
        raise ValueError("Invalid HTTP method")
    response.raise_for_status()
    return response
