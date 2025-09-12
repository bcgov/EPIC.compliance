import type { Meta, StoryObj } from "@storybook/react";
import { FormDecorator } from "../../../decorators/FormDecorator";
import ControlledDateField from "@/components/Shared/Controlled/ControlledDateField";
import * as yup from "yup";

const meta: Meta<typeof ControlledDateField> = {
  title: "Shared/Controlled/ControlledDateField",
  component: ControlledDateField,
  parameters: {
    layout: "centered",
  },
  decorators: [
    (Story) => (
      <FormDecorator>
        <Story />
      </FormDecorator>
    ),
  ],
  argTypes: {
    name: {
      control: "text",
      description: "Form field name",
    },
    label: {
      control: "text",
      description: "Field label",
    },
    isRequired: {
      control: "boolean",
      description: "Whether the field is required",
    },
    disabled: {
      control: "boolean",
      description: "Whether the field is disabled",
    },
    views: {
      control: "object",
      description: "Available views for the date picker",
    },
    openTo: {
      control: "select",
      options: ["day", "month", "year"],
      description: "Initial view to open",
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    name: "dateField",
    label: "Select Date",
  },
};

export const Required: Story = {
  args: {
    name: "dateField",
    label: "Required Date",
    isRequired: true,
  },
};

export const Disabled: Story = {
  args: {
    name: "dateField",
    label: "Disabled Date Field",
    disabled: true,
  },
};

export const YearOnly: Story = {
  args: {
    name: "dateField",
    label: "Select Year",
    views: ["year"],
    openTo: "year",
  },
};

export const MonthAndYear: Story = {
  args: {
    name: "dateField",
    label: "Select Month and Year",
    views: ["month", "year"],
    openTo: "month",
  },
};

export const WithPreSelectedDate: Story = {
  decorators: [
    (Story) => (
      <FormDecorator defaultFormValues={{ dateField: new Date("2024-01-15") }}>
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    name: "dateField",
    label: "Pre-selected Date",
  },
};

export const WithValidation: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        schema={yup.object({
          dateField: yup
            .date()
            .required("Date is required")
            .min(new Date(), "Date must be in the future"),
        })}
        defaultFormValues={{ dateField: null }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    name: "dateField",
    label: "Future Date Required",
    isRequired: true,
  },
};
