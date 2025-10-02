import type { Meta, StoryObj } from '@storybook/react';
import { MoreVert, Settings, Delete } from '@mui/icons-material';
import MenuActionDropdown from '@/components/Shared/MenuActionDropdown';

const meta: Meta<typeof MenuActionDropdown> = {
  title: 'Shared/MenuActionDropdown',
  component: MenuActionDropdown,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    buttonText: {
      control: 'text',
      description: 'Text displayed on the button',
    },
    menuWidth: {
      control: 'number',
      description: 'Width of the dropdown menu',
    },
    actions: {
      control: 'object',
      description: 'Array of menu actions',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

const defaultActions = [
  { text: 'Edit', onClick: () => console.log('Edit clicked') },
  { text: 'View Details', onClick: () => console.log('View Details clicked') },
  { text: 'Delete', onClick: () => console.log('Delete clicked') },
];

export const Default: Story = {
  args: {
    buttonText: 'Actions',
    actions: defaultActions,
  },
};

export const WithCustomIcon: Story = {
  args: {
    buttonText: 'Options',
    menuIcon: <MoreVert />,
    actions: defaultActions,
  },
};

export const WithSettingsIcon: Story = {
  args: {
    buttonText: 'Settings',
    menuIcon: <Settings />,
    actions: [
      { text: 'General', onClick: () => console.log('General clicked') },
      { text: 'Privacy', onClick: () => console.log('Privacy clicked') },
      { text: 'Notifications', onClick: () => console.log('Notifications clicked') },
    ],
  },
};

export const WithHiddenActions: Story = {
  args: {
    buttonText: 'Actions',
    actions: [
      { text: 'Edit', onClick: () => console.log('Edit clicked') },
      { text: 'View Details', onClick: () => console.log('View Details clicked') },
      { text: 'Delete', onClick: () => console.log('Delete clicked'), hidden: true },
      { text: 'Archive', onClick: () => console.log('Archive clicked'), hidden: true },
    ],
  },
};

export const CustomWidth: Story = {
  args: {
    buttonText: 'Actions',
    menuWidth: 300,
    actions: [
      { text: 'Edit Item', onClick: () => console.log('Edit clicked') },
      { text: 'View Detailed Information', onClick: () => console.log('View Details clicked') },
      { text: 'Delete Permanently', onClick: () => console.log('Delete clicked') },
    ],
  },
};

export const SingleAction: Story = {
  args: {
    buttonText: 'Delete',
    menuIcon: <Delete />,
    actions: [
      { text: 'Delete Item', onClick: () => console.log('Delete clicked') },
    ],
  },
};
