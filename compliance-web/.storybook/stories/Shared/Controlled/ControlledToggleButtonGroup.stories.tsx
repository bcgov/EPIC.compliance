import type { Meta, StoryObj } from "@storybook/react";
import { FormDecorator } from "../../../decorators/FormDecorator";
import ControlledToggleButtonGroup from "@/components/Shared/Controlled/ControlledToggleButtonGroup";

const meta: Meta<typeof ControlledToggleButtonGroup> = {
  title: "Shared/Controlled/ControlledToggleButtonGroup",
  component: ControlledToggleButtonGroup,
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
    options: {
      control: "object",
      description: "Array of toggle button options",
    },
    disabled: {
      control: "boolean",
      description: "Whether the toggle group is disabled",
    },
    exclusive: {
      control: "boolean",
      description: "Whether only one option can be selected",
    },
    size: {
      control: "select",
      options: ["small", "medium", "large"],
      description: "Size of the toggle buttons",
    },
    color: {
      control: "select",
      options: ["standard", "primary", "secondary"],
      description: "Color of the toggle buttons",
    },
  },
};

export default meta;
type Story = StoryObj<typeof ControlledToggleButtonGroup>;

const sampleOptions = [
  { id: "option1", name: "Option 1" },
  { id: "option2", name: "Option 2" },
  { id: "option3", name: "Option 3" },
];

export const Default: Story = {
  args: {
    name: "toggleField",
    options: sampleOptions,
  },
};

export const Multiple: Story = {
  args: {
    name: "toggleField",
    options: sampleOptions,
    exclusive: false,
  },
};

export const Disabled: Story = {
  args: {
    name: "toggleField",
    options: sampleOptions,
    disabled: true,
  },
};

export const Small: Story = {
  args: {
    name: "toggleField",
    options: sampleOptions,
    size: "small",
  },
};

export const Large: Story = {
  args: {
    name: "toggleField",
    options: sampleOptions,
    size: "large",
  },
};

export const PrimaryColor: Story = {
  args: {
    name: "toggleField",
    options: sampleOptions,
    color: "primary",
  },
};

export const WithPreSelected: Story = {
  decorators: [
    (Story) => (
      <FormDecorator defaultFormValues={{ toggleField: "option2" }}>
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    name: "toggleField",
    options: sampleOptions,
  },
};

export const WithMultiplePreSelected: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        defaultFormValues={{ toggleField: ["option1", "option3"] }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    name: "toggleField",
    options: sampleOptions,
    exclusive: false,
  },
};
