import { Typography } from "@mui/material";
import IRBoxContainer from "./IRBoxContainer";
import { useReportStore } from "@/components/App/Inspections/Profile/Reports/reportStore";
import { useEffect } from "react";
import { notify } from "@/store/snackbarStore";
import { useUpdateInspectionRecord } from "@/hooks/useInspectionReports";
import { InspectionRecord } from "@/models/InspectionRecord";
import { DEFAULT_REPORT_TAB_CONTENT } from "@/utils/constants";

const ActionsRequired = () => {
  const {
    inspectionData,
    inspectionReportsData,
    actionsRequired,
    proponentLabel,
    isReportsReadOnly,
    setActionsRequired,
    setInspectionReportsData,
  } = useReportStore();

  useEffect(() => {
    setActionsRequired(inspectionReportsData?.action_required_by_rp ?? "");
  }, [inspectionReportsData, setActionsRequired]);

  const handleOnSuccess = (data: InspectionRecord) => {
    setInspectionReportsData(data);
    notify.success("Actions required updated");
  };

  const { mutate: updateInspectionRecord, isPending: isSaving } =
    useUpdateInspectionRecord(handleOnSuccess);

  const handleSaveActionsRequired = (editorValue: string) => {
    updateInspectionRecord({
      inspectionId: inspectionData?.id ?? 0,
      inspectionRecordId: inspectionReportsData?.id ?? 0,
      updateRecord: {
        field_name: "action_required_by_rp",
        value: editorValue,
      },
    });
  };

  return (
    <IRBoxContainer
      title={`Actions Required by ${proponentLabel} and Comments`}
      defaultValue={actionsRequired}
      onEditSubmit={!isReportsReadOnly ? handleSaveActionsRequired : undefined}
      isSaving={isSaving}
    >
      <Typography
        variant="body1"
        component={"div"}
        className="editor-content"
        dangerouslySetInnerHTML={{
          __html: actionsRequired || DEFAULT_REPORT_TAB_CONTENT,
        }}
      />
    </IRBoxContainer>
  );
};

export default ActionsRequired;
