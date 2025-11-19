import { DialogContent, DialogContentText } from "@mui/material";
import { ReactNode } from "react";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import ModalActions from "@/components/Shared/Modals/ModalActions";

type ConfirmationModalProps = {
  title: string;
  description?: string;
  formattedDescription?: ReactNode;
  confirmButtonText?: string;
  cancelButtonText?: string;
  showActions?: boolean;
  hideSecondaryButton?: boolean;
  onConfirm: () => void;
  onCancel?: () => void;
};

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  title,
  description,
  formattedDescription,
  confirmButtonText,
  cancelButtonText,
  showActions = true,
  hideSecondaryButton = false,
  onConfirm,
  onCancel,
}) => {
  return (
    <>
      <ModalTitleBar title={title} onClose={onCancel} />
      <DialogContent dividers>
        {formattedDescription ? (
          formattedDescription
        ) : (
          <DialogContentText>{description}</DialogContentText>
        )}
      </DialogContent>
      {showActions === true && (
        <ModalActions
          primaryActionButtonText={confirmButtonText}
          secondaryActionButtonText={cancelButtonText}
          onPrimaryAction={onConfirm}
          onSecondaryAction={onCancel}
          hideSecondaryButton={hideSecondaryButton}
        />
      )}
    </>
  );
};

export default ConfirmationModal;
