import type { Meta, StoryObj } from "@storybook/react";
import { FormDecorator } from "../../decorators/FormDecorator";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import { Box, Typography } from "@mui/material";

const meta: Meta<typeof ModalActions> = {
  title: "Components/Modals/ModalActions",
  component: ModalActions,
  parameters: {
    layout: "centered",
  },
  decorators: [
    (Story) => (
      <FormDecorator>
        <Box
          sx={{ width: "500px", border: "1px solid #e0e0e0", borderRadius: 1 }}
        >
          <Box sx={{ padding: "20px" }}>
            <Typography variant="h6" gutterBottom>
              Modal Content
            </Typography>
            <Typography variant="body1">
              This is the modal content area. The actions will appear below.
            </Typography>
          </Box>
          <Story />
        </Box>
      </FormDecorator>
    ),
  ],
  argTypes: {
    primaryActionButtonText: {
      control: "text",
      description: "Text for the primary action button",
    },
    secondaryActionButtonText: {
      control: "text",
      description: "Text for the secondary action button",
    },
    onPrimaryAction: {
      action: "primary action",
      description: "Function called when primary button is clicked",
    },
    onSecondaryAction: {
      action: "secondary action",
      description: "Function called when secondary button is clicked",
    },
    isButtonValidation: {
      control: "boolean",
      description: "Whether to validate form before enabling primary button",
    },
    onDeleteAction: {
      action: "delete",
      description: "Function called when delete button is clicked",
    },
    onDeleteConfirmationText: {
      control: "text",
      description: "Text for delete confirmation",
    },
    isLoading: {
      control: "boolean",
      description: "Whether the primary button is in loading state",
    },
    isDeleteActionLoading: {
      control: "boolean",
      description: "Whether the delete button is in loading state",
    },
  },
};

export default meta;
type Story = StoryObj<typeof ModalActions>;

export const Default: Story = {
  args: {
    primaryActionButtonText: "Save",
    secondaryActionButtonText: "Cancel",
    isLoading: false,
  },
};

export const WithDeleteAction: Story = {
  args: {
    primaryActionButtonText: "Save",
    secondaryActionButtonText: "Cancel",
    onDeleteAction: () => console.log("Delete action triggered"),
    onDeleteConfirmationText: "Are you sure you want to delete this item?",
    isLoading: false,
    isDeleteActionLoading: false,
  },
};

export const LoadingStates: Story = {
  args: {
    primaryActionButtonText: "Saving...",
    secondaryActionButtonText: "Cancel",
    isLoading: true,
    isDeleteActionLoading: false,
  },
};

export const DeleteActionLoading: Story = {
  args: {
    primaryActionButtonText: "Save",
    secondaryActionButtonText: "Cancel",
    onDeleteAction: () => console.log("Delete action triggered"),
    onDeleteConfirmationText: "Are you sure you want to delete this item?",
    isLoading: false,
    isDeleteActionLoading: true,
  },
};

export const CustomButtonTexts: Story = {
  args: {
    primaryActionButtonText: "Confirm",
    secondaryActionButtonText: "Back",
    isLoading: false,
  },
};
