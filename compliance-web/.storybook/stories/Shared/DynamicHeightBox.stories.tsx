import type { Meta, StoryObj } from '@storybook/react';
import { Typography, Box } from '@mui/material';
import DynamicHeightBox from '@/components/Shared/DynamicHeightBox';

const meta: Meta<typeof DynamicHeightBox> = {
  title: 'Shared/DynamicHeightBox',
  component: DynamicHeightBox,
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
  argTypes: {
    bottomOffset: {
      control: 'number',
      description: 'Additional offset to subtract from calculated height',
    },
    includePadding: {
      control: 'boolean',
      description: 'Whether to include vertical padding in height calculation',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, bgcolor: 'primary.main' }}>
        <Typography variant="h5" color="white">Header Section</Typography>
        <Typography variant="body2" color="white">This header takes up some space at the top</Typography>
      </Box>
      <DynamicHeightBox
        sx={{
          bgcolor: 'grey.100',
          p: 2,
          border: '1px solid',
          borderColor: 'grey.300',
        }}
      >
        <Typography variant="h6" gutterBottom>
          Dynamic Height Box
        </Typography>
        <Typography variant="body1" paragraph>
          This box automatically calculates its height to fill the remaining viewport space.
          The height adjusts based on the component's position from the top of the viewport.
        </Typography>
        <Typography variant="body1" paragraph>
          Try resizing the browser window to see how the height adjusts dynamically.
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Bottom of the dynamic content area
          </Typography>
        </Box>
      </DynamicHeightBox>
    </Box>
  ),
};

export const WithBottomOffset: Story = {
  render: () => (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, bgcolor: 'secondary.main' }}>
        <Typography variant="h5">Header with Footer</Typography>
      </Box>
      <DynamicHeightBox
        bottomOffset={100}
        sx={{
          bgcolor: 'grey.100',
          p: 2,
          border: '1px solid',
          borderColor: 'grey.300',
        }}
      >
        <Typography variant="h6" gutterBottom>
          With Bottom Offset
        </Typography>
        <Typography variant="body1" paragraph>
          This box has a 100px bottom offset, leaving space for a footer.
        </Typography>
      </DynamicHeightBox>
      <Box sx={{ p: 2, bgcolor: 'error.main', color: 'white', height: 100 }}>
        <Typography variant="body2">Footer (100px height)</Typography>
      </Box>
    </Box>
  ),
};

export const WithPadding: Story = {
  render: () => (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, bgcolor: 'success.main', color: 'white' }}>
        <Typography variant="h5">Header Section</Typography>
      </Box>
      <DynamicHeightBox
        includePadding={true}
        sx={{
          bgcolor: 'grey.100',
          p: 4,
          border: '1px solid',
          borderColor: 'grey.300',
        }}
      >
        <Typography variant="h6" gutterBottom>
          With Padding Included
        </Typography>
        <Typography variant="body1" paragraph>
          This box includes its padding in the height calculation.
          Notice how the padding is accounted for in the total height.
        </Typography>
      </DynamicHeightBox>
    </Box>
  ),
};

export const CustomHeightCalculator: Story = {
  render: () => (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, bgcolor: 'warning.main', color: 'white' }}>
        <Typography variant="h5">Custom Height Calculator</Typography>
      </Box>
      <DynamicHeightBox
        heightCalculator={(topPosition) => `calc(100vh - ${topPosition + 50}px)`}
        sx={{
          bgcolor: 'grey.100',
          p: 2,
          border: '1px solid',
          borderColor: 'grey.300',
        }}
      >
        <Typography variant="h6" gutterBottom>
          Custom Height Calculation
        </Typography>
        <Typography variant="body1" paragraph>
          This box uses a custom height calculator that adds 50px to the top position.
        </Typography>
      </DynamicHeightBox>
    </Box>
  ),
};

export const WithScrollableContent: Story = {
  render: () => (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, bgcolor: 'info.main', color: 'white' }}>
        <Typography variant="h5">Scrollable Content</Typography>
      </Box>
      <DynamicHeightBox
        sx={{
          bgcolor: 'grey.100',
          p: 2,
          border: '1px solid',
          borderColor: 'grey.300',
          overflow: 'auto',
        }}
      >
        <Typography variant="h6" gutterBottom>
          Scrollable Dynamic Box
        </Typography>
        {Array.from({ length: 20 }, (_, i) => (
          <Typography key={i} variant="body1" paragraph>
            This is paragraph {i + 1}. The content is long enough to require scrolling
            within the dynamically sized container. The box maintains its calculated height
            while allowing internal scrolling when content exceeds the available space.
          </Typography>
        ))}
      </DynamicHeightBox>
    </Box>
  ),
};
