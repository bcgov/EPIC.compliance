import type { Meta, StoryObj } from '@storybook/react';
import { FormDecorator } from '../../decorators/FormDecorator';
import DrawerTitleBar from '@/components/Shared/Drawer/DrawerTitleBar';
import { Chip, Box } from '@mui/material';
import * as yup from 'yup';

const meta: Meta<typeof DrawerTitleBar> = {
  title: 'Components/Drawer/DrawerTitleBar',
  component: DrawerTitleBar,
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
    title: {
      control: 'text',
      description: 'Title text displayed in the drawer header',
    },
    isFormDirtyCheck: {
      control: 'boolean',
      description: 'Whether to check for form dirty state before closing',
    },
    isDirtyManual: {
      control: 'boolean',
      description: 'Manual dirty state override',
    },
    customCloseFn: {
      action: 'close',
      description: 'Custom close function',
    },
    statusFlag: {
      control: false,
      description: 'React node to display as status flag',
    },
  },
};

export default meta;
type Story = StoryObj<typeof DrawerTitleBar>;

export const Default: Story = {
  args: {
    title: 'Drawer Title',
  },
};

export const WithLongTitle: Story = {
  args: {
    title: 'This is a very long drawer title that might wrap to multiple lines',
  },
};

export const WithFormDirtyCheck: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        schema={yup.object({
          textField: yup.string().required('This field is required'),
        })}
        defaultFormValues={{ textField: 'Modified value' }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    title: 'Form with Dirty Check',
    isFormDirtyCheck: true,
  },
};

export const WithManualDirtyState: Story = {
  args: {
    title: 'Manual Dirty State',
    isDirtyManual: true,
    isFormDirtyCheck: true,
  },
};

export const WithCustomCloseFunction: Story = {
  args: {
    title: 'Custom Close Handler',
    customCloseFn: () => console.log('Custom close function called'),
  },
};

export const WithStatusFlag: Story = {
  args: {
    title: 'Record Details',
    statusFlag: (
      <Chip 
        label="Active" 
        color="success" 
        size="small" 
        sx={{ ml: 1 }}
      />
    ),
  },
};

export const WithMultipleStatusFlags: Story = {
  args: {
    title: 'Project Status',
    statusFlag: (
      <Box sx={{ display: 'flex', gap: 1, ml: 1 }}>
        <Chip label="Draft" color="warning" size="small" />
        <Chip label="Pending Review" color="info" size="small" />
      </Box>
    ),
  },
};

export const WithFormDirtyCheckAndStatus: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        schema={yup.object({
          textField: yup.string().required('This field is required'),
        })}
        defaultFormValues={{ textField: 'Original value' }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    title: 'Edit Record',
    isFormDirtyCheck: true,
    statusFlag: (
      <Chip 
        label="Modified" 
        color="warning" 
        size="small" 
        sx={{ ml: 1 }}
      />
    ),
  },
};

export const WithCustomCloseAndStatus: Story = {
  args: {
    title: 'Advanced Configuration',
    customCloseFn: () => console.log('Custom close function called'),
    statusFlag: (
      <Chip 
        label="In Progress" 
        color="primary" 
        size="small" 
        sx={{ ml: 1 }}
      />
    ),
  },
};

export const CompleteExample: Story = {
  decorators: [
    (Story) => (
      <FormDecorator
        schema={yup.object({
          textField: yup.string().required('This field is required'),
          emailField: yup.string().email('Invalid email').required('Email is required'),
        })}
        defaultFormValues={{ textField: 'Modified value', emailField: 'user@example.com' }}
      >
        <Story />
      </FormDecorator>
    ),
  ],
  args: {
    title: 'Edit User Profile',
    isFormDirtyCheck: true,
    customCloseFn: () => console.log('Custom close function called'),
    statusFlag: (
      <Box sx={{ display: 'flex', gap: 1, ml: 1 }}>
        <Chip label="Modified" color="warning" size="small" />
        <Chip label="Auto-save" color="info" size="small" />
      </Box>
    ),
  },
};
