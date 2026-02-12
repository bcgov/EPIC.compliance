import { RouterProvider } from "@tanstack/react-router";
import { useAuth } from "react-oidc-context";
import router from "./router";
import { useEffect } from "react";
import { useStaffUserValidation } from "@/hooks/useAuthorization";
import { trackAnalytics } from "@epic/centre-analytics";
import { AppConfig } from "@/utils/config";

// Register the router instance for type safety
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

export default function RouterProviderWithAuthContext() {
  const authentication = useAuth();
  const { isAccessDenied, preferredUsername } = useStaffUserValidation();

  useEffect(() => {
    const removeExpiring = authentication.events.addAccessTokenExpiring(() => {
      // eslint-disable-next-line no-console
      console.log("AccessTokenExpiring: Refreshing token");
      try{
        authentication.signinSilent();
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error("Silent renew failed", error);
        authentication.signoutRedirect();
      }
    });

    const removeSilentRenewError = authentication.events.addSilentRenewError((error) => {
      // eslint-disable-next-line no-console
      console.log("Silent renew failed, logging out", error);
      authentication.signoutRedirect();
    });

    const removeExpired = authentication.events.addAccessTokenExpired(() => {
      // eslint-disable-next-line no-console
      console.log("Token expired, logging out");
      authentication.signoutRedirect();
    });

    return () => {
      removeExpiring();
      removeSilentRenewError();
      removeExpired();
    };
  }, [authentication, authentication.events, authentication.signinSilent, authentication.signoutRedirect]);

  // Show access denied if user is authenticated but not a valid staff user
  if (authentication.isAuthenticated && isAccessDenied) {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>
        <h1>Access Denied</h1>
        <p>You are not authorized to access this application.</p>
        <p>User ID: {preferredUsername}</p>
        <p>Please contact your administrator to get access.</p>
        <button 
          onClick={() => authentication.signoutRedirect()}
          style={{
            padding: "0.5rem 1rem",
            marginTop: "1rem",
            backgroundColor: "#dc3545",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer"
          }}
        >
          Sign Out
        </button>
      </div>
    );
  }

  trackAnalytics({
    appName: "epic_compliance",
    centreApiUrl: AppConfig.centreAPIUrl,
    enabled: authentication.isAuthenticated && !!authentication.user,
  });

  return <RouterProvider router={router} context={{ authentication }} />;
}
