import { Typography } from "@mui/material";
import IRBoxContainer from "./IRBoxContainer";
import { useReportStore } from "@/components/App/Inspections/Profile/Reports/reportStore";
import { useEffect, useState } from "react";
import {
  useResetInspectionRecord,
  useUpdateInspectionRecord,
} from "@/hooks/useInspectionReports";
import { InspectionRecord } from "@/models/InspectionRecord";
import { notify } from "@/store/snackbarStore";
import { IR_STATUS } from "@/utils/constants";
import { AxiosError } from "axios";

const InspectionSummary = () => {
  const {
    inspectionData,
    inspectionScope,
    preliminaryReviewDetails,
    findingsStatement,
    inspectionReportsData,
    isReportsReadOnly,
    setInspectionScope,
    setPreliminaryReviewDetails,
    setFindingsStatement,
    setInspectionReportsData,
  } = useReportStore();

  const [isFindingsStatementChanged, setIsFindingsStatementChanged] =
    useState(false);
  const [
    isPreliminaryReviewDetailsChanged,
    setIsPreliminaryReviewDetailsChanged,
  ] = useState(false);
  const [isFinalReport, setIsFinalReport] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);

  useEffect(() => {
    setInspectionScope(inspectionReportsData?.inspection_scope ?? "");
    setPreliminaryReviewDetails(
      inspectionReportsData?.preliminary_review_details ?? ""
    );
    setFindingsStatement(inspectionReportsData?.finding_statement ?? "");
    setIsFindingsStatementChanged(
      inspectionReportsData?.field_change_info?.finding_statement_changed ??
      false
    );
    setIsPreliminaryReviewDetailsChanged(
      inspectionReportsData?.field_change_info
        ?.preliminary_review_details_changed ?? false
    );
    setIsFinalReport(inspectionReportsData?.ir_status_id === IR_STATUS.FINAL);
  }, [
    inspectionReportsData,
    setFindingsStatement,
    setInspectionScope,
    setPreliminaryReviewDetails,
  ]);

  const handleOnSuccess = (data: InspectionRecord) => {
    setInspectionReportsData(data);
    setIsRegenerating(false);
    notify.success("Inspection summary updated");
  };

  const handleOnError = (error: AxiosError) => {
    setIsRegenerating(false);
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      notify.error("Request timed out. Please try again or contact support if the issue persists.");
    } else {
      notify.error("Failed to update Inspection Summary");
    }
  };

  const { mutate: updateInspectionRecord, isPending: isSaving } =
    useUpdateInspectionRecord(handleOnSuccess);

  const { mutate: resetInspectionRecord } =
    useResetInspectionRecord(handleOnSuccess);

  const handleSaveInspectionSummary = (editorValue: string, field: string) => {
    updateInspectionRecord({
      inspectionId: inspectionData?.id ?? 0,
      inspectionRecordId: inspectionReportsData?.id ?? 0,
      updateRecord: {
        field_name: field,
        value: editorValue,
      },
    });
  };

  const handleResetInspectionSummary = (fieldName: string) => {
    setIsRegenerating(true);
    resetInspectionRecord(
      {
        inspectionId: inspectionData?.id ?? 0,
        inspectionRecordId: inspectionReportsData?.id ?? 0,
        resetPayload: {
          field_name: fieldName,
        },
      },
      {
        onError: handleOnError,
      });
  };

  return (
    <>
      <IRBoxContainer
        title="Inspection Scope"
        sx={{ mb: 1 }}
        defaultValue={inspectionScope}
        onEditSubmit={
          !isReportsReadOnly
            ? (editorValue) =>
              handleSaveInspectionSummary(editorValue, "inspection_scope")
            : undefined
        }
        onReset={
          !isReportsReadOnly
            ? () => handleResetInspectionSummary("inspection_scope")
            : undefined
        }
        isSaving={isSaving}
      >
        <Typography
          variant="body1"
          component={"div"}
          className="editor-content"
          dangerouslySetInnerHTML={{ __html: inspectionScope || "" }}
        />
      </IRBoxContainer>
      {isFinalReport && preliminaryReviewDetails && (
        <IRBoxContainer
          title="Preliminary Review Details"
          sx={{ mb: 1 }}
          defaultValue={preliminaryReviewDetails}
          onEditSubmit={
            !isReportsReadOnly
              ? (editorValue) =>
                handleSaveInspectionSummary(
                  editorValue,
                  "preliminary_review_details"
                )
              : undefined
          }
          onReset={
            !isReportsReadOnly && isPreliminaryReviewDetailsChanged
              ? () => handleResetInspectionSummary("preliminary_review_details")
              : undefined
          }
          isSaving={isSaving}
        >
          <Typography
            variant="body1"
            component={"div"}
            className="editor-content"
            dangerouslySetInnerHTML={{ __html: preliminaryReviewDetails || "" }}
          />
        </IRBoxContainer>
      )}
      <IRBoxContainer
        title="Findings Statement"
        defaultValue={findingsStatement}
        onEditSubmit={
          !isReportsReadOnly
            ? (editorValue) =>
              handleSaveInspectionSummary(editorValue, "finding_statement")
            : undefined
        }
        onReset={
          !isReportsReadOnly && isFindingsStatementChanged
            ? () => handleResetInspectionSummary("finding_statement")
            : undefined
        }
        isResetting={isRegenerating}
        isSaving={isSaving}
      >
        <Typography
          variant="body1"
          component={"div"}
          className="editor-content"
          dangerouslySetInnerHTML={{ __html: findingsStatement || "" }}
        />
      </IRBoxContainer>
    </>
  );
};

export default InspectionSummary;
