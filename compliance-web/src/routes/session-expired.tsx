import { Box, Button, Typography } from "@mui/material";
import { createFileRoute } from "@tanstack/react-router";
import { BCDesignTokens } from "epic.theme";
import { useAuth } from "react-oidc-context";

export const Route = createFileRoute("/session-expired")({
  component: SessionExpired,
});

function SessionExpired() {
  const authentication = useAuth();

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
