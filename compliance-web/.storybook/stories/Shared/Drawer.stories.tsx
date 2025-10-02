import type { Meta, StoryObj } from "@storybook/react";
import { FormDecorator } from "../../decorators/FormDecorator";
import DrawerProvider from "@/components/Shared/Drawer/DrawerProvider";
import DrawerTitleBar from "@/components/Shared/Drawer/DrawerTitleBar";
import DrawerActionBarTop from "@/components/Shared/Drawer/DrawerActionBarTop";
import DrawerActionBarBottom from "@/components/Shared/Drawer/DrawerActionBarBottom";
import { Box, Typography, TextField, Button, Chip, Stack } from "@mui/material";
import { useDrawer } from "@/store/drawerStore";
import { useMenuStore } from "@/store/menuStore";
import { useEffect } from "react";
import * as yup from "yup";

// Complete drawer content component (shows all components for demonstration)
const CompleteDrawerContent = () => (
  <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
    <DrawerTitleBar
      title="Drawer Example"
      isFormDirtyCheck={true}
      statusFlag={
        <Chip
          label="Custom Flag"
          color="warning"
          variant="outlined"
          size="small"
        />
      }
    />

    <DrawerActionBarTop isShowActionBar={true} isLoading={false} />

    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        flex: 1,
        px: 4,
        py: 2,
        overflow: "auto",
      }}
    >
      <Typography variant="h6" gutterBottom>
        Record Information
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        This complete example shows all drawer components together for
        demonstration purposes
      </Typography>
      <Box
        component="form"
        sx={{ display: "flex", flexDirection: "column", gap: 2 }}
      >
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
      onDeleteAction={() => console.log("Delete action triggered")}
      onDeleteTitle="Delete Record"
      onDeleteDescription="Are you sure you want to delete this record? This action cannot be undone."
      isLoading={false}
    />
  </Box>
);

// Create drawer content component (with Create button only)
const CreateDrawerContent = () => (
  <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
    <DrawerTitleBar title="Create New Record" isFormDirtyCheck={true} />

    <DrawerActionBarTop isShowActionBar={true} isLoading={false} />

    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        flex: 1,
        px: 4,
        py: 2,
        overflow: "auto",
      }}
    >
      <Typography variant="h6" gutterBottom>
        New Record Details
      </Typography>
      <Box
        component="form"
        sx={{ display: "flex", flexDirection: "column", gap: 2 }}
      >
        <TextField
          name="recordName"
          label="Record Name"
          variant="outlined"
          fullWidth
          required
          placeholder="Enter record name"
        />
        <TextField
          name="description"
          label="Description"
          variant="outlined"
          fullWidth
          multiline
          rows={3}
          placeholder="Describe the record"
        />
        <TextField
          name="category"
          label="Category"
          variant="outlined"
          fullWidth
          placeholder="Select category"
        />
        <TextField
          name="priority"
          label="Priority"
          variant="outlined"
          fullWidth
          placeholder="Set priority level"
        />
      </Box>
    </Box>

    {/* No DrawerActionBarBottom for create mode */}
  </Box>
);

// Save drawer content component (with Save button only)
const SaveDrawerContent = () => (
  <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
    <DrawerTitleBar
      title="Save Changes"
      isFormDirtyCheck={false}
      isDirtyManual={true}
      statusFlag={
        <Chip
          label="Custom Flag"
          color="warning"
          variant="outlined"
          size="small"
        />
      }
    />

    {/* No DrawerActionBarTop for edit/save mode */}

    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        flex: 1,
        px: 4,
        py: 2,
        overflow: "auto",
      }}
    >
      <Typography variant="h6" gutterBottom>
        Review Changes
      </Typography>
      <Box component="form" sx={{ display: "flex", flexDirection: "column" }}>
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
      isLoading={false}
      isDirtyManual={true}
    />
  </Box>
);

const DrawerTrigger = () => {
  const { setOpen } = useDrawer();

  const openDrawer = (content: React.ReactNode) => {
    setOpen({
      content,
      width: "600px",
    });
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2, p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Drawer Examples
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Click the buttons below to open different drawer configurations
      </Typography>
      <Stack
        direction="column"
        spacing={2}
        justifyContent="flex-start"
        flexWrap="wrap"
      >
        <Button
          variant="contained"
          size="large"
          onClick={() => openDrawer(<CompleteDrawerContent />)}
        >
          Complete Drawer Example
        </Button>
        <Button
          variant="contained"
          size="large"
          onClick={() => openDrawer(<CreateDrawerContent />)}
        >
          Create Drawer Example
        </Button>
        <Button
          variant="contained"
          size="large"
          onClick={() => openDrawer(<SaveDrawerContent />)}
        >
          Save Drawer Example
        </Button>
      </Stack>
    </Box>
  );
};

