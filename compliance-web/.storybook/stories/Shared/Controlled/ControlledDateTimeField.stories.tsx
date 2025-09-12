import type { Meta, StoryObj } from '@storybook/react';
import { FormDecorator } from '../../../decorators/FormDecorator';
import ControlledDateTimeField from '@/components/Shared/Controlled/ControlledDateTimeField';
import * as yup from 'yup';

const meta: Meta<typeof ControlledDateTimeField> = {
  title: 'Shared/Controlled/ControlledDateTimeField',
  component: ControlledDateTimeField,
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
    isRequired: {
      control: 'boolean',
      description: 'Whether the field is required',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the field is disabled',
    },
    views: {
      control: 'object',
      description: 'Available views for the date time picker',
    },
    openTo: {
      control: 'select',
      options: ['day', 'month', 'year'],
      description: 'Initial view to open',
    },
    format: {
      control: 'text',
      description: 'Display format for the date time',
    },
  },
};

export default meta;
type Story = StoryObj<typeof ControlledDateTimeField>;

export const Default: Story = {
  args: {
    name: 'dateTimeField',
    label: 'Select Date and Time',
  },
};

export const Required: Story = {
  args: {
    name: 'dateTimeField',
    label: 'Required Date and Time',
    isRequired: true,
  },
};

export const Disabled: Story = {
  args: {
    name: 'dateTimeField',
    label: 'Disabled Date Time Field',
    disabled: true,
  },
};

export const DateOnly: Story = {
  args: {
    name: 'dateTimeField',
    label: 'Date Only',
    views: ['day', 'month', 'year'],
    openTo: 'day',
  },
};

export const YearOnly: Story = {
  args: {
    name: 'dateTimeField',
    label: 'Year Only',
    views: ['year'],
    openTo: 'year',
  },
};

export const WithCustomFormat: Story = {
  args: {
    name: 'dateTimeField',
    label: 'Custom Format',
    format: 'DD/MM/YYYY HH:mm',
  },
};

export const WithPreSelectedDateTime: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        defaultFormValues={{ dateTimeField: new Date('2024-01-15T14:30:00') }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    name: 'dateTimeField',
    label: 'Pre-selected Date and Time',
  },
};

export const WithValidation: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        schema={yup.object({
          dateTimeField: yup.date().required('Date and time is required').min(new Date(), 'Date must be in the future'),
        })}
        defaultFormValues={{ dateTimeField: null }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    name: 'dateTimeField',
    label: 'Future Date and Time Required',
    isRequired: true,
  },
};
