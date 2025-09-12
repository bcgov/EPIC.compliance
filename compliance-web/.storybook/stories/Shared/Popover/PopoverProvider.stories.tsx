import type { Meta, StoryObj } from "@storybook/react";
import React from "react";
import { Box, Button, Typography, DialogContent } from "@mui/material";
import PopoverProvider from "@/components/Shared/Popover/PopoverProvider";
import PopoverActions from "@/components/Shared/Popover/PopoverActions";
import { usePopover } from "@/store/popoverStore";

// Demo component to show PopoverProvider with different content
const PopoverProviderDemo = () => {
  const { setOpen } = usePopover();

  const openPopover = (content: React.ReactNode, width?: string) => {
    const button = document.getElementById("trigger-button");
    if (button) {
      setOpen({ anchorEl: button, content, width });
    }
  };

  const openBasicPopover = () => {
    const button = document.getElementById("trigger-button");
    if (button) {
      setOpen({
        anchorEl: button,
        content: (
          <Box>
            <DialogContent dividers>
              <Typography variant="h6" gutterBottom>
                Basic Popover
              </Typography>
              <Typography variant="body1">
                This is a basic popover with simple content.
              </Typography>
            </DialogContent>
            <PopoverActions
              primaryActionButtonText="OK"
              secondaryActionButtonText="Cancel"
              onPrimaryAction={() => console.log("OK clicked")}
              onSecondaryAction={() => console.log("Cancel clicked")}
            />
          </Box>
        ),
        width: "300px",
      });
    }
  };

  const openFormPopover = () => {
    const button = document.getElementById("trigger-button");
    if (button) {
      setOpen({
        anchorEl: button,
        content: (
          <Box>
            <DialogContent dividers>
              <Typography variant="h6" gutterBottom>
                Form Popover
              </Typography>
              <Typography variant="body1" paragraph>
                This popover contains form elements and validation.
              </Typography>
            </DialogContent>
            <PopoverActions
              primaryActionButtonText="Submit"
              secondaryActionButtonText="Cancel"
              onPrimaryAction={() => console.log("Submit clicked")}
              onSecondaryAction={() => console.log("Cancel clicked")}
              isButtonValidation={true}
            />
          </Box>
        ),
        width: "400px",
      });
    }
  };

  const openDeletePopover = () => {
    const button = document.getElementById("trigger-button");
    if (button) {
      setOpen({
        anchorEl: button,
        content: (
          <Box>
            <DialogContent dividers>
              <Typography variant="h6" gutterBottom>
                Delete Confirmation
              </Typography>
              <Typography variant="body1">
                This popover includes a delete action with confirmation.
              </Typography>
            </DialogContent>
            <PopoverActions
              primaryActionButtonText="Save"
              secondaryActionButtonText="Cancel"
              onPrimaryAction={() => console.log("Save clicked")}
              onSecondaryAction={() => console.log("Cancel clicked")}
              onDeleteAction={() => console.log("Delete confirmed")}
              onDeleteConfirmationText="Are you sure you want to delete this item?"
            />
          </Box>
        ),
        width: "350px",
      });
    }
  };

  const openLoadingPopover = () => {
    const button = document.getElementById("trigger-button");
    if (button) {
      setOpen({
        anchorEl: button,
        content: (
          <Box>
            <DialogContent dividers>
              <Typography variant="h6" gutterBottom>
                Loading State
              </Typography>
              <Typography variant="body1">
                This popover shows a loading state on the primary button.
              </Typography>
            </DialogContent>
            <PopoverActions
              primaryActionButtonText="Processing..."
              secondaryActionButtonText="Cancel"
              onPrimaryAction={() => console.log("Processing...")}
              onSecondaryAction={() => console.log("Cancel clicked")}
              isLoading={true}
            />
          </Box>
        ),
        width: "300px",
      });
    }
  };

  const openWidePopover = () => {
    const button = document.getElementById("trigger-button");
    if (button) {
      setOpen({
        anchorEl: button,
        content: (
          <Box>
            <DialogContent dividers>
              <Typography variant="h6" gutterBottom>
                Wide Popover
              </Typography>
              <Typography variant="body1" paragraph>
                This is a wider popover that demonstrates how the component adapts to different widths.
                It can contain more content and still maintain proper layout.
              </Typography>
              <Typography variant="body2" color="text.secondary">
                The popover width is controlled by the width parameter in the setOpen function.
              </Typography>
            </DialogContent>
            <PopoverActions
              primaryActionButtonText="Continue"
              secondaryActionButtonText="Go Back"
              onPrimaryAction={() => console.log("Continue clicked")}
              onSecondaryAction={() => console.log("Go Back clicked")}
            />
          </Box>
        ),
        width: "600px",
      });
    }
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        Popover Provider Examples
      </Typography>
      <Typography variant="body1" paragraph>
        Click the buttons below to open different types of popovers. The popover will appear anchored to the trigger button.
      </Typography>
      <Box sx={{ display: "flex", gap: "10px", flexWrap: "wrap", mb: 2 }}>
        <Button
          id="trigger-button"
          variant="contained"
          onClick={openBasicPopover}
        >
          Basic Popover
        </Button>
        <Button
          variant="contained"
          onClick={openFormPopover}
        >
          Form Popover
        </Button>
        <Button
          variant="contained"
          onClick={openDeletePopover}
        >
          Delete Popover
        </Button>
        <Button
          variant="contained"
          onClick={openLoadingPopover}
        >
          Loading Popover
        </Button>
        <Button
          variant="contained"
          onClick={openWidePopover}
        >
          Wide Popover
        </Button>
      </Box>
      <PopoverProvider />
    </Box>
  );
};

