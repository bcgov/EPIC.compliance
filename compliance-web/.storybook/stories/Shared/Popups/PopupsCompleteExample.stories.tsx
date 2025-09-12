import type { Meta, StoryObj } from "@storybook/react";
import React from "react";
import { Box, Button, Typography } from "@mui/material";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";
import SnackBarProvider from "@/components/Shared/Popups/SnackBarProvider";
import { useModal } from "@/store/modalStore";
import { useSnackbar, notify } from "@/store/snackbarStore";
import ModalProvider from "@/components/Shared/Modals/ModalProvider";

// Demo component showing both ConfirmationModal and SnackBarProvider working together
const PopupsCompleteDemo = () => {
  const { setOpen } = useModal();
  const { setOpen: setSnackbarOpen } = useSnackbar();

  const showConfirmationWithSnackbar = () => {
    setOpen({
      content: (
        <ConfirmationModal
          title="Save Changes"
          description="Do you want to save your changes before leaving?"
          confirmButtonText="Save"
          cancelButtonText="Don't Save"
          onConfirm={() => {
            console.log("Changes saved");
            setOpen({ content: null });
            setSnackbarOpen("Changes saved successfully!", "success");
          }}
          onCancel={() => {
            console.log("Changes not saved");
            setOpen({ content: null });
            setSnackbarOpen("Changes discarded", "warning");
          }}
        />
      ),
      width: "400px",
    });
  };

  const showDeleteConfirmationWithSnackbar = () => {
    setOpen({
      content: (
        <ConfirmationModal
          title="Delete Item"
          description="Are you sure you want to delete this item? This action cannot be undone."
          confirmButtonText="Delete"
          cancelButtonText="Cancel"
          onConfirm={() => {
            console.log("Item deleted");
            setOpen({ content: null });
            setSnackbarOpen("Item deleted successfully", "success");
          }}
          onCancel={() => {
            console.log("Deletion cancelled");
            setOpen({ content: null });
            setSnackbarOpen("Deletion cancelled", "info");
          }}
        />
      ),
      width: "400px",
    });
  };

  const showFormattedConfirmation = () => {
    setOpen({
      content: (
        <ConfirmationModal
          title="Update Profile"
          formattedDescription={
            <Box>
              <Typography variant="body1" paragraph>
                Your profile will be updated with the following changes:
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Email address will be changed
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Phone number will be updated
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Notification preferences will be reset
              </Typography>
            </Box>
          }
          confirmButtonText="Update Profile"
          cancelButtonText="Cancel"
          onConfirm={() => {
            console.log("Profile updated");
            setOpen({ content: null });
            setSnackbarOpen("Profile updated successfully!", "success");
          }}
          onCancel={() => {
            console.log("Update cancelled");
            setOpen({ content: null });
            setSnackbarOpen("Profile update cancelled", "info");
          }}
        />
      ),
      width: "450px",
    });
  };

  const showErrorWithRetry = () => {
    setOpen({
      content: (
        <ConfirmationModal
          title="Operation Failed"
          description="The operation could not be completed. Would you like to try again?"
          confirmButtonText="Retry"
          cancelButtonText="Cancel"
          onConfirm={() => {
            console.log("Retrying operation");
            setOpen({ content: null });
            setSnackbarOpen("Retrying operation...", "info");
            // Simulate retry
            setTimeout(() => {
              setSnackbarOpen("Operation completed successfully!", "success");
            }, 2000);
          }}
          onCancel={() => {
            console.log("Operation cancelled");
            setOpen({ content: null });
            setSnackbarOpen("Operation cancelled", "warning");
          }}
        />
      ),
      width: "400px",
    });
  };

  const showMultipleSnackbars = () => {
    setSnackbarOpen("First notification", "info");
    setTimeout(() => {
      setSnackbarOpen("Second notification", "success");
    }, 1000);
    setTimeout(() => {
      setSnackbarOpen("Third notification", "warning");
    }, 2000);
  };

  const showNotifyHelpers = () => {
    notify.success("Success notification using helper");
    setTimeout(() => {
      notify.error("Error notification using helper");
    }, 1000);
    setTimeout(() => {
      notify.warning("Warning notification using helper");
    }, 2000);
    setTimeout(() => {
      notify.info("Info notification using helper");
    }, 3000);
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        Complete Popups Examples
      </Typography>
      <Typography variant="body1" paragraph>
        These examples demonstrate how ConfirmationModal and SnackBarProvider work together
        to provide a complete user feedback system.
      </Typography>
      
      <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
        Confirmation Modals with Snackbar Feedback
      </Typography>
      <Box sx={{ display: "flex", gap: "10px", flexWrap: "wrap", mb: 3 }}>
        <Button variant="contained" onClick={showConfirmationWithSnackbar}>
          Save Confirmation
        </Button>
        <Button variant="contained" color="error" onClick={showDeleteConfirmationWithSnackbar}>
          Delete Confirmation
        </Button>
        <Button variant="contained" onClick={showFormattedConfirmation}>
          Formatted Confirmation
        </Button>
        <Button variant="contained" color="warning" onClick={showErrorWithRetry}>
          Error with Retry
        </Button>
      </Box>

      <Typography variant="h6" gutterBottom>
        Snackbar Notifications
      </Typography>
      <Box sx={{ display: "flex", gap: "10px", flexWrap: "wrap", mb: 3 }}>
        <Button variant="outlined" onClick={showMultipleSnackbars}>
          Multiple Snackbars
        </Button>
        <Button variant="outlined" onClick={showNotifyHelpers}>
          Notify Helpers
        </Button>
      </Box>

      <ModalProvider />
      <SnackBarProvider />
    </Box>
  );
};

