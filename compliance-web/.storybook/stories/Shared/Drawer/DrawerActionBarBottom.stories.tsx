import type { Meta, StoryObj } from "@storybook/react";
import { FormDecorator } from "../../../decorators/FormDecorator";
import DrawerActionBarBottom from "@/components/Shared/Drawer/DrawerActionBarBottom";
import * as yup from "yup";

const meta: Meta<typeof DrawerActionBarBottom> = {
  title: "Shared/Drawer/DrawerActionBarBottom",
  component: DrawerActionBarBottom,
  parameters: {
    layout: "centered",
  },
  decorators: [
    (Story) => (
      <FormDecorator>
        <div style={{ width: "600px" }}>
          <Story />
        </div>
      </FormDecorator>
    ),
  ],
  argTypes: {
    isShowActionBar: {
      control: "boolean",
      description: "Whether to show the action bar",
    },
    onDeleteAction: {
      action: "delete",
      description: "Function called when delete button is clicked",
    },
    onDeleteTitle: {
      control: "text",
      description: "Title for the delete confirmation modal",
    },
    onDeleteDescription: {
      control: "text",
      description: "Description for the delete confirmation modal",
    },
    isDirtyManual: {
      control: "boolean",
      description: "Manual dirty state override",
    },
    customCancelFn: {
      action: "cancel",
      description: "Custom cancel function",
    },
    isLoading: {
      control: "boolean",
      description: "Whether the save button is in loading state",
    },
  },
};

export default meta;
type Story = StoryObj<typeof DrawerActionBarBottom>;

export const Default: Story = {
  args: {
    isShowActionBar: true,
    isLoading: false,
  },
};

export const Hidden: Story = {
  args: {
    isShowActionBar: false,
    isLoading: false,
  },
};

export const WithDeleteAction: Story = {
  args: {
    isShowActionBar: true,
    onDeleteAction: () => console.log("Delete action triggered"),
    onDeleteTitle: "Delete Item",
    onDeleteDescription:
      "Are you sure you want to delete this item? This action cannot be undone.",
    isLoading: false,
  },
};

export const Loading: Story = {
  args: {
    isShowActionBar: true,
    isLoading: true,
  },
};

export const WithCustomDeleteText: Story = {
  args: {
    isShowActionBar: true,
    onDeleteAction: () => console.log("Delete action triggered"),
    onDeleteTitle: "Remove Record",
    onDeleteDescription:
      "This will permanently remove the record from the system.",
    isLoading: false,
  },
};

export const WithManualDirtyState: Story = {
  args: {
    isShowActionBar: true,
    isDirtyManual: true,
    isLoading: false,
  },
};

export const WithCustomCancelFunction: Story = {
  args: {
    isShowActionBar: true,
    customCancelFn: () => console.log("Custom cancel function called"),
    isLoading: false,
  },
};

export const WithValidForm: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        schema={yup.object({
          textField: yup.string().required("This field is required"),
        })}
        defaultFormValues={{ textField: "Valid input" }}
      >
        <div style={{ padding: "20px", width: "600px" }}>
          <Story />
        </div>
      </FormDecorator>
    ),
  ],
  args: {
    isShowActionBar: true,
    isLoading: false,
  },
};

export const WithInvalidForm: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        schema={yup.object({
          textField: yup.string().required("This field is required"),
        })}
        defaultFormValues={{ textField: "" }}
      >
        <div style={{ width: "600px" }}>
          <Story />
        </div>
      </FormDecorator>
    ),
  ],
  args: {
    isShowActionBar: true,
    isLoading: false,
  },
};

export const WithDirtyForm: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        schema={yup.object({
          textField: yup.string().required("This field is required"),
        })}
        defaultFormValues={{ textField: "Original value" }}
      >
        <div style={{ width: "600px" }}>
          <Story />
        </div>
      </FormDecorator>
    ),
  ],
  args: {
    isShowActionBar: true,
    isLoading: false,
  },
};

export const CompleteExample: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        schema={yup.object({
          textField: yup.string().required("This field is required"),
          emailField: yup
            .string()
            .email("Invalid email")
            .required("Email is required"),
        })}
        defaultFormValues={{
          textField: "Modified value",
          emailField: "user@example.com",
        }}
      >
        <div style={{ width: "600px" }}>
          <Story />
        </div>
      </FormDecorator>
    ),
  ],
  args: {
    isShowActionBar: true,
    onDeleteAction: () => console.log("Delete action triggered"),
    onDeleteTitle: "Delete Record",
    onDeleteDescription: "Are you sure you want to delete this record?",
    customCancelFn: () => console.log("Custom cancel function called"),
    isLoading: false,
  },
};