const meta: Meta<typeof PopoverProvider> = {
  title: "Shared/Popover/PopoverProvider",
  component: PopoverProvider,
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
type Story = StoryObj<typeof PopoverProvider>;

export const InteractiveDemo: Story = {
  render: () => <PopoverProviderDemo />,
};

export const BasicPopover: Story = {
  render: () => {
    const { setOpen } = usePopover();

    React.useEffect(() => {
      const button = document.createElement("button");
      button.textContent = "Trigger Button";
      button.style.position = "absolute";
      button.style.top = "50%";
      button.style.left = "50%";
      button.style.transform = "translate(-50%, -50%)";
      button.id = "trigger-button";
      document.body.appendChild(button);

      setOpen({
        anchorEl: button,
        content: (
          <Box>
            <DialogContent dividers>
              <Typography variant="h6" gutterBottom>
                Basic Popover
              </Typography>
              <Typography variant="body1">
                This is a basic popover example.
              </Typography>
            </DialogContent>
            <PopoverActions
              primaryActionButtonText="OK"
              secondaryActionButtonText="Cancel"
              onPrimaryAction={() => console.log("OK clicked")}
              onSecondaryAction={() => console.log("Cancel clicked")}
            />
          </Box>
        ),
        width: "300px",
      });

      return () => {
        document.body.removeChild(button);
      };
    }, [setOpen]);

    return <PopoverProvider />;
  },
};

export const PopoverWithDelete: Story = {
  render: () => {
    const { setOpen } = usePopover();

    React.useEffect(() => {
      const button = document.createElement("button");
      button.textContent = "Trigger Button";
      button.style.position = "absolute";
      button.style.top = "50%";
      button.style.left = "50%";
      button.style.transform = "translate(-50%, -50%)";
      button.id = "trigger-button";
      document.body.appendChild(button);

      setOpen({
        anchorEl: button,
        content: (
          <Box>
            <DialogContent dividers>
              <Typography variant="h6" gutterBottom>
                Delete Confirmation
              </Typography>
              <Typography variant="body1">
                This popover includes delete functionality with confirmation.
              </Typography>
            </DialogContent>
            <PopoverActions
              primaryActionButtonText="Save"
              secondaryActionButtonText="Cancel"
              onPrimaryAction={() => console.log("Save clicked")}
              onSecondaryAction={() => console.log("Cancel clicked")}
              onDeleteAction={() => console.log("Delete confirmed")}
              onDeleteConfirmationText="Are you sure you want to delete this item?"
            />
          </Box>
        ),
        width: "350px",
      });

      return () => {
        document.body.removeChild(button);
      };
    }, [setOpen]);

    return <PopoverProvider />;
  },
};

export const LoadingPopover: Story = {
  render: () => {
    const { setOpen } = usePopover();

    React.useEffect(() => {
      const button = document.createElement("button");
      button.textContent = "Trigger Button";
      button.style.position = "absolute";
      button.style.top = "50%";
      button.style.left = "50%";
      button.style.transform = "translate(-50%, -50%)";
      button.id = "trigger-button";
      document.body.appendChild(button);

      setOpen({
        anchorEl: button,
        content: (
          <Box>
            <DialogContent dividers>
              <Typography variant="h6" gutterBottom>
                Loading State
              </Typography>
              <Typography variant="body1">
                This popover shows a loading state on the primary button.
              </Typography>
            </DialogContent>
            <PopoverActions
              primaryActionButtonText="Processing..."
              secondaryActionButtonText="Cancel"
              onPrimaryAction={() => console.log("Processing...")}
              onSecondaryAction={() => console.log("Cancel clicked")}
              isLoading={true}
            />
          </Box>
        ),
        width: "300px",
      });

      return () => {
        document.body.removeChild(button);
      };
    }, [setOpen]);

    return <PopoverProvider />;
  },
};