const meta: Meta<typeof SnackBarProvider> = {
  title: "Shared/Popups/Complete Example",
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
  render: () => <PopupsCompleteDemo />,
};

export const ConfirmationWithSuccess: Story = {
  render: () => {
    const { setOpen } = useModal();
    const { setOpen: setSnackbarOpen } = useSnackbar();

    React.useEffect(() => {
      setOpen({
        content: (
          <ConfirmationModal
            title="Save Changes"
            description="Do you want to save your changes before leaving?"
            confirmButtonText="Save"
            cancelButtonText="Don't Save"
            onConfirm={() => {
              console.log("Changes saved");
              setOpen({ content: null });
              setSnackbarOpen("Changes saved successfully!", "success");
            }}
            onCancel={() => {
              console.log("Changes not saved");
              setOpen({ content: null });
              setSnackbarOpen("Changes discarded", "warning");
            }}
          />
        ),
        width: "400px",
      });
    }, [setOpen, setSnackbarOpen]);

    return (
      <>
        <ModalProvider />
        <SnackBarProvider />
      </>
    );
  },
};

export const DeleteWithFeedback: Story = {
  render: () => {
    const { setOpen } = useModal();
    const { setOpen: setSnackbarOpen } = useSnackbar();

    React.useEffect(() => {
      setOpen({
        content: (
          <ConfirmationModal
            title="Delete Item"
            description="Are you sure you want to delete this item? This action cannot be undone."
            confirmButtonText="Delete"
            cancelButtonText="Cancel"
            onConfirm={() => {
              console.log("Item deleted");
              setOpen({ content: null });
              setSnackbarOpen("Item deleted successfully", "success");
            }}
            onCancel={() => {
              console.log("Deletion cancelled");
              setOpen({ content: null });
              setSnackbarOpen("Deletion cancelled", "info");
            }}
          />
        ),
        width: "400px",
      });
    }, [setOpen, setSnackbarOpen]);

    return (
      <>
        <ModalProvider />
        <SnackBarProvider />
      </>
    );
  },
};

export const MultipleNotifications: Story = {
  render: () => {
    const { setOpen: setSnackbarOpen } = useSnackbar();

    React.useEffect(() => {
      setSnackbarOpen("First notification", "info");
      setTimeout(() => {
        setSnackbarOpen("Second notification", "success");
      }, 1000);
      setTimeout(() => {
        setSnackbarOpen("Third notification", "warning");
      }, 2000);
    }, [setSnackbarOpen]);

    return <SnackBarProvider />;
  },
};

export const NotifyHelpersSequence: Story = {
  render: () => {
    React.useEffect(() => {
      notify.success("Success notification using helper");
      setTimeout(() => {
        notify.error("Error notification using helper");
      }, 1000);
      setTimeout(() => {
        notify.warning("Warning notification using helper");
      }, 2000);
      setTimeout(() => {
        notify.info("Info notification using helper");
      }, 3000);
    }, []);

    return <SnackBarProvider />;
  },
};
