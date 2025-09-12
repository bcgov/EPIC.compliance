import type { Meta, StoryObj } from '@storybook/react';
import { FormDecorator } from '../../../decorators/FormDecorator';
import DrawerActionBarTop from '@/components/Shared/Drawer/DrawerActionBarTop';
import * as yup from 'yup';

const meta: Meta<typeof DrawerActionBarTop> = {
  title: 'Shared/Drawer/DrawerActionBarTop',
  component: DrawerActionBarTop,
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
    isShowActionBar: {
      control: 'boolean',
      description: 'Whether to show the action bar',
    },
    isLoading: {
      control: 'boolean',
      description: 'Whether the submit button is in loading state',
    },
  },
};

export default meta;
type Story = StoryObj<typeof DrawerActionBarTop>;

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

export const Loading: Story = {
  args: {
    isShowActionBar: true,
    isLoading: true,
  },
};

export const WithValidForm: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        schema={yup.object({
          textField: yup.string().required('This field is required'),
        })}
        defaultFormValues={{ textField: 'Valid input' }}
      >
        <Story />
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
          textField: yup.string().required('This field is required'),
        })}
        defaultFormValues={{ textField: '' }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    isShowActionBar: true,
    isLoading: false,
  },
};
