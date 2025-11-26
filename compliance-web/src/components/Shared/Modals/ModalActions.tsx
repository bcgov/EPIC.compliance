import { useModal } from "@/store/modalStore";
import { DeleteOutlineRounded } from "@mui/icons-material";
import { Box, Button, DialogActions, Typography } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import { FC, useState } from "react";
import { useFormContext } from "react-hook-form";
import LoadingButton from "@/components/Shared/LoadingButton";

type ModalActionsProps = {
  primaryActionButtonText?: string;
  secondaryActionButtonText?: string;
  onPrimaryAction?: () => void;
  onSecondaryAction?: () => void;
  isButtonValidation?: boolean;
  onDeleteAction?: () => void;
  onDeleteConfirmationText?: string;
  isLoading?: boolean;
  isDeleteActionLoading?: boolean;
  hideSecondaryButton?: boolean;
  requireSaveConfirmation?: boolean;
  onSaveConfirmationText?: string;
  onSaveConfirmationTitle?: string;
};

const ModalActions: FC<ModalActionsProps> = ({
  primaryActionButtonText,
  secondaryActionButtonText,
  onPrimaryAction,
  onSecondaryAction,
  isButtonValidation,
  onDeleteAction,
  onDeleteConfirmationText = "Are you sure you want to delete this?",
  isLoading = false,
  isDeleteActionLoading = false,
  hideSecondaryButton = false,
  requireSaveConfirmation = false,
  onSaveConfirmationText = "All required information has been entered, so please review the details before continuing.",
  onSaveConfirmationTitle = "Locking Enforcement",
}) => {
  const { setClose } = useModal();
  const formContext = useFormContext();
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false);
  const [showSaveConfirmation, setShowSaveConfirmation] = useState(false);

  const isValid = isButtonValidation ? formContext?.formState.isValid : true;

  const handlePrimaryAction = () => {
    if (requireSaveConfirmation && !showSaveConfirmation) {
      setShowSaveConfirmation(true);
    } else {
      onPrimaryAction?.();
    }
  };

  return (
    <>
      {!showDeleteConfirmation && !showSaveConfirmation && (
        <DialogActions
          sx={{
            padding: "1rem 1.5rem",
            justifyContent: onDeleteAction ? "space-between" : "flex-end",
          }}
        >
          {onDeleteAction && (
            <Button
              variant="text"
              startIcon={<DeleteOutlineRounded />}
              onClick={() => {
                setShowDeleteConfirmation(true);
              }}
              disabled={showDeleteConfirmation}
              data-testid="delete-action-modal-button"
            >
              Delete
            </Button>
          )}
          <Box sx={{ display: "flex", gap: "0.75rem" }}>
            {!hideSecondaryButton && (
              <Button
                variant="text"
                onClick={() => {
                  onSecondaryAction?.();
                  setClose();
                }}
                disabled={showDeleteConfirmation}
                data-testid="cancel-action-modal-button"
              >
                {secondaryActionButtonText ?? "Cancel"}
              </Button>
            )}
            <LoadingButton
              sx={{ minWidth: 100 }}
              type={onPrimaryAction ? "button" : "submit"}
              isLoading={isLoading}
              onClick={handlePrimaryAction}
              disabled={
                (!!isButtonValidation && !isValid) || showDeleteConfirmation
              }
              data-testid="primary-action-modal-button"
            >
              {primaryActionButtonText ?? "Ok"}
            </LoadingButton>
          </Box>
        </DialogActions>
      )}
      {showDeleteConfirmation && (
        <Box
          sx={{
            background: BCDesignTokens.supportSurfaceColorDanger,
            borderTop: `${BCDesignTokens.layoutBorderWidthSmall} solid ${BCDesignTokens.surfaceColorBorderDefault}`,
            padding: ".5rem 1.5rem",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "0.5rem",
          }}
        >
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              flexWrap: "wrap",
              flex: 1,
            }}
          >
            <Typography variant="body1" fontWeight={"bold"}>
              Delete Confirmation
            </Typography>
            <Typography variant="body1">{onDeleteConfirmationText}</Typography>
          </Box>
          <Button
            sx={{ minWidth: 100, height: 40 }}
            color="secondary"
            onClick={() => {
              setShowDeleteConfirmation(false);
            }}
            data-testid="delete-confirmation-cancel-button"
          >
            No, Cancel
          </Button>
          <LoadingButton
            sx={{ minWidth: 100, height: 40 }}
            onClick={onDeleteAction}
            color="error"
            data-testid="delete-confirmation-button"
            isLoading={isDeleteActionLoading}
          >
            Yes, Delete
          </LoadingButton>
        </Box>
      )}
      {showSaveConfirmation && (
        <Box
          sx={{
            background: BCDesignTokens.supportSurfaceColorDanger,
            borderTop: `${BCDesignTokens.layoutBorderWidthSmall} solid ${BCDesignTokens.surfaceColorBorderDefault}`,
            padding: ".5rem 1.5rem",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "0.5rem",
          }}
        >
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              flexWrap: "wrap",
              flex: 1,
            }}
          >
            <Typography variant="body1" fontWeight={"bold"}>
              {onSaveConfirmationTitle}
            </Typography>
            <Typography variant="body1">{onSaveConfirmationText}</Typography>
          </Box>
          <Button
            sx={{ minWidth: 100, height: 40 }}
            color="secondary"
            onClick={() => {
              setShowSaveConfirmation(false);
            }}
            data-testid="save-confirmation-cancel-button"
          >
            No, Cancel
          </Button>
          <LoadingButton
            sx={{ minWidth: 100, height: 40 }}
            onClick={onPrimaryAction}
            color="error"
            data-testid="save-confirmation-button"
            isLoading={isLoading}
          >
            Yes, Save
          </LoadingButton>
        </Box>
      )}
    </>
  );
};

export default ModalActions;
