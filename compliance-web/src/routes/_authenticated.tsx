import { createFileRoute, Outlet } from "@tanstack/react-router";
import { useEffect } from "react";
import { useAuth } from "react-oidc-context";

export const Route = createFileRoute("/_authenticated")({
  component: Auth,
});

function Auth() {
  const { isAuthenticated, signinRedirect, isLoading } = useAuth();

  useEffect(() => {
    if (!isAuthenticated && !isLoading) {
      const cleanPathname = window.location.pathname.replace(/^\/compliance/, ''); // Remove "/compliance" prefix if present
      window.sessionStorage.setItem("redirectUrl", cleanPathname + window.location.search);
      signinRedirect({ extraQueryParams: { kc_idp_hint: "idir" } });
    }
  }, [isAuthenticated, isLoading, signinRedirect]);

  return <Outlet />;
}
