import type { Meta, StoryObj } from '@storybook/react';
import { FormDecorator } from '../../decorators/FormDecorator';
import ControlledSwitch from '@/components/Shared/Controlled/ControlledSwitch';

const meta: Meta<typeof ControlledSwitch> = {
  title: 'Components/Controlled/ControlledSwitch',
  component: ControlledSwitch,
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
      description: 'Switch label',
    },
    isRequired: {
      control: 'boolean',
      description: 'Whether the field is required',
    },
    sx: {
      control: 'object',
      description: 'Custom styles',
    },
  },
};

export default meta;
type Story = StoryObj<typeof ControlledSwitch>;

export const Default: Story = {
  args: {
    name: 'switchField',
    label: 'Toggle Switch',
  },
};

export const Required: Story = {
  args: {
    name: 'switchField',
    label: 'Required Switch',
    isRequired: true,
  },
};

export const WithCustomStyles: Story = {
  args: {
    name: 'switchField',
    label: 'Switch with Custom Styles',
    sx: { 
      '& .MuiSwitch-switchBase': { 
        color: 'primary.main' 
      } 
    },
  },
};

export const Checked: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        defaultFormValues={{ switchField: true }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    name: 'switchField',
    label: 'Pre-checked Switch',
  },
};

export const WithCustomSx: Story = {
  args: {
    name: 'switchField',
    label: 'Custom Styled Switch',
    sx: {
      '& .MuiFormControlLabel-label': {
        color: 'primary.main',
        fontWeight: 'bold',
      },
    },
  },
};
