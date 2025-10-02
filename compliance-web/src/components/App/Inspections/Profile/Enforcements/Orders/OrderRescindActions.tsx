import { useModal } from "@/store/modalStore";
import { Box, Button, DialogActions, Typography } from "@mui/material";
import { FC, useState } from "react";
import { useFormContext } from "react-hook-form";
import LoadingButton from "@/components/Shared/LoadingButton";

type OrderRescindActionsProps = {
  onReplaceAction?: () => void;
  onRescindAction?: () => void;
  isButtonValidation?: boolean;
  onRescindConfirmationText?: string;
  isLoading?: boolean;
  isRescindActionLoading?: boolean;
};

const OrderRescindActions: FC<OrderRescindActionsProps> = ({
  onReplaceAction,
  onRescindAction,
  isButtonValidation,
  onRescindConfirmationText = "Are you sure you want to rescind this order?",
  isLoading = false,
  isRescindActionLoading = false,
}) => {
  const { setClose } = useModal();
  const formContext = useFormContext();
  const [showRescindConfirmation, setShowRescindConfirmation] = useState(false);

  const isValid = isButtonValidation ? formContext?.formState.isValid : true;

  return (
    <>
      {!showRescindConfirmation && (
        <DialogActions
          sx={{
            padding: "1rem 1.5rem",
            justifyContent: "space-between",
          }}
        >
          <Button
            variant="text"
            onClick={() => setClose()}
            data-testid="rescind-modal-button-cancel"
          >
            Cancel
          </Button>
          <Box sx={{ display: "flex", gap: "0.75rem" }}>
            <LoadingButton
              type="submit"
              data-testid="rescind-modal-button-replace"
              disabled={!isValid}
              isLoading={isLoading}
              onClick={onReplaceAction}
            >
              Replace
            </LoadingButton>
            <Button
              color="error"
              onClick={() => {
                setShowRescindConfirmation(true);
              }}
              disabled={showRescindConfirmation}
              data-testid="rescind-modal-button-rescind"
            >
              Rescind
            </Button>
          </Box>
        </DialogActions>
      )}

      {showRescindConfirmation && (
        <Box
          sx={{
            padding: "1rem 1.5rem",
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
              Rescind Confirmation
            </Typography>
            <Typography variant="body1">{onRescindConfirmationText}</Typography>
          </Box>
          <Button
            sx={{ minWidth: 100, height: 40 }}
            color="secondary"
            onClick={() => {
              setShowRescindConfirmation(false);
            }}
            data-testid="rescind-confirmation-cancel-button"
          >
            No, Cancel
          </Button>
          <LoadingButton
            sx={{ minWidth: 100, height: 40 }}
            onClick={onRescindAction}
            color="error"
            data-testid="rescind-confirmation-button"
            isLoading={isRescindActionLoading}
          >
            Yes, Rescind
          </LoadingButton>
        </Box>
      )}
    </>
  );
};

export default OrderRescindActions;
