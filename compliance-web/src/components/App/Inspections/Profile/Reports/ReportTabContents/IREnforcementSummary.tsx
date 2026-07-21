import { Typography } from "@mui/material";
import IRBoxContainer from "./IRBoxContainer";
import { useReportStore } from "@/components/App/Inspections/Profile/Reports/reportStore";
import { useEffect, useState } from "react";
import { notify } from "@/store/snackbarStore";
import { useResetInspectionRecord, useUpdateInspectionRecord } from "@/hooks/useInspectionReports";
import { InspectionRecord } from "@/models/InspectionRecord";
import { DEFAULT_REPORT_TAB_CONTENT } from "@/utils/constants";
import { AxiosError } from "axios";
import { sanitizeHtml } from "@/utils/sanitizeHtml";

const IREnforcementSummary = () => {
  const {
    inspectionData,
    inspectionReportsData,
    enforcementSummary,
    isReportsReadOnly,
    setEnforcementSummary,
    setInspectionReportsData,
  } = useReportStore();

  const [isRegenerating, setIsRegenerating] = useState(false);

  useEffect(() => {
    setEnforcementSummary(inspectionReportsData?.enforcement_summary ?? "");
  }, [inspectionReportsData, setEnforcementSummary]);

  const handleOnSuccess = (data: InspectionRecord) => {
    setInspectionReportsData(data);
    setIsRegenerating(false); 
    notify.success("Enforcement summary updated");
  };

   const handleOnError = (error: AxiosError) => {
    setIsRegenerating(false);
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      notify.error("Request timed out. Please try again or contact support if the issue persists.");
    } else {
      const errorData = error.response?.data as { message?: string } | undefined;
      notify.error(`Failed to update Enforcement Summary. ${errorData?.message || error.message}`);
    }
  };

  const { mutate: updateInspectionRecord, isPending: isSaving } =
    useUpdateInspectionRecord(handleOnSuccess);

  const handleSaveEnforcementSummary = (editorValue: string) => {
    updateInspectionRecord({
      inspectionId: inspectionData?.id ?? 0,
      inspectionRecordId: inspectionReportsData?.id ?? 0,
      updateRecord: {
        field_name: "enforcement_summary",
        value: editorValue,
      },
    });
  };

  const { mutate: resetInspectionRecord } =
    useResetInspectionRecord(handleOnSuccess);

  const handleResetEnforcementSummary = () => {
    setIsRegenerating(true); 
    resetInspectionRecord(
      {
      inspectionId: inspectionData?.id ?? 0,
      inspectionRecordId: inspectionReportsData?.id ?? 0,
      resetPayload: {
        field_name: "enforcement_summary",
      },
    }, {
        onError: handleOnError,
      }
  );
  };

  return (
    <IRBoxContainer
      title="Enforcement Summary"
      defaultValue={enforcementSummary}
      onEditSubmit={!isReportsReadOnly ? handleSaveEnforcementSummary : undefined}
      onReset={!isReportsReadOnly ? handleResetEnforcementSummary : undefined}
      isResetting={isRegenerating}
      isSaving={isSaving}
    >
      <Typography
        variant="body1"
        component={"div"}
        className="editor-content"
        dangerouslySetInnerHTML={{ __html: sanitizeHtml(enforcementSummary || DEFAULT_REPORT_TAB_CONTENT) }}
      />
    </IRBoxContainer>
  );
};

export default IREnforcementSummary;
