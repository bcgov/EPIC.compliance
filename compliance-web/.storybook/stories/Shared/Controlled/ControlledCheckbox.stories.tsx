import type { Meta, StoryObj } from "@storybook/react";
import { FormDecorator } from "../../../decorators/FormDecorator";
import ControlledCheckbox from "@/components/Shared/Controlled/ControlledCheckbox";

const meta: Meta<typeof ControlledCheckbox> = {
  title: "Shared/Controlled/ControlledCheckbox",
  component: ControlledCheckbox,
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
      description: "Checkbox label",
    },
    isRequired: {
      control: "boolean",
      description: "Whether the field is required",
    },
    fontSize: {
      control: "select",
      options: ["small", "medium"],
      description: "Font size of the checkbox label",
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    name: "checkboxField",
    label: "Checkbox Option",
  },
};

export const Required: Story = {
  args: {
    name: "checkboxField",
    label: "Required Checkbox",
    isRequired: true,
  },
};

export const SmallFont: Story = {
  args: {
    name: "checkboxField",
    label: "Small Font Checkbox",
    fontSize: "small",
  },
};

export const Checked: Story = {
  decorators: [
    (Story) => (
      <FormDecorator defaultFormValues={{ checkboxField: true }}>
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    name: "checkboxField",
    label: "Pre-checked Checkbox",
  },
};

export const RequiredSmallFont: Story = {
  args: {
    name: "checkboxField",
    label: "Required Small Font Checkbox",
    isRequired: true,
    fontSize: "small",
  },
};
