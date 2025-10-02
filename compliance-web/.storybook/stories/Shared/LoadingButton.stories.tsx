import type { Meta, StoryObj } from '@storybook/react';
import LoadingButton from '@/components/Shared/LoadingButton';

const meta: Meta<typeof LoadingButton> = {
  title: 'Shared/LoadingButton',
  component: LoadingButton,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    isLoading: {
      control: 'boolean',
      description: 'Whether the button is in loading state',
    },
    loadingText: {
      control: 'text',
      description: 'Text to display while loading',
    },
    variant: {
      control: 'select',
      options: ['text', 'outlined', 'contained'],
      description: 'Button variant',
    },
    color: {
      control: 'select',
      options: ['inherit', 'primary', 'secondary', 'success', 'error', 'info', 'warning'],
      description: 'Button color',
    },
    size: {
      control: 'select',
      options: ['small', 'medium', 'large'],
      description: 'Button size',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    children: 'Click me',
    variant: 'contained',
    color: 'primary',
  },
};

export const Loading: Story = {
  args: {
    children: 'Save Changes',
    isLoading: true,
    loadingText: 'Saving...',
    variant: 'contained',
    color: 'primary',
  },
};

export const Outlined: Story = {
  args: {
    children: 'Cancel',
    variant: 'outlined',
    color: 'error',
  },
};

export const Text: Story = {
  args: {
    children: 'Edit',
    variant: 'text',
    color: 'primary',
  },
};

export const LoadingWithCustomText: Story = {
  args: {
    children: 'Submit Form',
    isLoading: true,
    loadingText: 'Processing...',
    variant: 'contained',
    color: 'success',
  },
};

export const Disabled: Story = {
  args: {
    children: 'Disabled Button',
    disabled: true,
    variant: 'contained',
    color: 'primary',
  },
};
