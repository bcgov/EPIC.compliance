import { Box, DialogContent } from "@mui/material";
import { FC } from "react";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import { sanitizeHtml } from "@/utils/sanitizeHtml";

type ReportPreviewModalProps = {
  previewHtml: string;
};

const ReportPreviewModal: FC<ReportPreviewModalProps> = ({ previewHtml }) => {
  return (
    <>
      <ModalTitleBar title="Report Preview" />
      <DialogContent dividers sx={{ maxHeight: "80vh" }}>
        {previewHtml ? (
          <Box
            sx={{
              height: "100%",
              overflow: "auto",
              "& img": { maxWidth: "100%" },
            }}
            dangerouslySetInnerHTML={{ __html: sanitizeHtml(previewHtml) }}
          />
        ) : (
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              height: "100%",
            }}
          >
            No preview available
          </Box>
        )}
      </DialogContent>
    </>
  );
};

export default ReportPreviewModal;
