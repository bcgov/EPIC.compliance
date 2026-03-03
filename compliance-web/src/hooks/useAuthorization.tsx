import { useMemo } from "react";
import { StaffUser } from "@/models/Staff";
import { jwtDecode, JwtPayload } from "jwt-decode";
import { useAuth } from "react-oidc-context";
import { useQuery } from "@tanstack/react-query";
import { request } from "@/utils/axiosUtils";
import { OidcConfig } from "@/utils/config";

interface CustomJwtPayload extends JwtPayload {
  resource_access?: {
    [key: string]: {
      roles: string[];
    };
  };
}

export const KC_USER_GROUPS = {
  SUPERUSER: "super_user",
  USER: "user",
  ADMIN: "admin",
  VIEWER: "viewer",
};

export const useIsRolesAllowed = (
  roles: string[],
  users?: StaffUser[]
): boolean => {
  const { user: authUser } = useAuth();

  return useMemo(() => {
    if (!authUser?.access_token) {
      return false;
    }

    const payload = jwtDecode<CustomJwtPayload>(authUser.access_token);

    // Get roles from resource_access if available
    const resourceRoles =
      payload.resource_access?.[OidcConfig.client_id]?.roles || [];

    // Check if the user has any of the required roles (from groups or resource_access)
    const isRoleAllowed = roles.some((role) => resourceRoles.includes(role));

    // Check if the logged-in user is part of the provided users list
    const isUserAllowed =
      users?.some(
        (user) => user?.auth_user_guid === authUser?.profile?.preferred_username
      ) ?? false;

    return isRoleAllowed || isUserAllowed;
  }, [authUser?.access_token, authUser?.profile?.preferred_username, roles, users]);
};

export const useCurrentLoggedInUser = () => {
  const { user } = useAuth();
  return user?.profile;
};

export const useStaffUserValidation = () => {
  const { user, isAuthenticated } = useAuth();
  const preferredUsername = user?.profile?.preferred_username;

  const {
    data: staffUser,
    isLoading,
    error,
    isError,
  } = useQuery({
    queryKey: ["staff-user-validation", preferredUsername],
    queryFn: async (): Promise<StaffUser | null> => {
      if (!preferredUsername) {
        throw new Error("No preferred_username found in token");
      }

      try {
        const response = await request({
          url: `/staff-users/by-auth-user-guid/${preferredUsername}`,
          method: "get"
        });
        return response;
      } catch (error: unknown) {
        // If user not found (404), return null instead of throwing
        if (error && typeof error === 'object' && 'response' in error && 
            error.response && typeof error.response === 'object' && 'status' in error.response &&
            error.response.status === 404) {
          return null;
        }
        throw error;
      }
    },
    enabled: isAuthenticated && !!preferredUsername,
    retry: false, // Don't retry if staff user doesn't exist
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  const isValidStaffUser = !!staffUser;
  const isAccessDenied = !isLoading && !isError && !isValidStaffUser;

  return {
    staffUser,
    isLoading,
    error,
    isValidStaffUser,
    isAccessDenied,
    preferredUsername,
  };
};
