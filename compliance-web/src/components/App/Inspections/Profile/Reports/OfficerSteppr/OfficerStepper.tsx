import { Box, Step, StepLabel, Stepper, Collapse, IconButton } from "@mui/material";
import { ExpandLessRounded, ChevronRight } from "@mui/icons-material";
import { BCDesignTokens } from "epic.theme";
import { useMemo, useState } from "react";
import PreliminaryReview from "./PreliminaryReview";
import RegPartyResponse from "./RegPartyResponse";
import IRVersionSelect from "./IRVersionSelect";
import {
  useUpdateInspectionRecord,
  useUpdateIRApproval,
  useUpdateIRReportToFinal,
} from "@/hooks/useInspectionReports";
import { useReportStore } from "../reportStore";
import {
  InspectionRecordApprovalPayload,
  IRApproval,
} from "@/models/IRApproval";
import { notify } from "@/store/snackbarStore";
import { InspectionRecord } from "@/models/InspectionRecord";
import { IRProgressEnum } from "@/utils/constants";
import IssuanceDate from "./IssuanceDate";
import { useQueryClient } from "@tanstack/react-query";

const preliminarySteps = [
  "Preliminary Review",
  "Response from Regulated Party",
  "Select IR version",
];

const finalSteps = ["IR Issuance Date"];

export default function OfficerStepper() {
  const {
    inspectionData,
    inspectionReportsData,
    irApprovalsData,
    setIRApprovalsData,
    setInspectionReportsData,
  } = useReportStore();
  const [activeStep, setActiveStep] = useState(0);
  const [isContentExpanded, setIsContentExpanded] = useState(true);
  const queryClient = useQueryClient();

  const isFinalReportStep = useMemo(() => {
    return (
      inspectionReportsData?.ir_progress?.id === IRProgressEnum.FINAL_APPROVED
    );
  }, [inspectionReportsData]);

  const handleNext = (isRefreshReport: boolean = false) => {
    if (activeStep !== preliminarySteps.length - 1) {
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
    }
    if (inspectionData?.id && isRefreshReport) {
      queryClient.invalidateQueries({
        queryKey: ["inspection-reports", inspectionData.id],
      });
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const onSuccessApproval = (data: IRApproval) => {
    setIRApprovalsData([data]);
    notify.success("Inspection record approval updated");
  };

  const onSuccessIRReport = (data: InspectionRecord) => {
    setInspectionReportsData(data);
    notify.success("Inspection record updated");
    handleNext();
  };

  const { mutateAsync: updateIRApprovalStatusAsync,  isPending: isApprovalPending } =
    useUpdateIRApproval(onSuccessApproval);

  const { mutate: updateIRReportToFinal, isPending: isReportFinalPending } =
    useUpdateIRReportToFinal(onSuccessIRReport);

  const { mutate: updateInspectionRecord, isPending: isInspectionRecordPending } =
    useUpdateInspectionRecord(onSuccessIRReport);

  const onUpdateIRApprovalStep = async (
    approvalPayloads: InspectionRecordApprovalPayload[]
  ) => {
    for (const approvalPayload of approvalPayloads) {
      await updateIRApprovalStatusAsync({
        inspectionId: inspectionData?.id ?? 0,
        inspectionRecordId: inspectionReportsData?.id ?? 0,
        approvalId: irApprovalsData?.[0]?.id ?? 0,
        approvalPayload,
      });
    }
    // doing this to avoid going to the next step before all the updates are done
    handleNext(true);
  };

  const onUpdateIRReport = (type: "final" | "preliminary") => {
    if (type === "final") {
      updateIRReportToFinal({
        inspectionId: inspectionData?.id ?? 0,
        inspectionRecordId: inspectionReportsData?.id ?? 0,
      });
    } else {
      updateInspectionRecord({
        inspectionId: inspectionData?.id ?? 0,
        inspectionRecordId: inspectionReportsData?.id ?? 0,
        updateRecord: {
          field_name: "ir_progress",
          value: IRProgressEnum.PRELIMINARY_DRAFTING,
        },
      });
    }
  };

  const toggleContentExpansion = () => {
    setIsContentExpanded(prev => !prev);
  };

  return (
    <Box
      sx={{
        mt: 1,
        mb: 2,
        border: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
        borderRadius: 1,
      }}
    >
      <Box
        onClick={toggleContentExpansion}
        sx={{
          cursor: "pointer",
          position: "relative",
          "&:hover": {
            backgroundColor: BCDesignTokens.surfaceColorBackgroundLightBlue,
          },
        }}
      >
        <Stepper
          activeStep={activeStep}
          sx={{
            backgroundColor: BCDesignTokens.surfaceColorBackgroundLightGray,
            p: 2,
            borderBottom: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
            fontWeight: 600,
            pl: "3rem",
          }}
        >
        {(isFinalReportStep ? finalSteps : preliminarySteps).map((label) => {
          return (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          );
        })}
        </Stepper>
        
        {/* Expand/Collapse Icon */}
        <IconButton 
          size="small"
          disableRipple
          sx={{ 
            position: "absolute",
            top: "50%",
            left: "1rem",
            transform: "translateY(-50%)",
            color: BCDesignTokens.typographyColorSecondary,
            "&:hover": {
              backgroundColor: "transparent",
            },
          }}
        >
          {isContentExpanded ? <ExpandLessRounded /> : <ChevronRight />}
        </IconButton>
      </Box>
      
      <Collapse in={isContentExpanded}>
        <Box sx={{ p: 2 }}>
        {activeStep === 0 && (
          <>
            {isFinalReportStep ? (
              <IssuanceDate />
            ) : (
              <PreliminaryReview
                onUpdateIRApprovalStep={onUpdateIRApprovalStep}
                nextStep={handleNext}
                isPending={isApprovalPending}
              />
            )}
          </>
        )}
        {activeStep === 1 && (
          <RegPartyResponse
            onUpdateIRApprovalStep={onUpdateIRApprovalStep}
            onNext={handleNext}
            onBack={handleBack}
            isPending={isApprovalPending}
          />
        )}
        {activeStep === 2 && (
          <IRVersionSelect
            onBack={handleBack}
            onUpdateIRReportToFinal={() => onUpdateIRReport("final")}
            onUpdateIRReportToPreliminary={() =>
              onUpdateIRReport("preliminary")
            }
            isPending={isReportFinalPending || isInspectionRecordPending}
          />
        )}
        </Box>
      </Collapse>
    </Box>
  );
}
