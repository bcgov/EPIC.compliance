import { DialogContent, Typography } from "@mui/material";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import { FC } from "react";
import {
  useResetInspectionRecord,
  useUpdateInspectionRecord,
  useUpdateIRApproval,
} from "@/hooks/useInspectionReports";
import { useReportStore } from "./reportStore";
import { InspectionRecord } from "@/models/InspectionRecord";
import { IRProgressEnum } from "@/utils/constants";
import { notify } from "@/store/snackbarStore";

type ReopenIRModalProps = {
  onSubmit: (message: string) => void;
  previousApprovalId?: number;
};

const ReopenIRModal: FC<ReopenIRModalProps> = ({ onSubmit, previousApprovalId }) => {
  const { inspectionData, inspectionReportsData, setInspectionReportsData } =
    useReportStore();

  const handleOnUpdateSuccess = (data: InspectionRecord) => {
    setInspectionReportsData(data);
    onSubmit("Inspection Record Reopened");
  };

  const handleOnResetSuccess = (data: InspectionRecord) => {
    setInspectionReportsData(data);
    notify.success("Enforcement summary updated");
  };

  const { mutate: updateInspectionRecord, isPending } =
    useUpdateInspectionRecord(handleOnUpdateSuccess);

  const { mutate: updateIRApproval } =
    useUpdateIRApproval(handleOnUpdateSuccess);

  const { mutate: resetInspectionRecord } =
    useResetInspectionRecord(handleOnResetSuccess);

  const onSubmitHandler = () => {
    resetInspectionRecord({
      inspectionId: inspectionData?.id ?? 0,
      inspectionRecordId: inspectionReportsData?.id ?? 0,
      resetPayload: {
        field_name: "date_issued",
      },
    });
    updateInspectionRecord({
      inspectionId: inspectionData?.id ?? 0,
      inspectionRecordId: inspectionReportsData?.id ?? 0,
      updateRecord: {
        field_name: "ir_progress",
        value: IRProgressEnum.FINALIZING_RECORD,
      },
    });
    updateIRApproval({
       inspectionId: inspectionData?.id ?? 0,
        inspectionRecordId: inspectionReportsData?.id ?? 0,
        approvalId: previousApprovalId ?? 0,
        approvalPayload: {
          field_name: "is_active",
          value: "false",
        },
    })
  };

  return (
    <>
      <ModalTitleBar title={"Reissue IR?"} />
      <DialogContent dividers>
        <Typography variant="body1" mb={2}>
          You are about to reopen Inspection Record:{" "}
          <b>{inspectionData?.ir_number}</b>.
        </Typography>
        <Typography variant="body2" mb={1.5}>
          Once reopened, you can make changes to the IR. You need to issue the
          IR again in order to close it.
        </Typography>
      </DialogContent>
      <ModalActions
        primaryActionButtonText={"Reopen"}
        isLoading={isPending}
        onPrimaryAction={onSubmitHandler}
      />
    </>
  );
};

export default ReopenIRModal;