const meta: Meta<typeof DrawerProvider> = {
  title: "Shared/Drawer",
  component: DrawerProvider,
  parameters: {
    layout: "fullscreen",
  },
  decorators: [
    () => {
      const { setAppHeaderHeight } = useMenuStore();

      useEffect(() => {
        setAppHeaderHeight(64);
      }, [setAppHeaderHeight]);

      return (
        <FormDecorator
          schema={yup.object({
            recordName: yup.string().required("Record name is required"),
            description: yup.string().optional(),
            category: yup.string().optional(),
            priority: yup.string().optional(),
          })}
          defaultFormValues={{
            recordName: "",
            description: "",
            category: "",
            priority: "",
          }}
        >
          <Box sx={{ height: "100vh", position: "relative" }}>
            <DrawerProvider />
            <DrawerTrigger />
          </Box>
        </FormDecorator>
      );
    },
  ],
};

export default meta;
type Story = StoryObj<typeof DrawerProvider>;

export const CompleteExample: Story = {
  decorators: [
    () => {
      const { setAppHeaderHeight } = useMenuStore();

      useEffect(() => {
        setAppHeaderHeight(64);
      }, [setAppHeaderHeight]);

      return (
        <FormDecorator
          schema={yup.object({
            recordName: yup.string().required("Record name is required"),
            description: yup.string().optional(),
            category: yup.string().optional(),
            priority: yup.string().optional(),
          })}
          defaultFormValues={{
            recordName: "Sample Record",
            description: "This is a sample description",
            category: "Important",
            priority: "High",
          }}
        >
          <Box sx={{ height: "100vh", position: "relative" }}>
            <DrawerProvider />
            <Box sx={{ p: 3, textAlign: "center" }}>
              <Typography variant="h6" gutterBottom>
                Complete Drawer Example
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                This example shows all drawer components working together with
                form validation and delete functionality
              </Typography>
              <Button
                variant="contained"
                size="large"
                onClick={() => {
                  const { setOpen } = useDrawer();
                  setOpen({
                    content: <CompleteDrawerContent />,
                    width: "600px",
                  });
                }}
              >
                Open Complete Example
              </Button>
            </Box>
          </Box>
        </FormDecorator>
      );
    },
  ],
};

export const CreateExample: Story = {
  decorators: [
    () => {
      const { setAppHeaderHeight } = useMenuStore();

      useEffect(() => {
        setAppHeaderHeight(64);
      }, [setAppHeaderHeight]);

      return (
        <FormDecorator
          schema={yup.object({
            recordName: yup.string().required("Record name is required"),
            description: yup.string().optional(),
            category: yup.string().optional(),
            priority: yup.string().optional(),
          })}
          defaultFormValues={{
            recordName: "",
            description: "",
            category: "",
            priority: "",
          }}
        >
          <Box sx={{ height: "100vh", position: "relative" }}>
            <DrawerProvider />
            <Box sx={{ p: 3, textAlign: "center" }}>
              <Typography variant="h6" gutterBottom>
                Create Drawer Example
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                This example demonstrates the drawer for creating new records
                with empty form fields
              </Typography>
              <Button
                variant="contained"
                size="large"
                onClick={() => {
                  const { setOpen } = useDrawer();
                  setOpen({
                    content: <CreateDrawerContent />,
                    width: "600px",
                  });
                }}
              >
                Open Create Example
              </Button>
            </Box>
          </Box>
        </FormDecorator>
      );
    },
  ],
};

export const SaveExample: Story = {
  decorators: [
    () => {
      const { setAppHeaderHeight } = useMenuStore();

      useEffect(() => {
        setAppHeaderHeight(64);
      }, [setAppHeaderHeight]);

      return (
        <FormDecorator
          schema={yup.object({
            recordName: yup.string().required("Record name is required"),
            description: yup.string().optional(),
            category: yup.string().optional(),
            priority: yup.string().optional(),
          })}
          defaultFormValues={{
            recordName: "Modified Record Name",
            description: "This description has been modified",
            category: "Updated Category",
            priority: "Medium",
          }}
        >
          <Box sx={{ height: "100vh", position: "relative" }}>
            <DrawerProvider />
            <Box sx={{ p: 3, textAlign: "center" }}>
              <Typography variant="h6" gutterBottom>
                Save Drawer Example
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                This example shows the drawer with unsaved changes, emphasizing
                the save functionality
              </Typography>
              <Button
                variant="contained"
                size="large"
                onClick={() => {
                  const { setOpen } = useDrawer();
                  setOpen({
                    content: <SaveDrawerContent />,
                    width: "600px",
                  });
                }}
              >
                Open Save Example
              </Button>
            </Box>
          </Box>
        </FormDecorator>
      );
    },
  ],
};
