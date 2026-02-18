import { createFileRoute, Navigate } from "@tanstack/react-router";
import { useAuth } from "react-oidc-context";
import { useStaffUserValidation } from "@/hooks/useAuthorization";
import { notify } from "@/store/snackbarStore";

export const Route = createFileRoute("/oidc-callback")({
  component: OidcCallback,
});

function OidcCallback() {
  const { isAuthenticated, isLoading, error } = useAuth();
  const {
    isLoading: isValidatingStaff,
    isValidStaffUser,
    isAccessDenied,
    preferredUsername,
    error: staffValidationError
  } = useStaffUserValidation();

  if (isLoading || isValidatingStaff) {
    return <h1>Redirecting, Please wait...</h1>;
  }

  if (error?.message) {
    return <h1>Error: {error.message}</h1>;
  }

  if (staffValidationError && staffValidationError.message !== "No preferred_username found in token") {
    return <h1>Error validating user: {staffValidationError.message}</h1>;
  }

  if (isAccessDenied) {
    notify.error(`Access Denied: User ${preferredUsername} is not authorized to access this application. Please contact your administrator.`);
    return <h1>Access denied. Redirecting...</h1>;
  }

  if (!isLoading && isAuthenticated && isValidStaffUser) {
    const redirectUrl = window.sessionStorage.getItem("redirectUrl") || "/ce-database/case-files";
    return <Navigate to={redirectUrl} replace />;
  }

  return <h1>Authentication in progress...</h1>;
}
