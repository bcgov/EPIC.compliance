import type { Meta, StoryObj } from '@storybook/react';
import { FormDecorator } from '../../../decorators/FormDecorator';
import ControlledDateRangePicker from '@/components/Shared/Controlled/ControlledDateRangePicker';
import * as yup from 'yup';

const meta: Meta<typeof ControlledDateRangePicker> = {
  title: 'Shared/Controlled/ControlledDateRangePicker',
  component: ControlledDateRangePicker,
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
    placeHolder: {
      control: 'text',
      description: 'Placeholder text',
    },
  },
};

export default meta;
type Story = StoryObj<typeof ControlledDateRangePicker>;

export const Default: Story = {
  args: {
    name: 'dateRangeField',
    label: 'Select Date Range',
  },
};

export const WithPlaceholder: Story = {
  args: {
    name: 'dateRangeField',
    label: 'Date Range with Custom Placeholder',
    placeHolder: 'Choose your date range...',
  },
};

export const WithPreSelectedRange: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        defaultFormValues={{ 
          dateRangeField: {
            startDate: new Date('2024-01-01'),
            endDate: new Date('2024-01-31')
          }
        }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    name: 'dateRangeField',
    label: 'Pre-selected Range',
  },
};

export const WithValidation: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        schema={yup.object({
          dateRangeField: yup.object({
            startDate: yup.date().required('Start date is required'),
            endDate: yup.date().required('End date is required'),
          }).test('date-range', 'End date must be after start date', function(value) {
            if (!value?.startDate || !value?.endDate) return true;
            return value.endDate > value.startDate;
          }),
        })}
        defaultFormValues={{ dateRangeField: { startDate: null, endDate: null } }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    name: 'dateRangeField',
    label: 'Validated Date Range',
  },
};
