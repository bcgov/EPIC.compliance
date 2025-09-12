import type { Meta, StoryObj } from "@storybook/react";
import { Grid, Box, Chip } from "@mui/material";
import GridLabelValuePair from "../../../src/components/Shared/GridLabelValuePair";

const meta: Meta<typeof GridLabelValuePair> = {
  title: "Shared/GridLabelValuePair",
  component: GridLabelValuePair,
  parameters: {
    layout: "padded",
  },
  tags: ["autodocs"],
  argTypes: {
    label: {
      control: "text",
      description: "Label text",
    },
    value: {
      control: "text",
      description: "Value content",
    },
    gridProps: {
      control: "object",
      description: "Grid item properties",
    },
    isBold: {
      control: "boolean",
      description: "Whether the label is bold",
    },
    hideTooltip: {
      control: "boolean",
      description: "Whether to hide the tooltip",
    },
    multiline: {
      control: "boolean",
      description: "Whether the value supports multiline text",
    },
    isChip: {
      control: "boolean",
      description: "Whether to display the value as a chip",
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    label: "Case File Number",
    value: "CF-2024-001",
  },
};

export const BoldLabel: Story = {
  args: {
    label: "Status",
    value: "Active",
    isBold: true,
  },
};

export const WithChip: Story = {
  args: {
    label: "Priority",
    value: "High",
    isChip: true,
  },
};

export const MultilineValue: Story = {
  args: {
    label: "Description",
    value:
      "This is a very long description that spans multiple lines and should be displayed properly with word wrapping enabled.",
    multiline: true,
  },
};

export const LongValue: Story = {
  args: {
    label: "Project Name",
    value:
      "Environmental Impact Assessment for Northern Pipeline Project Phase 2",
  },
};

export const WithTooltip: Story = {
  args: {
    label: "Full Name",
    value: "Dr. Sarah Johnson-Smith",
    hideTooltip: false,
  },
};

export const WithoutTooltip: Story = {
  args: {
    label: "ID",
    value: "12345",
    hideTooltip: true,
  },
};

export const CustomGridSize: Story = {
  args: {
    label: "Email",
    value: "john.doe@example.com",
    gridProps: { xs: 6 },
  },
};

export const MultiplePairs: Story = {
  render: () => (
    <Grid container spacing={2}>
      <GridLabelValuePair
        label="Case File Number"
        value="CF-2024-001"
        gridProps={{ xs: 12 }}
      />
      <GridLabelValuePair
        label="Status"
        value="Active"
        isBold={true}
        gridProps={{ xs: 12 }}
      />
      <GridLabelValuePair
        label="Priority"
        value="High"
        isChip={true}
        gridProps={{ xs: 12 }}
      />
      <GridLabelValuePair
        label="Created Date"
        value="2024-01-15"
        gridProps={{ xs: 12 }}
      />
      <GridLabelValuePair
        label="Description"
        value="Environmental compliance case for industrial facility in Northern BC"
        multiline={true}
        gridProps={{ xs: 12 }}
      />
    </Grid>
  ),
};

export const WithComplexValue: Story = {
  args: {
    label: "Actions",
    value: (
      <Box sx={{ display: "flex", gap: 1 }}>
        <Chip label="Edit" size="small" color="primary" />
        <Chip label="View" size="small" color="secondary" />
        <Chip label="Delete" size="small" color="error" />
      </Box>
    ),
  },
};
