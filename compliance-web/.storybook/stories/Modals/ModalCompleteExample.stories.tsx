import type { Meta, StoryObj } from "@storybook/react";
import React from "react";
import {
  Button,
  Box,
  Typography,
  TextField,
  DialogContent,
} from "@mui/material";
import ModalProvider from "@/components/Shared/Modals/ModalProvider";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import { useModal } from "@/store/modalStore";
import { FormDecorator } from "../../decorators/FormDecorator";
import * as yup from "yup";

// Complete modal content component
const CompleteModalContent = ({
  title,
  showDelete = false,
  isLoading = false,
  isDeleteLoading = false,
}: {
  title: string;
  showDelete?: boolean;
  isLoading?: boolean;
  isDeleteLoading?: boolean;
}) => {
  return (
    <Box>
      <ModalTitleBar title={title} />
      <DialogContent dividers>
        <Typography variant="h6" gutterBottom>
          Modal Content
        </Typography>
        <Typography variant="body1" paragraph>
          This is a complete modal example that combines all three modal
          components: ModalTitleBar, ModalActions, and ModalProvider.
        </Typography>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 2 }}>
          <TextField
            label="Name"
            variant="outlined"
            fullWidth
            defaultValue="John Doe"
          />
          <TextField
            label="Email"
            type="email"
            variant="outlined"
            fullWidth
            defaultValue="john.doe@example.com"
          />
          <TextField
            label="Message"
            multiline
            rows={3}
            variant="outlined"
            fullWidth
            defaultValue="This is a sample message in the modal."
          />
        </Box>
      </DialogContent>
      <ModalActions
        primaryActionButtonText="Save Changes"
        secondaryActionButtonText="Cancel"
        onPrimaryAction={() => console.log("Save action triggered")}
        onSecondaryAction={() => console.log("Cancel action triggered")}
        onDeleteAction={
          showDelete ? () => console.log("Delete action triggered") : undefined
        }
        onDeleteConfirmationText="Are you sure you want to delete this record? This action cannot be undone."
        isButtonValidation={true}
        isLoading={isLoading}
        isDeleteActionLoading={isDeleteLoading}
      />
    </Box>
  );
};

// Demo component to show different modal states
const ModalDemo = () => {
  const { setOpen } = useModal();

  const openModal = (content: React.ReactNode, width?: string) => {
    setOpen({ content, width });
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        Complete Modal Examples
      </Typography>
      <Typography variant="body1" paragraph>
        These examples demonstrate how all modal components work together.
      </Typography>
      <Box sx={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        <Button
          variant="contained"
          onClick={() =>
            openModal(<CompleteModalContent title="Basic Modal" />, "500px")
          }
        >
          Basic Modal
        </Button>
        <Button
          variant="contained"
          onClick={() =>
            openModal(
              <CompleteModalContent
                title="Modal with Delete"
                showDelete={true}
              />,
              "500px"
            )
          }
        >
          Modal with Delete
        </Button>
        <Button
          variant="contained"
          onClick={() =>
            openModal(
              <CompleteModalContent title="Loading Modal" isLoading={true} />,
              "500px"
            )
          }
        >
          Loading Modal
        </Button>
        <Button
          variant="contained"
          onClick={() =>
            openModal(
              <CompleteModalContent
                title="Delete Loading Modal"
                showDelete={true}
                isDeleteLoading={true}
              />,
              "500px"
            )
          }
        >
          Delete Loading Modal
        </Button>
        <Button
          variant="contained"
          onClick={() =>
            openModal(
              <CompleteModalContent
                title="Wide Modal with All Features"
                showDelete={true}
                isLoading={false}
              />,
              "700px"
            )
          }
        >
          Wide Modal
        </Button>
      </Box>
      <ModalProvider />
    </Box>
  );
};

const meta: Meta<typeof ModalProvider> = {
  title: "Components/Modals/Complete Example",
  component: ModalProvider,
  parameters: {
    layout: "fullscreen",
  },
  decorators: [
    (Story) => (
      <div style={{ width: "100%", height: "100vh" }}>
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof ModalProvider>;

export const InteractiveDemo: Story = {
  render: () => <ModalDemo />,
};

export const BasicModal: Story = {
  render: () => {
    const { setOpen } = useModal();

    React.useEffect(() => {
      setOpen({
        content: <CompleteModalContent title="Basic Modal Example" />,
        width: "500px",
      });
    }, [setOpen]);

    return <ModalProvider />;
  },
};

export const ModalWithDelete: Story = {
  render: () => {
    const { setOpen } = useModal();

    React.useEffect(() => {
      setOpen({
        content: (
          <CompleteModalContent
            title="Modal with Delete Action"
            showDelete={true}
          />
        ),
        width: "500px",
      });
    }, [setOpen]);

    return <ModalProvider />;
  },
};

export const LoadingModal: Story = {
  render: () => {
    const { setOpen } = useModal();

    React.useEffect(() => {
      setOpen({
        content: (
          <CompleteModalContent title="Loading Modal" isLoading={true} />
        ),
        width: "500px",
      });
    }, [setOpen]);

    return <ModalProvider />;
  },
};

export const WideModal: Story = {
  render: () => {
    const { setOpen } = useModal();

    React.useEffect(() => {
      setOpen({
        content: (
          <CompleteModalContent
            title="Wide Modal with All Features"
            showDelete={true}
            isLoading={false}
          />
        ),
        width: "800px",
      });
    }, [setOpen]);

    return <ModalProvider />;
  },
};

export const WithFormValidation: Story = {
  render: () => {
    const { setOpen } = useModal();

    React.useEffect(() => {
      setOpen({
        content: (
          <FormDecorator
            schema={yup.object({
              name: yup.string().required("Name is required"),
              email: yup
                .string()
                .email("Invalid email")
                .required("Email is required"),
              message: yup.string().required("Message is required"),
            })}
            defaultFormValues={{ name: "", email: "", message: "" }}
          >
            <Box>
              <ModalTitleBar title="Form Validation Modal" />
              <DialogContent dividers>
                <Typography variant="h6" gutterBottom>
                  Form with Validation
                </Typography>
                <Typography variant="body1" paragraph>
                  This form has validation. The Save button will be disabled
                  until all fields are valid.
                </Typography>
                <Box
                  sx={{
                    display: "flex",
                    flexDirection: "column",
                    gap: 2,
                    mt: 2,
                  }}
                >
                  <TextField
                    label="Name *"
                    variant="outlined"
                    fullWidth
                    error={false}
                  />
                  <TextField
                    label="Email *"
                    type="email"
                    variant="outlined"
                    fullWidth
                    error={false}
                  />
                  <TextField
                    label="Message *"
                    multiline
                    rows={3}
                    variant="outlined"
                    fullWidth
                    error={false}
                  />
                </Box>
              </DialogContent>
              <ModalActions
                primaryActionButtonText="Save"
                secondaryActionButtonText="Cancel"
                onPrimaryAction={() => console.log("Save action triggered")}
                onSecondaryAction={() => console.log("Cancel action triggered")}
                isButtonValidation={true}
                isLoading={false}
              />
            </Box>
          </FormDecorator>
        ),
        width: "600px",
      });
    }, [setOpen]);

    return <ModalProvider />;
  },
};
