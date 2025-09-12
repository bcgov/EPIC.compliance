import type { Meta, StoryObj } from "@storybook/react";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import { Box, Typography } from "@mui/material";

const meta: Meta<typeof ModalTitleBar> = {
  title: "Shared/Modals/ModalTitleBar",
  component: ModalTitleBar,
  parameters: {
    layout: "centered",
  },
  decorators: [
    (Story) => (
      <Box sx={{ width: "500px", border: "1px solid #e0e0e0", borderRadius: 1 }}>
        <Story />
        <Box sx={{ padding: "20px" }}>
          <Typography variant="body1">
            This is the modal content area below the title bar.
          </Typography>
        </Box>
      </Box>
    ),
  ],
  argTypes: {
    title: {
      control: "text",
      description: "Title text to display in the modal header",
    },
    onClose: {
      action: "close",
      description: "Function called when close button is clicked",
    },
    titleVariant: {
      control: "select",
      options: ["h5", "h6"],
      description: "Typography variant for the title",
    },
  },
};

export default meta;
type Story = StoryObj<typeof ModalTitleBar>;

export const Default: Story = {
  args: {
    title: "Modal Title",
    titleVariant: "h5",
  },
};

export const WithH6Variant: Story = {
  args: {
    title: "Smaller Modal Title",
    titleVariant: "h6",
  },
};

export const LongTitle: Story = {
  args: {
    title: "This is a very long modal title that should wrap properly and not overflow",
    titleVariant: "h5",
  },
};

export const ShortTitle: Story = {
  args: {
    title: "Short",
    titleVariant: "h5",
  },
};

export const WithCustomCloseAction: Story = {
  args: {
    title: "Modal with Custom Close",
    titleVariant: "h5",
    onClose: () => console.log("Custom close action triggered"),
  },
};

export const SpecialCharacters: Story = {
  args: {
    title: "Modal Title with Special Characters: @#$%^&*()",
    titleVariant: "h5",
  },
};

export const WithNumbers: Story = {
  args: {
    title: "Modal #123 - Version 2.1.0",
    titleVariant: "h5",
  },
};

export const EmptyTitle: Story = {
  args: {
    title: "",
    titleVariant: "h5",
  },
};

export const WithEmojis: Story = {
  args: {
    title: "🚀 Modal Title with Emojis ✨",
    titleVariant: "h5",
  },
};

export const CompleteExample: Story = {
  decorators: [
    (Story) => (
      <Box sx={{ width: "600px", border: "1px solid #e0e0e0", borderRadius: 1 }}>
        <Story />
        <Box sx={{ padding: "20px" }}>
          <Typography variant="h6" gutterBottom>
            Complete Modal Example
          </Typography>
          <Typography variant="body1" paragraph>
            This example shows how the ModalTitleBar integrates with other modal components.
            The title bar provides a consistent header with close functionality.
          </Typography>
          <Box sx={{ display: "flex", gap: 2, mt: 2 }}>
            <button
              style={{
                padding: "8px 16px",
                backgroundColor: "#1976d2",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Action Button
            </button>
            <button
              style={{
                padding: "8px 16px",
                backgroundColor: "#757575",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Secondary Action
            </button>
          </Box>
        </Box>
      </Box>
    ),
  ],
  args: {
    title: "Complete Modal Example",
    titleVariant: "h5",
    onClose: () => console.log("Modal closed"),
  },
};
