import type { Meta, StoryObj } from "@storybook/react";
import React from "react";
import { Box, Button, Typography } from "@mui/material";
import SnackBarProvider from "@/components/Shared/Popups/SnackBarProvider";
import { useSnackbar, notify } from "@/store/snackbarStore";

// Demo component to show SnackBarProvider with different severities
const SnackBarProviderDemo = () => {
  const { setOpen } = useSnackbar();

  const showSuccess = () => {
    setOpen("Operation completed successfully!", "success");
  };

  const showError = () => {
    setOpen("An error occurred while processing your request.", "error");
  };

  const showWarning = () => {
    setOpen("Please review your input before proceeding.", "warning");
  };

  const showInfo = () => {
    setOpen("New updates are available for download.", "info");
  };

  const showCustomMessage = () => {
    setOpen("This is a custom message with detailed information about the current operation.", "info");
  };

  const showLongMessage = () => {
    setOpen(
      "This is a very long message that demonstrates how the snackbar handles longer text content. It should wrap properly and maintain good readability.",
      "warning"
    );
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        SnackBar Provider Examples
      </Typography>
      <Typography variant="body1" paragraph>
        Click the buttons below to show different types of snackbar notifications. The snackbar will appear in the bottom-right corner.
      </Typography>
      <Box sx={{ display: "flex", gap: "10px", flexWrap: "wrap", mb: 2 }}>
        <Button variant="contained" color="success" onClick={showSuccess}>
          Success Message
        </Button>
        <Button variant="contained" color="error" onClick={showError}>
          Error Message
        </Button>
        <Button variant="contained" color="warning" onClick={showWarning}>
          Warning Message
        </Button>
        <Button variant="contained" color="info" onClick={showInfo}>
          Info Message
        </Button>
      </Box>
      <Box sx={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        <Button variant="outlined" onClick={showCustomMessage}>
          Custom Message
        </Button>
        <Button variant="outlined" onClick={showLongMessage}>
          Long Message
        </Button>
      </Box>
      <SnackBarProvider />
    </Box>
  );
};

// Demo component using the notify helper functions
const NotifyHelperDemoComponent = () => {
  const showSuccessNotify = () => {
    notify.success("Data saved successfully!");
  };

  const showErrorNotify = () => {
    notify.error("Failed to save data. Please try again.");
  };

  const showWarningNotify = () => {
    notify.warning("Please check your internet connection.");
  };

  const showInfoNotify = () => {
    notify.info("New features are now available!");
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        Notify Helper Examples
      </Typography>
      <Typography variant="body1" paragraph>
        These examples use the notify helper functions for easier snackbar management.
      </Typography>
      <Box sx={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        <Button variant="contained" color="success" onClick={showSuccessNotify}>
          Success (notify.success)
        </Button>
        <Button variant="contained" color="error" onClick={showErrorNotify}>
          Error (notify.error)
        </Button>
        <Button variant="contained" color="warning" onClick={showWarningNotify}>
          Warning (notify.warning)
        </Button>
        <Button variant="contained" color="info" onClick={showInfoNotify}>
          Info (notify.info)
        </Button>
      </Box>
      <SnackBarProvider />
    </Box>
  );
};

const meta: Meta<typeof SnackBarProvider> = {
  title: "Shared/Popups/SnackBarProvider",
  component: SnackBarProvider,
  parameters: {
    layout: "fullscreen",
  },
  decorators: [
    (Story) => (
      <div style={{ width: "100%", height: "100vh" }}>
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof SnackBarProvider>;

export const InteractiveDemo: Story = {
  render: () => <SnackBarProviderDemo />,
};

export const NotifyHelperDemo: Story = {
  render: () => <NotifyHelperDemoComponent />,
};

export const SuccessMessage: Story = {
  render: () => {
    const { setOpen } = useSnackbar();

    React.useEffect(() => {
      setOpen("Operation completed successfully!", "success");
    }, [setOpen]);

    return <SnackBarProvider />;
  },
};

export const ErrorMessage: Story = {
  render: () => {
    const { setOpen } = useSnackbar();

    React.useEffect(() => {
      setOpen("An error occurred while processing your request.", "error");
    }, [setOpen]);

    return <SnackBarProvider />;
  },
};

export const WarningMessage: Story = {
  render: () => {
    const { setOpen } = useSnackbar();

    React.useEffect(() => {
      setOpen("Please review your input before proceeding.", "warning");
    }, [setOpen]);

    return <SnackBarProvider />;
  },
};

export const InfoMessage: Story = {
  render: () => {
    const { setOpen } = useSnackbar();

    React.useEffect(() => {
      setOpen("New updates are available for download.", "info");
    }, [setOpen]);

    return <SnackBarProvider />;
  },
};

export const LongMessage: Story = {
  render: () => {
    const { setOpen } = useSnackbar();

    React.useEffect(() => {
      setOpen(
        "This is a very long message that demonstrates how the snackbar handles longer text content. It should wrap properly and maintain good readability across different screen sizes.",
        "info"
      );
    }, [setOpen]);

    return <SnackBarProvider />;
  },
};

export const CustomSeverity: Story = {
  render: () => {
    const { setOpen } = useSnackbar();

    React.useEffect(() => {
      setOpen("This is a custom severity message.", "primary");
    }, [setOpen]);

    return <SnackBarProvider />;
  },
};
