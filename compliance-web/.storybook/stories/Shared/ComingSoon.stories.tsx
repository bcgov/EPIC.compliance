import type { Meta, StoryObj } from '@storybook/react';
import { Box } from '@mui/material';
import ComingSoon from '@/components/Shared/ComingSoon';

const meta: Meta<typeof ComingSoon> = {
  title: 'Shared/ComingSoon',
  component: ComingSoon,
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Box sx={{ height: '100vh' }}>
      <ComingSoon />
    </Box>
  ),
};

export const InContainer: Story = {
  render: () => (
    <Box
      sx={{
        height: '400px',
        border: '1px solid #e0e0e0',
        borderRadius: '8px',
        margin: '20px',
      }}
    >
      <ComingSoon />
    </Box>
  ),
};

export const InSmallContainer: Story = {
  render: () => (
    <Box
      sx={{
        height: '250px',
        width: '300px',
        border: '1px solid #e0e0e0',
        borderRadius: '8px',
        margin: '20px',
      }}
    >
      <ComingSoon />
    </Box>
  ),
};

