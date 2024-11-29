import { StaffUser } from "@/models/Staff";
import { jwtDecode, JwtPayload } from "jwt-decode";
import { useAuth } from "react-oidc-context";

interface CustomJwtPayload extends JwtPayload {
  groups?: string[];
}

export const KC_USER_GROUPS = {
  SUPERUSER: "/COMPLIANCE/SUPERUSER",
  USER: "/COMPLIANCE/USER",
  ADMIN: "/COMPLIANCE/ADMIN",
  VIEWER: "/COMPLIANCE/VIEWER",
};

export const useIsRolesAllowed = (
  roles: string[],
  users?: StaffUser[]
): boolean => {
  const { user: authUser } = useAuth();
  
  if (!authUser?.access_token) {
    return false;
  }

  const { groups = [] } = jwtDecode<CustomJwtPayload>(authUser.access_token);

  // Check if the user has any of the required roles
  const isRoleAllowed = roles.some((role) => groups.includes(role));

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
