import type { Meta, StoryObj } from "@storybook/react";
import React from "react";
import { Box, Button, Typography, DialogContent } from "@mui/material";
import PopoverProvider from "@/components/Shared/Popover/PopoverProvider";
import PopoverActions from "@/components/Shared/Popover/PopoverActions";
import { usePopover } from "@/store/popoverStore";
import { FormDecorator } from "../../../decorators/FormDecorator";
import * as yup from "yup";

// Complete popover content component
const CompletePopoverContent = ({
  title,
  showDelete = false,
  isLoading = false,
  isButtonValidation = false,
}: {
  title: string;
  showDelete?: boolean;
  isLoading?: boolean;
  isButtonValidation?: boolean;
}) => {
  return (
    <Box>
      <DialogContent dividers>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body1" paragraph>
          This is a complete popover example that combines PopoverProvider and PopoverActions components.
        </Typography>
        <Typography variant="body2" color="text.secondary">
          The popover can contain various content types and action configurations.
        </Typography>
      </DialogContent>
      <PopoverActions
        primaryActionButtonText="Save Changes"
        secondaryActionButtonText="Cancel"
        onPrimaryAction={() => console.log("Save action triggered")}
        onSecondaryAction={() => console.log("Cancel action triggered")}
        onDeleteAction={
          showDelete ? () => console.log("Delete action triggered") : undefined
        }
        onDeleteConfirmationText="Are you sure you want to delete this record? This action cannot be undone."
        isButtonValidation={isButtonValidation}
        isLoading={isLoading}
      />
    </Box>
  );
};

// Demo component to show different popover states
const PopoverDemo = () => {
  const { setOpen } = usePopover();

  const openPopover = (content: React.ReactNode, width?: string) => {
    const button = document.getElementById("trigger-button");
    if (button) {
      setOpen({ anchorEl: button, content, width });
    }
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        Complete Popover Examples
      </Typography>
      <Typography variant="body1" paragraph>
        These examples demonstrate how PopoverProvider and PopoverActions work together.
      </Typography>
      <Box sx={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        <Button
          id="trigger-button"
          variant="contained"
          onClick={() =>
            openPopover(<CompletePopoverContent title="Basic Popover" />, "400px")
          }
        >
          Basic Popover
        </Button>
        <Button
          variant="contained"
          onClick={() =>
            openPopover(
              <CompletePopoverContent
                title="Popover with Delete"
                showDelete={true}
              />,
              "400px"
            )
          }
        >
          Popover with Delete
        </Button>
        <Button
          variant="contained"
          onClick={() =>
            openPopover(
              <CompletePopoverContent title="Loading Popover" isLoading={true} />,
              "400px"
            )
          }
        >
          Loading Popover
        </Button>
        <Button
          variant="contained"
          onClick={() =>
            openPopover(
              <CompletePopoverContent
                title="Wide Popover with All Features"
                showDelete={true}
                isLoading={false}
              />,
              "600px"
            )
          }
        >
          Wide Popover
        </Button>
      </Box>
      <PopoverProvider />
    </Box>
  );
};

const meta: Meta<typeof PopoverProvider> = {
  title: "Shared/Popover/Complete Example",
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
  render: () => <PopoverDemo />,
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
        content: <CompletePopoverContent title="Basic Popover Example" />,
        width: "400px",
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
          <CompletePopoverContent
            title="Popover with Delete Action"
            showDelete={true}
          />
        ),
        width: "400px",
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
          <CompletePopoverContent title="Loading Popover" isLoading={true} />
        ),
        width: "400px",
      });

      return () => {
        document.body.removeChild(button);
      };
    }, [setOpen]);

    return <PopoverProvider />;
  },
};

export const WidePopover: Story = {
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
          <CompletePopoverContent
            title="Wide Popover with All Features"
            showDelete={true}
            isLoading={false}
          />
        ),
        width: "600px",
      });

      return () => {
        document.body.removeChild(button);
      };
    }, [setOpen]);

    return <PopoverProvider />;
  },
};

export const WithFormValidation: Story = {
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
          <FormDecorator
            schema={yup.object({
              name: yup.string().required("Name is required"),
              email: yup
                .string()
                .email("Invalid email")
                .required("Email is required"),
              message: yup.string().required("Message is required"),
            })}
            defaultFormValues={{ name: "", email: "", message: "" }}
          >
            <Box>
              <DialogContent dividers>
                <Typography variant="h6" gutterBottom>
                  Form Validation Popover
                </Typography>
                <Typography variant="body1" paragraph>
                  This popover has form validation. The Save button will be disabled
                  until all fields are valid.
                </Typography>
              </DialogContent>
              <PopoverActions
                primaryActionButtonText="Save"
                secondaryActionButtonText="Cancel"
                onPrimaryAction={() => console.log("Save action triggered")}
                onSecondaryAction={() => console.log("Cancel action triggered")}
                isButtonValidation={true}
                isLoading={false}
              />
            </Box>
          </FormDecorator>
        ),
        width: "500px",
      });

      return () => {
        document.body.removeChild(button);
      };
    }, [setOpen]);

    return <PopoverProvider />;
  },
};
