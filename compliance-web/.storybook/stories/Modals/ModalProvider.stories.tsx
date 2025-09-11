import type { Meta, StoryObj } from "@storybook/react";
import React, { useState } from "react";
import { Button, Box, Typography } from "@mui/material";
import ModalProvider from "@/components/Shared/Modals/ModalProvider";
import { useModal } from "@/store/modalStore";

// Mock component to demonstrate modal usage
const ModalDemo = () => {
  const { setOpen, setClose } = useModal();
  const [modalContent, setModalContent] = useState<React.ReactNode>(null);

  const openModal = (content: React.ReactNode, width?: string) => {
    setModalContent(content);
    setOpen({ content, width });
  };

  const closeModal = () => {
    setClose();
    setModalContent(null);
  };

  return (
    <Box sx={{ padding: "20px" }}>
      <Typography variant="h6" gutterBottom>
        Modal Provider Demo
      </Typography>
      <Box sx={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        <Button
          variant="contained"
          onClick={() =>
            openModal(
              <Box sx={{ padding: "20px" }}>
                <Typography variant="h6" gutterBottom>
                  Basic Modal
                </Typography>
                <Typography variant="body1">
                  This is a basic modal with default width (400px).
                </Typography>
                <Button
                  variant="outlined"
                  onClick={closeModal}
                  sx={{ mt: 2 }}
                >
                  Close Modal
                </Button>
              </Box>
            )
          }
        >
          Open Basic Modal
        </Button>
        <Button
          variant="contained"
          onClick={() =>
            openModal(
              <Box sx={{ padding: "20px" }}>
                <Typography variant="h6" gutterBottom>
                  Wide Modal
                </Typography>
                <Typography variant="body1">
                  This is a wider modal (600px).
                </Typography>
                <Button
                  variant="outlined"
                  onClick={closeModal}
                  sx={{ mt: 2 }}
                >
                  Close Modal
                </Button>
              </Box>,
              "600px"
            )
          }
        >
          Open Wide Modal
        </Button>
        <Button
          variant="contained"
          onClick={() =>
            openModal(
              <Box sx={{ padding: "20px" }}>
                <Typography variant="h6" gutterBottom>
                  Narrow Modal
                </Typography>
                <Typography variant="body1">
                  This is a narrow modal (300px).
                </Typography>
                <Button
                  variant="outlined"
                  onClick={closeModal}
                  sx={{ mt: 2 }}
                >
                  Close Modal
                </Button>
              </Box>,
              "300px"
            )
          }
        >
          Open Narrow Modal
        </Button>
        <Button
          variant="contained"
          onClick={() =>
            openModal(
              <Box sx={{ padding: "20px" }}>
                <Typography variant="h6" gutterBottom>
                  Large Content Modal
                </Typography>
                <Typography variant="body1" paragraph>
                  This modal contains a lot of content to demonstrate scrolling
                  behavior when the content exceeds the viewport height.
                </Typography>
                {Array.from({ length: 20 }, (_, i) => (
                  <Typography key={i} variant="body2" paragraph>
                    This is paragraph {i + 1} of content. Lorem ipsum dolor sit
                    amet, consectetur adipiscing elit. Sed do eiusmod tempor
                    incididunt ut labore et dolore magna aliqua.
                  </Typography>
                ))}
                <Button
                  variant="outlined"
                  onClick={closeModal}
                  sx={{ mt: 2 }}
                >
                  Close Modal
                </Button>
              </Box>,
              "500px"
            )
          }
        >
          Open Large Content Modal
        </Button>
      </Box>
      <ModalProvider />
    </Box>
  );
};

const meta: Meta<typeof ModalProvider> = {
  title: "Components/Modals/ModalProvider",
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
  argTypes: {
    // ModalProvider doesn't take props directly, it uses the store
  },
};

export default meta;
type Story = StoryObj<typeof ModalProvider>;

export const Default: Story = {
  render: () => <ModalDemo />,
};

export const WithCustomContent: Story = {
  render: () => {
    const { setOpen } = useModal();
    
    // Open modal immediately when story loads
    React.useEffect(() => {
      setOpen({
        content: (
          <Box sx={{ padding: "20px" }}>
            <Typography variant="h6" gutterBottom>
              Auto-opened Modal
            </Typography>
            <Typography variant="body1">
              This modal opens automatically when the story loads.
            </Typography>
          </Box>
        ),
        width: "450px",
      });
    }, [setOpen]);

    return <ModalProvider />;
  },
};

export const WithFormContent: Story = {
  render: () => {
    const { setOpen } = useModal();
    
    React.useEffect(() => {
      setOpen({
        content: (
          <Box sx={{ padding: "20px" }}>
            <Typography variant="h6" gutterBottom>
              Form Modal
            </Typography>
            <Box component="form" sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
              <input
                type="text"
                placeholder="Enter your name"
                style={{ padding: "8px", border: "1px solid #ccc", borderRadius: "4px" }}
              />
              <input
                type="email"
                placeholder="Enter your email"
                style={{ padding: "8px", border: "1px solid #ccc", borderRadius: "4px" }}
              />
              <Button variant="contained" sx={{ mt: 1 }}>
                Submit
              </Button>
            </Box>
          </Box>
        ),
        width: "400px",
      });
    }, [setOpen]);

    return <ModalProvider />;
  },
};
