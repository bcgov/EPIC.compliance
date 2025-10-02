import React from "react";
import { Snackbar, Alert } from "@mui/material";
import { useSnackbar } from "@/store/snackbarStore";

const SnackBarProvider: React.FC = () => {
  const { isOpen, setClose, severity, message } = useSnackbar();

  return (
    <Snackbar
      open={isOpen}
      autoHideDuration={3000}
      onClose={setClose}
      anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
    >
      <Alert
        onClose={setClose}
        severity={severity}
        variant="filled"
        sx={{ 
          width: "100%",
          fontWeight: 600,
          '& .MuiAlert-action': {
            '& .MuiIconButton-root': {
              color: 'white',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
            },
          },
        }}
      >
        {message}
      </Alert>
    </Snackbar>
  );
};

export default SnackBarProvider;
