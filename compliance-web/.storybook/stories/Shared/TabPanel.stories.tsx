import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import { Box, Tabs, Tab, Typography } from '@mui/material';
import TabPanel from '../../../src/components/Shared/TabPanel';

const meta: Meta<typeof TabPanel> = {
  title: 'Shared/TabPanel',
  component: TabPanel,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    index: {
      control: 'number',
      description: 'Tab index',
    },
    value: {
      control: 'number',
      description: 'Current active tab value',
    },
    id: {
      control: 'text',
      description: 'Unique identifier for the tab panel',
    },
    width: {
      control: 'text',
      description: 'Width of the tab panel',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

// Helper component to demonstrate TabPanel usage
const TabPanelDemo = ({ width = "75%" }: { width?: string }) => {
  const [value, setValue] = useState(0);

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
          <Tab label="Item One" />
          <Tab label="Item Two" />
          <Tab label="Item Three" />
        </Tabs>
      </Box>
      <TabPanel value={value} index={0} id="demo-tabpanel" width={width}>
        <Typography variant="h6" gutterBottom>
          Tab One Content
        </Typography>
        <Typography variant="body1">
          This is the content for the first tab. It can contain any React components or elements.
        </Typography>
      </TabPanel>
      <TabPanel value={value} index={1} id="demo-tabpanel" width={width}>
        <Typography variant="h6" gutterBottom>
          Tab Two Content
        </Typography>
        <Typography variant="body1">
          This is the content for the second tab. Notice how the content changes when you switch tabs.
        </Typography>
      </TabPanel>
      <TabPanel value={value} index={2} id="demo-tabpanel" width={width}>
        <Typography variant="h6" gutterBottom>
          Tab Three Content
        </Typography>
        <Typography variant="body1">
          This is the content for the third tab. The TabPanel component handles the visibility logic.
        </Typography>
      </TabPanel>
    </Box>
  );
};

export const Default: Story = {
  render: () => <TabPanelDemo />,
};

export const CustomWidth: Story = {
  render: () => <TabPanelDemo width="100%" />,
};

export const NarrowWidth: Story = {
  render: () => <TabPanelDemo width="50%" />,
};

export const WithFormContent: Story = {
  render: () => {
    const [value, setValue] = useState(0);

    const handleChange = (event: React.SyntheticEvent, newValue: number) => {
      setValue(newValue);
    };

    return (
      <Box sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={value} onChange={handleChange}>
            <Tab label="Personal Info" />
            <Tab label="Contact Details" />
            <Tab label="Preferences" />
          </Tabs>
        </Box>
        <TabPanel value={value} index={0} id="form-tabpanel">
          <Box sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Personal Information</Typography>
            <Typography variant="body2" color="text.secondary">
              Enter your personal details here.
            </Typography>
          </Box>
        </TabPanel>
        <TabPanel value={value} index={1} id="form-tabpanel">
          <Box sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Contact Details</Typography>
            <Typography variant="body2" color="text.secondary">
              Provide your contact information.
            </Typography>
          </Box>
        </TabPanel>
        <TabPanel value={value} index={2} id="form-tabpanel">
          <Box sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Preferences</Typography>
            <Typography variant="body2" color="text.secondary">
              Configure your application preferences.
            </Typography>
          </Box>
        </TabPanel>
      </Box>
    );
  },
};
