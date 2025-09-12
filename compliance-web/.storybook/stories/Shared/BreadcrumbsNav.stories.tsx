import type { Meta, StoryObj } from '@storybook/react';
import BreadcrumbsNav from '../../../src/components/Shared/BreadcrumbsNav';
import { RouterDecorator } from '../../decorators/RouterDecorator';

const meta: Meta<typeof BreadcrumbsNav> = {
  title: 'Shared/BreadcrumbsNav',
  component: BreadcrumbsNav,
  parameters: {
    layout: 'padded',
  },
  decorators: [RouterDecorator],
  tags: ['autodocs'],
  argTypes: {
    items: {
      control: 'object',
      description: 'Array of breadcrumb items',
    },
    caseFileNumber: {
      control: 'text',
      description: 'Optional case file number for back navigation',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    items: [
      { label: 'Home', to: '/' },
      { label: 'Case Files', to: '/ce-database/case-files' },
      { label: 'Case File Details' },
    ],
  },
};

export const WithCaseFileNumber: Story = {
  args: {
    caseFileNumber: 'CF-2024-001',
  },
};

export const SingleItem: Story = {
  args: {
    items: [
      { label: 'Current Page' },
    ],
  },
};

export const LongBreadcrumbs: Story = {
  args: {
    items: [
      { label: 'Home', to: '/' },
      { label: 'Administration', to: '/admin' },
      { label: 'User Management', to: '/admin/users' },
      { label: 'User Details', to: '/admin/users/123' },
      { label: 'Edit Profile' },
    ],
  },
};
