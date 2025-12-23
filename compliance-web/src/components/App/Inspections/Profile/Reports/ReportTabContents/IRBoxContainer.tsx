import LexicalEditor from "@/components/Shared/LexicalEditor/LexicalEditor";
import { EditOutlined, RestartAltRounded } from "@mui/icons-material";
import {
  Box,
  Typography,
  IconButton,
  SxProps,
  Button,
  Tooltip,
  CircularProgress,
} from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import { useState } from "react";
import { $generateHtmlFromNodes } from "@lexical/html";
import { useModal } from "@/store/modalStore";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";

type IRBoxContainerProps = {
  title: string;
  children?: React.ReactNode;
  sx?: SxProps;
  onEdit?: () => void;
  defaultValue?: string;
  onEditSubmit?: (editorValue: string) => void;
  onReset?: () => void;
  isResetting?: boolean;
};

const IRBoxContainer = ({
  title,
  children,
  sx,
  onEdit,
  defaultValue,
  onEditSubmit,
  onReset,
  isResetting = false,
}: IRBoxContainerProps) => {
  const { setOpen, setClose } = useModal();
  const [isEdit, setIsEdit] = useState<boolean>(false);
  const [editorValue, setEditorValue] = useState<string>(defaultValue || "");
  const handleEdit = () => {
    setIsEdit(true);
    setEditorValue(defaultValue || "");
  };

  const handleSave = () => {
    setIsEdit(false);
    onEditSubmit?.(editorValue);
  };

  const handleCancel = () => {
    setIsEdit(false);
    setEditorValue("");
  };

  const handleReset = () => {
    setOpen({
      content: (
        <ConfirmationModal
          title={"Reset Template"}
          description={`This will reset the template to its default version. 
            All your changes will be permanently removed and cannot be undone. 
            Do you want to proceed?`}
          confirmButtonText="Yes, Reset"
          cancelButtonText="No, Keep Changes"
          onConfirm={() => {
            onReset?.();
            setClose();
          }}
        />
      ),
    });
  };

  return (
    <Box
      aria-label={title}
      sx={{
        border: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
        borderRadius: 1,
        ...sx,
      }}
    >
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          px: 3,
          minHeight: 40,
          borderBottom: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
        }}
      >
        <Typography variant="body1">{title}</Typography>
        <Box display="flex" gap={1}>
          {onReset && (
            <Tooltip title={isResetting ? "Regenerating..." : "Reset Template"}>
            <span>
                <IconButton 
                  size="small" 
                  color="secondary" 
                  onClick={handleReset}
                  disabled={isResetting}
                >
                  {isResetting ? (
                    <CircularProgress size={24} color="primary" />
                  ) : (
                    <RestartAltRounded />
                  )}
                </IconButton>
              </span>
            </Tooltip>
          )}
          {(onEdit || onEditSubmit) && (
            <IconButton
              size="small"
              color="secondary"
              onClick={onEdit || handleEdit}
              data-testid={`irbox-container-edit`}
              disabled={isResetting}
            >
              <EditOutlined />
            </IconButton>
          )}
        </Box>
      </Box>
      <Box px={3} py={2}>
        {isEdit ? (
          <>
            <LexicalEditor
              name={"inspection-scope"}
              label={"Text"}
              errorMsg={""}
              placeholder={"Enter text..."}
              defaultHtml={editorValue}
              height={"400px"}
              onChange={(editorState, editor) => {
                editorState.read(() => {
                  const editorStateHtmlString = $generateHtmlFromNodes(editor);
                  setEditorValue(editorStateHtmlString);
                });
              }}
            />
            <Box
              sx={{
                display: "flex",
                justifyContent: "flex-end",
                gap: 1,
                mt: 1.5,
              }}
            >
              <Button
                variant="contained"
                color="secondary"
                onClick={handleCancel}
              >
                Cancel
              </Button>
              <Button variant="contained" color="primary" onClick={handleSave}>
                Save
              </Button>
            </Box>
          </>
        ) : (
          children
        )}
      </Box>
    </Box>
  );
};

export default IRBoxContainer;
