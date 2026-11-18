import { Box, Button, Typography } from "@mui/material";
import { createFileRoute } from "@tanstack/react-router";
import { BCDesignTokens } from "epic.theme";
import { useEffect } from "react";
import { useAuth } from "react-oidc-context";
import { useDrawer } from "@/store/drawerStore";
import { useModal } from "@/store/modalStore";
import { usePopover } from "@/store/popoverStore";

export const Route = createFileRoute("/session-expired")({
  component: SessionExpired,
});

function SessionExpired() {
  const authentication = useAuth();

  // The drawer, modal and popover render outside the router, so navigating
  // here does not unmount them. Close whatever the expired session left open.
  useEffect(() => {
    useDrawer.getState().setClose();
    useModal.getState().setClose();
    usePopover.getState().setClose();
  }, []);

  return (
    <Box
      sx={{ padding: "2rem", textAlign: "center" }}
      gap={2}
      display="flex"
      flexDirection="column"
      alignItems="center"
    >
      <Typography
        variant="h1"
        sx={{ color: BCDesignTokens.typographyColorLink }}
      >
        Session Expired
      </Typography>
      <Typography variant="body1">
        Your session has expired. Please sign in again to continue.
      </Typography>
      <Button onClick={() => authentication.signinRedirect()}>Sign In</Button>
    </Box>
  );
}
