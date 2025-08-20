import React from "react";
import { Box } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import { useFormContext } from "react-hook-form";
import LoadingButton from "@/components/Shared/LoadingButton";

const DrawerActionBarTop: React.FC<{
  isShowActionBar: boolean;
  isLoading?: boolean;
}> = React.memo(({ isShowActionBar, isLoading }) => {
  const {
    formState: { isValid },
  } = useFormContext();

  return isShowActionBar ? (
    <Box
      sx={{
        backgroundColor: BCDesignTokens.surfaceColorBackgroundLightGray,
        padding: "0.75rem 2rem",
        textAlign: "right",
      }}
    >
      <LoadingButton type="submit" disabled={!isValid} isLoading={isLoading}>
        Create
      </LoadingButton>
    </Box>
  ) : null;
});

export default DrawerActionBarTop;
