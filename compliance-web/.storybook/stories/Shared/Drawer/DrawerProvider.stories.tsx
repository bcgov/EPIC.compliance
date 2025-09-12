import type { Meta, StoryObj } from '@storybook/react';
import DrawerProvider from '@/components/Shared/Drawer/DrawerProvider';
import { Box, Typography, Button, TextField } from '@mui/material';
import { useDrawer } from '@/store/drawerStore';
import { useMenuStore } from '@/store/menuStore';
import { useEffect } from 'react';

// Mock content components for stories
const MockDrawerContent = ({ title, description }: { title: string; description: string }) => (
  <Box sx={{ p: 3 }}>
    <Typography variant="h6" gutterBottom>
      {title}
    </Typography>
    <Typography variant="body1" color="text.secondary" paragraph>
      {description}
    </Typography>
    <TextField
      label="Sample Input"
      variant="outlined"
      fullWidth
      sx={{ mb: 2 }}
    />
    <Button variant="contained" color="primary">
      Sample Action
    </Button>
  </Box>
);

const DrawerTrigger = () => {
  const { setOpen } = useDrawer();
  
  const openDrawer = (content: React.ReactNode, width = "450px") => {
    setOpen({ content, width });
  };

  return (
    <Box sx={{ p: 3, textAlign: 'center' }}>
      <Typography variant="h6" gutterBottom>
        Drawer Provider Demo
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Click the buttons below to open different drawer configurations
      </Typography>
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
        <Button
          variant="contained"
          onClick={() => openDrawer(
            <MockDrawerContent 
              title="Default Drawer" 
              description="This is a default width drawer with sample content." 
            />
          )}
        >
          Open Default Drawer
        </Button>
        <Button
          variant="contained"
          onClick={() => openDrawer(
            <MockDrawerContent 
              title="Wide Drawer" 
              description="This is a wider drawer (600px) with more content space." 
            />,
            "600px"
          )}
        >
          Open Wide Drawer
        </Button>
        <Button
          variant="contained"
          onClick={() => openDrawer(
            <MockDrawerContent 
              title="Narrow Drawer" 
              description="This is a narrow drawer (300px) for compact content." 
            />,
            "300px"
          )}
        >
          Open Narrow Drawer
        </Button>
      </Box>
    </Box>
  );
};

const meta: Meta<typeof DrawerProvider> = {
  title: 'Shared/Drawer/DrawerProvider',
  component: DrawerProvider,
  parameters: {
    layout: 'fullscreen',
  },
  decorators: [
    (Story) => {
      // Initialize the menu store with a mock header height
      const { setAppHeaderHeight } = useMenuStore();
      
      useEffect(() => {
        setAppHeaderHeight(64); // Mock header height
      }, [setAppHeaderHeight]);

      return (
        <Box sx={{ height: '100vh', position: 'relative' }}>
          <Story />
          <DrawerTrigger />
        </Box>
      );
    },
  ],
  argTypes: {
    // DrawerProvider doesn't take props directly, it uses the store
  },
};

export default meta;
type Story = StoryObj<typeof DrawerProvider>;

export const Default: Story = {};

export const WithMockContent: Story = {
  decorators: [
    (Story) => {
      const { setOpen } = useDrawer();
      const { setAppHeaderHeight } = useMenuStore();
      
      useEffect(() => {
        setAppHeaderHeight(64);
        // Auto-open drawer with mock content
        setOpen({
          content: (
            <MockDrawerContent 
              title="Auto-opened Drawer" 
              description="This drawer opens automatically to demonstrate the component." 
            />
          ),
          width: "500px"
        });
      }, [setOpen, setAppHeaderHeight]);

      return (
        <Box sx={{ height: '100vh', position: 'relative' }}>
          <Story />
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6">
              Drawer is automatically opened above
            </Typography>
          </Box>
        </Box>
      );
    },
  ],
};

export const WithDifferentWidths: Story = {
  decorators: [
    (Story) => {
      const { setOpen } = useDrawer();
      const { setAppHeaderHeight } = useMenuStore();
      
      useEffect(() => {
        setAppHeaderHeight(64);
        // Open with extra wide drawer
        setOpen({
          content: (
            <Box sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Extra Wide Drawer (800px)
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                This drawer demonstrates the maximum width configuration.
              </Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                <TextField label="Left Column" variant="outlined" fullWidth />
                <TextField label="Right Column" variant="outlined" fullWidth />
              </Box>
            </Box>
          ),
          width: "800px"
        });
      }, [setOpen, setAppHeaderHeight]);

      return (
        <Box sx={{ height: '100vh', position: 'relative' }}>
          <Story />
        </Box>
      );
    },
  ],
};

export const WithFormContent: Story = {
  decorators: [
    (Story) => {
      const { setOpen } = useDrawer();
      const { setAppHeaderHeight } = useMenuStore();
      
      useEffect(() => {
        setAppHeaderHeight(64);
        setOpen({
          content: (
            <Box sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Form Drawer
              </Typography>
              <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField label="Name" variant="outlined" fullWidth />
                <TextField label="Email" variant="outlined" fullWidth />
                <TextField label="Phone" variant="outlined" fullWidth />
                <TextField 
                  label="Message" 
                  variant="outlined" 
                  fullWidth 
                  multiline 
                  rows={4}
                />
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2 }}>
                  <Button variant="outlined">Cancel</Button>
                  <Button variant="contained">Save</Button>
                </Box>
              </Box>
            </Box>
          ),
          width: "500px"
        });
      }, [setOpen, setAppHeaderHeight]);

      return (
        <Box sx={{ height: '100vh', position: 'relative' }}>
          <Story />
        </Box>
      );
    },
  ],
};
