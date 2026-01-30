import { DialogContent, Typography } from "@mui/material";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import { FC } from "react";
import { useUpdateInspectionRecord } from "@/hooks/useInspectionReports";
import { useReportStore } from "./reportStore";
import { InspectionRecord } from "@/models/InspectionRecord";

type IssueIRModalProps = {
  onSubmit: (message: string) => void | Promise<void>;};

const IssueIRModal: FC<IssueIRModalProps> = ({ onSubmit }) => {
  const { inspectionData, inspectionReportsData, setInspectionReportsData } =
    useReportStore();

  const onSuccess = (data: InspectionRecord) => {
    setInspectionReportsData(data);
    onSubmit("Inspection Record Issued");
  };

  const { mutate: updateInspectionRecord, isPending } =
    useUpdateInspectionRecord(onSuccess);

  const onSubmitHandler = async () => {
    updateInspectionRecord({
      inspectionId: inspectionData?.id ?? 0,
      inspectionRecordId: inspectionReportsData?.id ?? 0,
      updateRecord: {
        field_name: "date_issued",
        value: inspectionReportsData?.intended_issuance_date ?? "",
      },
    });
  };

  return (
    <>
      <ModalTitleBar title={"Issue IR?"} />
      <DialogContent dividers>
        <Typography variant="body1" mb={2}>
          You are about to issue Inspection Record:{" "}
          <b>{inspectionData?.ir_number}</b>
        </Typography>
        <Typography variant="body2" mb={1.5}>
          Once issued, this Inspection will be locked and cannot be edited. You
          will no longer be able to download the report, but it will remain
          available for preview.
        </Typography>
      </DialogContent>
      <ModalActions
        primaryActionButtonText={"Save & Issue"}
        isLoading={isPending}
        onPrimaryAction={onSubmitHandler}
      />
    </>
  );
};

export default IssueIRModal;
