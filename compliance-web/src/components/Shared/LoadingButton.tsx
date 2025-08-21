import { Box, Button, ButtonProps, CircularProgress } from "@mui/material";

const LoadingButton = ({
  isLoading,
  loadingText = "Loading...",
  ...props
}: ButtonProps & { isLoading?: boolean; loadingText?: string }) => {
  return (
    <Button {...props} disabled={isLoading || props.disabled}>
      {isLoading ? (
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <CircularProgress size={20} color="inherit" sx={{ mr: 1 }} />
          {loadingText}
        </Box>
      ) : (
        props.children
      )}
    </Button>
  );
};

export default LoadingButton;
