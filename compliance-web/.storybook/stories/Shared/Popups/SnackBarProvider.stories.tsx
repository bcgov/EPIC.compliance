import type { Meta, StoryObj } from "@storybook/react";
import React from "react";
import { Box, Button, Typography, Paper, Alert, Chip } from "@mui/material";
import { Info as InfoIcon, CheckCircle as CheckCircleIcon, Error as ErrorIcon, Warning as WarningIcon } from "@mui/icons-material";
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
  tags: ['autodocs'],
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

// Documentation component
const DocumentationSection = () => {
  return (
    <Box sx={{ padding: "24px", maxWidth: "1200px", margin: "0 auto" }}>
      <Typography variant="h3" gutterBottom sx={{ mb: 4 }}>
        SnackBarProvider Documentation
      </Typography>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <InfoIcon color="primary" />
          Overview
        </Typography>
        <Typography variant="body1" paragraph>
          The SnackBarProvider is a React component that provides a centralized notification system for displaying temporary messages to users. It uses Material-UI's Snackbar component and integrates with a global state management system to show notifications with different severity levels.
        </Typography>
        <Typography variant="body1" paragraph>
          This component is designed to be used throughout the application to provide user feedback for various actions such as form submissions, API calls, and general notifications.
        </Typography>
      </Paper>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <CheckCircleIcon color="success" />
          Features
        </Typography>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Chip label="Multiple Severity Levels" color="primary" size="small" />
            <Typography variant="body2">Success, Error, Warning, Info, and custom severities</Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Chip label="Auto-dismiss" color="primary" size="small" />
            <Typography variant="body2">Configurable auto-dismiss timing</Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Chip label="Manual Dismiss" color="primary" size="small" />
            <Typography variant="body2">Users can manually close notifications</Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Chip label="Global State" color="primary" size="small" />
            <Typography variant="body2">Centralized state management with Zustand</Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Chip label="Responsive Design" color="primary" size="small" />
            <Typography variant="body2">Adapts to different screen sizes</Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Chip label="Accessibility" color="primary" size="small" />
            <Typography variant="body2">Built-in accessibility features</Typography>
          </Box>
        </Box>
      </Paper>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <ErrorIcon color="error" />
          Severity Types
        </Typography>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Alert severity="success" sx={{ minWidth: "200px" }}>
              Success
            </Alert>
            <Typography variant="body2">
              Used for successful operations, confirmations, and positive feedback
            </Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Alert severity="error" sx={{ minWidth: "200px" }}>
              Error
            </Alert>
            <Typography variant="body2">
              Used for errors, failures, and critical issues that require attention
            </Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Alert severity="warning" sx={{ minWidth: "200px" }}>
              Warning
            </Alert>
            <Typography variant="body2">
              Used for warnings, potential issues, and important notices
            </Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Alert severity="info" sx={{ minWidth: "200px" }}>
              Info
            </Alert>
            <Typography variant="body2">
              Used for general information, updates, and neutral notifications
            </Typography>
          </Box>
        </Box>
      </Paper>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <WarningIcon color="warning" />
          Usage Examples
        </Typography>
        
        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          Method 1: Using the useSnackbar Hook
        </Typography>
        <Box sx={{ backgroundColor: "#f5f5f5", p: 2, borderRadius: 1, fontFamily: "monospace", mb: 2 }}>
          <Typography variant="body2" component="pre">
{`import { useSnackbar } from '@/store/snackbarStore';

const MyComponent = () => {
  const { setOpen } = useSnackbar();

  const handleSuccess = () => {
    setOpen("Operation completed successfully!", "success");
  };

  return (
    <div>
      <button onClick={handleSuccess}>Save</button>
    </div>
  );
};`}
          </Typography>
        </Box>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          Method 2: Using the notify Helper Functions
        </Typography>
        <Box sx={{ backgroundColor: "#f5f5f5", p: 2, borderRadius: 1, fontFamily: "monospace", mb: 2 }}>
          <Typography variant="body2" component="pre">
{`import { notify } from '@/store/snackbarStore';

const MyComponent = () => {
  const handleSave = async () => {
    try {
      await saveData();
      notify.success("Data saved successfully!");
    } catch (error) {
      notify.error("Failed to save data. Please try again.");
    }
  };

  return (
    <div>
      <button onClick={handleSave}>Save</button>
    </div>
  );
};`}
          </Typography>
        </Box>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          Component Setup
        </Typography>
        <Box sx={{ backgroundColor: "#f5f5f5", p: 2, borderRadius: 1, fontFamily: "monospace" }}>
          <Typography variant="body2" component="pre">
{`// In your main App component or layout
import SnackBarProvider from '@/components/Shared/Popups/SnackBarProvider';

const App = () => {
  return (
    <div>
      {/* Your app content */}
      <SnackBarProvider />
    </div>
  );
};`}
          </Typography>
        </Box>
      </Paper>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          API Reference
        </Typography>
        
        <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
          useSnackbar Hook
        </Typography>
        <Typography variant="body2" component="div" sx={{ mb: 2 }}>
          <strong>Returns:</strong> An object with the following properties:
        </Typography>
        <Box sx={{ ml: 2 }}>
          <Typography variant="body2" component="div">
            • <strong>setOpen</strong>: (message: string, severity: SeverityType) =&gt; void
          </Typography>
          <Typography variant="body2" component="div">
            • <strong>closeSnackbar</strong>: () =&gt; void
          </Typography>
        </Box>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          notify Helper Functions
        </Typography>
        <Box sx={{ ml: 2 }}>
          <Typography variant="body2" component="div">
            • <strong>notify.success(message: string)</strong>: Shows a success notification
          </Typography>
          <Typography variant="body2" component="div">
            • <strong>notify.error(message: string)</strong>: Shows an error notification
          </Typography>
          <Typography variant="body2" component="div">
            • <strong>notify.warning(message: string)</strong>: Shows a warning notification
          </Typography>
          <Typography variant="body2" component="div">
            • <strong>notify.info(message: string)</strong>: Shows an info notification
          </Typography>
        </Box>

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          SeverityType
        </Typography>
        <Typography variant="body2">
          "success" | "error" | "warning" | "info" | "primary" | "secondary"
        </Typography>
      </Paper>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Best Practices
        </Typography>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          <Alert severity="info">
            <Typography variant="body2">
              <strong>Keep messages concise:</strong> Use clear, brief messages that users can quickly understand.
            </Typography>
          </Alert>
          <Alert severity="info">
            <Typography variant="body2">
              <strong>Choose appropriate severity:</strong> Match the severity level to the importance and nature of the message.
            </Typography>
          </Alert>
          <Alert severity="info">
            <Typography variant="body2">
              <strong>Provide actionable feedback:</strong> When possible, include next steps or context in your messages.
            </Typography>
          </Alert>
          <Alert severity="info">
            <Typography variant="body2">
              <strong>Don't overuse:</strong> Avoid showing too many notifications at once, as this can overwhelm users.
            </Typography>
          </Alert>
        </Box>
      </Paper>
    </Box>
  );
};

export const Documentation: Story = {
  render: () => <DocumentationSection />,
  parameters: {
    docs: {
      description: {
        component: "Comprehensive documentation for the SnackBarProvider component including usage examples, API reference, and best practices."
      }
    }
  }
};
