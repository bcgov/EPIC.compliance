import type { Meta, StoryObj } from "@storybook/react";
import React from "react";
import { Box, Button, Typography } from "@mui/material";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";
import { useModal } from "@/store/modalStore";
import ModalProvider from "@/components/Shared/Modals/ModalProvider";

// Demo component to show ConfirmationModal in different contexts
const ConfirmationModalDemo = () => {
  const { setOpen } = useModal();

  const openConfirmationModal = (
    title: string,
    description: string,
    confirmText?: string,
    cancelText?: string
  ) => {
    setOpen({
      content: (
        <ConfirmationModal
          title={title}
          description={description}
          confirmButtonText={confirmText}
          cancelButtonText={cancelText}
          onConfirm={() => {
            console.log("Confirmed");
            setOpen({ content: null });
          }}
          onCancel={() => {
            console.log("Cancelled");
            setOpen({ content: null });
          }}
        />
      ),
      width: "400px",
    });
  };

  const openFormattedModal = () => {
    setOpen({
      content: (
        <ConfirmationModal
          title="Delete Item"
          formattedDescription={
            <Box>
              <Typography variant="body1" paragraph>
                Are you sure you want to delete this item?
              </Typography>
              <Typography variant="body2" color="error">
                This action cannot be undone.
              </Typography>
            </Box>
          }
          confirmButtonText="Delete"
          cancelButtonText="Keep"
          onConfirm={() => {
            console.log("Item deleted");
            setOpen({ content: null });
          }}
          onCancel={() => {
            console.log("Deletion cancelled");
            setOpen({ content: null });
          }}
        />
      ),
      width: "400px",
    });
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        Confirmation Modal Examples
      </Typography>
      <Typography variant="body1" paragraph>
        These examples demonstrate the ConfirmationModal component in different
        configurations.
      </Typography>
      <Box sx={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        <Button
          variant="contained"
          onClick={() =>
            openConfirmationModal(
              "Confirm Action",
              "Are you sure you want to proceed with this action?",
              "Yes, Proceed",
              "Cancel"
            )
          }
        >
          Basic Confirmation
        </Button>
        <Button
          variant="contained"
          onClick={() =>
            openConfirmationModal(
              "Save Changes",
              "Do you want to save your changes before leaving?",
              "Save",
              "Don't Save"
            )
          }
        >
          Save Confirmation
        </Button>
        <Button
          variant="contained"
          onClick={() =>
            openConfirmationModal(
              "Discard Changes",
              "You have unsaved changes. Are you sure you want to discard them?",
              "Discard",
              "Keep Editing"
            )
          }
        >
          Discard Confirmation
        </Button>
        <Button variant="contained" onClick={openFormattedModal}>
          Formatted Description
        </Button>
      </Box>
      <ModalProvider />
    </Box>
  );
};

const meta: Meta<typeof ConfirmationModal> = {
  title: "Shared/Popups/ConfirmationModal",
  component: ConfirmationModal,
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
type Story = StoryObj<typeof ConfirmationModal>;

export const InteractiveDemo: Story = {
  render: () => <ConfirmationModalDemo />,
};

export const BasicConfirmation: Story = {
  render: () => {
    const { setOpen } = useModal();

    React.useEffect(() => {
      setOpen({
        content: (
          <ConfirmationModal
            title="Confirm Action"
            description="Are you sure you want to proceed with this action?"
            confirmButtonText="Yes, Proceed"
            cancelButtonText="Cancel"
            onConfirm={() => console.log("Confirmed")}
            onCancel={() => console.log("Cancelled")}
          />
        ),
        width: "400px",
      });
    }, [setOpen]);

    return <ModalProvider />;
  },
};

export const SaveConfirmation: Story = {
  render: () => {
    const { setOpen } = useModal();

    React.useEffect(() => {
      setOpen({
        content: (
          <ConfirmationModal
            title="Save Changes"
            description="Do you want to save your changes before leaving?"
            confirmButtonText="Save"
            cancelButtonText="Don't Save"
            onConfirm={() => console.log("Changes saved")}
            onCancel={() => console.log("Changes not saved")}
          />
        ),
        width: "400px",
      });
    }, [setOpen]);

    return <ModalProvider />;
  },
};

export const DeleteConfirmation: Story = {
  render: () => {
    const { setOpen } = useModal();

    React.useEffect(() => {
      setOpen({
        content: (
          <ConfirmationModal
            title="Delete Item"
            description="Are you sure you want to delete this item? This action cannot be undone."
            confirmButtonText="Delete"
            cancelButtonText="Cancel"
            onConfirm={() => console.log("Item deleted")}
            onCancel={() => console.log("Deletion cancelled")}
          />
        ),
        width: "400px",
      });
    }, [setOpen]);

    return <ModalProvider />;
  },
};

export const WithFormattedDescription: Story = {
  render: () => {
    const { setOpen } = useModal();

    React.useEffect(() => {
      setOpen({
        content: (
          <ConfirmationModal
            title="Delete Item"
            formattedDescription={
              <Box>
                <Typography variant="body1" paragraph>
                  Are you sure you want to delete this item?
                </Typography>
                <Typography variant="body2" color="error">
                  This action cannot be undone.
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  All associated data will be permanently removed.
                </Typography>
              </Box>
            }
            confirmButtonText="Delete"
            cancelButtonText="Keep"
            onConfirm={() => console.log("Item deleted")}
            onCancel={() => console.log("Deletion cancelled")}
          />
        ),
        width: "450px",
      });
    }, [setOpen]);

    return <ModalProvider />;
  },
};

export const CustomButtonTexts: Story = {
  render: () => {
    const { setOpen } = useModal();

    React.useEffect(() => {
      setOpen({
        content: (
          <ConfirmationModal
            title="Custom Buttons"
            description="This example shows custom button text for both confirm and cancel actions."
            confirmButtonText="Accept Terms"
            cancelButtonText="Decline"
            onConfirm={() => console.log("Terms accepted")}
            onCancel={() => console.log("Terms declined")}
          />
        ),
        width: "400px",
      });
    }, [setOpen]);

    return <ModalProvider />;
  },
};

export const DefaultButtonTexts: Story = {
  render: () => {
    const { setOpen } = useModal();

    React.useEffect(() => {
      setOpen({
        content: (
          <ConfirmationModal
            title="Default Buttons"
            description="This example uses the default button text (Confirm/Cancel)."
            onConfirm={() => console.log("Confirmed")}
            onCancel={() => console.log("Cancelled")}
          />
        ),
        width: "400px",
      });
    }, [setOpen]);

    return <ModalProvider />;
  },
};
