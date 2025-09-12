import type { Meta, StoryObj } from '@storybook/react';
import { FormDecorator } from '../../../decorators/FormDecorator';
import ControlledTextField from '@/components/Shared/Controlled/ControlledTextField';
import * as yup from 'yup';

const meta: Meta<typeof ControlledTextField> = {
  title: 'Shared/Controlled/ControlledTextField',
  component: ControlledTextField,
  parameters: {
    layout: 'centered',
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
      control: 'text',
      description: 'Form field name',
    },
    label: {
      control: 'text',
      description: 'Field label',
    },
    placeholder: {
      control: 'text',
      description: 'Field placeholder',
    },
    isRequired: {
      control: 'boolean',
      description: 'Whether the field is required',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the field is disabled',
    },
    multiline: {
      control: 'boolean',
      description: 'Whether the field is multiline',
    },
    rows: {
      control: 'number',
      description: 'Number of rows for multiline field',
    },
    maxLength: {
      control: 'number',
      description: 'Maximum character length',
    },
    mask: {
      control: 'text',
      description: 'Input mask pattern',
    },
  },
};

export default meta;
type Story = StoryObj<typeof ControlledTextField>;

export const Default: Story = {
  args: {
    name: 'textField',
    label: 'Text Field',
    placeholder: 'Enter text...',
  },
};

export const Required: Story = {
  args: {
    name: 'textField',
    label: 'Required Field',
    placeholder: 'This field is required',
    isRequired: true,
  },
};

export const Disabled: Story = {
  args: {
    name: 'textField',
    label: 'Disabled Field',
    placeholder: 'This field is disabled',
    disabled: true,
  },
};

export const Multiline: Story = {
  args: {
    name: 'textField',
    label: 'Multiline Field',
    placeholder: 'Enter multiple lines of text...',
    multiline: true,
    rows: 4,
  },
};

export const WithMaxLength: Story = {
  args: {
    name: 'textField',
    label: 'Field with Max Length',
    placeholder: 'Max 50 characters',
    maxLength: 50,
  },
};

export const WithMask: Story = {
  args: {
    name: 'textField',
    label: 'Phone Number',
    placeholder: '(000) 000-0000',
    mask: '(000) 000-0000',
  },
};

export const WithValidation: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        schema={yup.object({
          textField: yup.string().required('This field is required').min(3, 'Must be at least 3 characters'),
        })}
        defaultFormValues={{ textField: '' }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    name: 'textField',
    label: 'Field with Validation',
    placeholder: 'Enter at least 3 characters',
    isRequired: true,
  },
};

export const WithError: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        schema={yup.object({
          textField: yup.string().required('This field is required'),
        })}
        defaultFormValues={{ textField: '' }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    name: 'textField',
    label: 'Field with Error',
    placeholder: 'This will show an error',
    isRequired: true,
  },
};
