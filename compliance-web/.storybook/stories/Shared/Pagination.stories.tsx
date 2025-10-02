import type { Meta, StoryObj } from '@storybook/react';
import Pagination from '@/components/Shared/Pagination';

const meta: Meta<typeof Pagination> = {
  title: 'Shared/Pagination',
  component: Pagination,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    currentPage: {
      control: 'number',
      description: 'Current page index (0-based)',
    },
    pageSize: {
      control: 'number',
      description: 'Number of items per page',
    },
    totalCount: {
      control: 'number',
      description: 'Total number of items',
    },
    canPreviousPage: {
      control: 'boolean',
      description: 'Whether previous page navigation is available',
    },
    canNextPage: {
      control: 'boolean',
      description: 'Whether next page navigation is available',
    },
    onPreviousPage: {
      description: 'Callback function when previous page button is clicked',
    },
    onNextPage: {
      description: 'Callback function when next page button is clicked',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    currentPage: 0,
    pageSize: 10,
    totalCount: 100,
    canPreviousPage: false,
    canNextPage: true,
    onPreviousPage: () => console.log('Previous page clicked'),
    onNextPage: () => console.log('Next page clicked'),
  },
};

export const LastPage: Story = {
  args: {
    currentPage: 9,
    pageSize: 10,
    totalCount: 95,
    canPreviousPage: true,
    canNextPage: false,
    onPreviousPage: () => console.log('Previous page clicked'),
    onNextPage: () => console.log('Next page clicked'),
  },
};

export const SinglePage: Story = {
  args: {
    currentPage: 0,
    pageSize: 50,
    totalCount: 25,
    canPreviousPage: false,
    canNextPage: false,
    onPreviousPage: () => console.log('Previous page clicked'),
    onNextPage: () => console.log('Next page clicked'),
  },
};
