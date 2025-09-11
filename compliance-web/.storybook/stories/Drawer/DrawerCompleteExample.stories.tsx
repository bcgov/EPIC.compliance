import type { Meta, StoryObj } from '@storybook/react';
import { FormDecorator } from '../../decorators/FormDecorator';
import DrawerProvider from '@/components/Shared/Drawer/DrawerProvider';
import DrawerTitleBar from '@/components/Shared/Drawer/DrawerTitleBar';
import DrawerActionBarTop from '@/components/Shared/Drawer/DrawerActionBarTop';
import DrawerActionBarBottom from '@/components/Shared/Drawer/DrawerActionBarBottom';
import { Box, Typography, TextField, Button, Chip } from '@mui/material';
import { useDrawer } from '@/store/drawerStore';
import { useMenuStore } from '@/store/menuStore';
import { useEffect } from 'react';
import * as yup from 'yup';

// Complete drawer content component
const CompleteDrawerContent = () => (
  <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
    <DrawerTitleBar 
      title="Create New Record" 
      isFormDirtyCheck={true}
      statusFlag={<Chip label="Draft" color="warning" size="small" />}
    />
    
    <DrawerActionBarTop 
      isShowActionBar={true} 
      isLoading={false} 
    />
    
    <Box sx={{ flex: 1, p: 3, overflow: 'auto' }}>
      <Typography variant="h6" gutterBottom>
        Record Information
      </Typography>
      <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <TextField 
          name="recordName"
          label="Record Name" 
          variant="outlined" 
          fullWidth 
          required
        />
        <TextField 
          name="description"
          label="Description" 
          variant="outlined" 
          fullWidth 
          multiline 
          rows={3}
        />
        <TextField 
          name="category"
          label="Category" 
          variant="outlined" 
          fullWidth 
        />
        <TextField 
          name="priority"
          label="Priority" 
          variant="outlined" 
          fullWidth 
        />
      </Box>
    </Box>
    
    <DrawerActionBarBottom 
      isShowActionBar={true}
      onDeleteAction={() => console.log('Delete action triggered')}
      onDeleteTitle="Delete Record"
      onDeleteDescription="Are you sure you want to delete this record? This action cannot be undone."
      isLoading={false}
    />
  </Box>
);

const DrawerTrigger = () => {
  const { setOpen } = useDrawer();
  
  const openCompleteDrawer = () => {
    setOpen({ 
      content: <CompleteDrawerContent />, 
      width: "600px" 
    });
  };

  return (
    <Box sx={{ p: 3, textAlign: 'center' }}>
      <Typography variant="h6" gutterBottom>
        Complete Drawer Example
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        This example shows all drawer components working together with form validation
      </Typography>
      <Button
        variant="contained"
        size="large"
        onClick={openCompleteDrawer}
      >
        Open Complete Drawer
      </Button>
    </Box>
  );
};

const meta: Meta<typeof DrawerProvider> = {
  title: 'Components/Drawer/Complete Example',
  component: DrawerProvider,
  parameters: {
    layout: 'fullscreen',
  },
  decorators: [
    (Story) => {
      const { setAppHeaderHeight } = useMenuStore();
      
      useEffect(() => {
        setAppHeaderHeight(64);
      }, [setAppHeaderHeight]);

      return (
        <FormDecorator
          schema={yup.object({
            recordName: yup.string().required('Record name is required'),
            description: yup.string().optional(),
            category: yup.string().optional(),
            priority: yup.string().optional(),
          })}
          defaultFormValues={{
            recordName: '',
            description: '',
            category: '',
            priority: '',
          }}
        >
          <Box sx={{ height: '100vh', position: 'relative' }}>
            <Story />
            <DrawerTrigger />
          </Box>
        </FormDecorator>
      );
    },
  ],
};

export default meta;
type Story = StoryObj<typeof DrawerProvider>;

export const CompleteDrawerExample: Story = {};

export const WithPreFilledData: Story = {
  decorators: [
    (Story) => {
      const { setAppHeaderHeight } = useMenuStore();
      
      useEffect(() => {
        setAppHeaderHeight(64);
      }, [setAppHeaderHeight]);

      return (
        <FormDecorator
          schema={yup.object({
            recordName: yup.string().required('Record name is required'),
            description: yup.string().optional(),
            category: yup.string().optional(),
            priority: yup.string().optional(),
          })}
          defaultFormValues={{
            recordName: 'Sample Record',
            description: 'This is a pre-filled description',
            category: 'Important',
            priority: 'High',
          }}
        >
          <Box sx={{ height: '100vh', position: 'relative' }}>
            <Story />
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                Drawer with Pre-filled Data
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                This example shows the drawer with pre-filled form data
              </Typography>
              <Button
                variant="contained"
                size="large"
                onClick={() => {
                  const { setOpen } = useDrawer();
                  setOpen({ 
                    content: <CompleteDrawerContent />, 
                    width: "600px" 
                  });
                }}
              >
                Open Drawer with Data
              </Button>
            </Box>
          </Box>
        </FormDecorator>
      );
    },
  ],
};
