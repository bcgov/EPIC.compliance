import { StaffUser } from "@/models/Staff";
import { jwtDecode, JwtPayload } from "jwt-decode";
import { useAuth } from "react-oidc-context";
import { CLIENT_ID } from "@/utils/config";

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
  
  if (!authUser?.access_token) {
    return false;
  }

  const payload = jwtDecode<CustomJwtPayload>(authUser.access_token);
  
  // Get roles from resource_access if available
  const resourceRoles = payload.resource_access?.[CLIENT_ID]?.roles || [];
  
  // Check if the user has any of the required roles (from groups or resource_access)
  const isRoleAllowed = roles.some((role) => 
    resourceRoles.includes(role)
  );

  // Check if the logged-in user is part of the provided users list
  const isUserAllowed =
    users?.some(
      (user) => user?.auth_user_guid === authUser?.profile?.preferred_username
    ) ?? false;

  return isRoleAllowed || isUserAllowed;
};

export const useCurrentLoggedInUser = () => {
  const { user } = useAuth();
  return user?.profile;
};
