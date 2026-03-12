import React, { useEffect, useMemo, useState } from "react";
import { Inspection } from "@/models/Inspection";
import {
  Box,
  Button,
  CircularProgress,
  FormControlLabel,
  Radio,
  RadioGroup,
  Typography,
} from "@mui/material";
import ReportTabs from "./Reports/ReportTabs";
import {
  useCreateInspectionRecord,
  useFetchIRApprovals,
  useInspectionReportsData,
} from "@/hooks/useInspectionReports";
import { useReportStore } from "./Reports/reportStore";
import { notify } from "@/store/snackbarStore";
import { useQueryClient } from "@tanstack/react-query";
import { useIRStatusesData } from "@/hooks/useInspections";
import { IR_STATUS } from "@/utils/constants";
import DynamicHeightBox from "@/components/Shared/DynamicHeightBox";

interface InspectionReportsProps {
  inspectionData: Inspection;
}

const InspectionReports: React.FC<InspectionReportsProps> = ({
  inspectionData,
}) => {
  const queryClient = useQueryClient();
  const { setInspectionReportsData, setQueryClient, setIRApprovalsData } =
    useReportStore();
  const [reportVersion, setReportVersion] = useState<string>("");

  useEffect(() => {
    if (inspectionData.is_history) {
      setReportVersion(IR_STATUS.FINAL.toString());
    }
  }, [inspectionData.is_history]);

  const isReportsAllowed = useMemo(
    () => inspectionData?.inspection_status?.toLowerCase() === "open",
    [inspectionData]
  );

  const { data: irStatusesData } = useIRStatusesData();
  const { data: inspectionReportsData, isLoading } = useInspectionReportsData(
    inspectionData.id
  );
  const { data: irApprovalsData } = useFetchIRApprovals(
    inspectionData.id,
    inspectionReportsData?.id ?? 0
  );

  useEffect(() => {
    if (inspectionReportsData) {
      setQueryClient(queryClient);
      setInspectionReportsData(inspectionReportsData);
      setIRApprovalsData(irApprovalsData ?? []);
    }
  }, [
    inspectionReportsData,
    queryClient,
    irApprovalsData,
    setInspectionReportsData,
    setQueryClient,
    setIRApprovalsData,
  ]);

  const handleReportVersionChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setReportVersion(event.target.value);
  };

  const handleOnSuccess = () => {
    notify.success("Inspection record created");
    queryClient.invalidateQueries({
      queryKey: ["inspection-reports", inspectionData.id],
    });
  };

  const { mutate: createInspectionRecord, isPending } =
    useCreateInspectionRecord(handleOnSuccess);

  const handleProceedToReport = () => {
    createInspectionRecord({
      inspectionId: inspectionData.id,
      inspectionRecordType: {
        ir_status: parseInt(reportVersion),
      },
    });
  };

  return isLoading ? (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100%",
      }}
    >
      <CircularProgress />
    </Box>
  ) : inspectionReportsData?.id ? (
    <DynamicHeightBox
      display={"flex"}
      flexGrow={1}
      flexDirection={"column"}
      overflow={"auto"}
      bottomOffset={20}
    >
      <ReportTabs />
    </DynamicHeightBox>
  ) : isReportsAllowed ? (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        py: 3,
        maxWidth: "600px",
      }}
    >
      {!inspectionData.is_history && (
        <>
          <Typography variant="h6" mb={2}>
            Select Report Version
          </Typography>

          <Typography variant="body2" mb={2}>
            Choose the IR report version you want to work on.
          </Typography>

          <RadioGroup
            value={reportVersion}
            onChange={handleReportVersionChange}
            sx={{ mb: 3 }}
          >
            {irStatusesData?.map((irStatus) => (
              <FormControlLabel
                key={irStatus.id}
                value={irStatus.id}
                control={<Radio />}
                label={`${irStatus.name} Inspection Record`}
                sx={{ mb: 0.5 }}
              />
            ))}
          </RadioGroup>
        </>
      )}

      <Button
        onClick={handleProceedToReport}
        disabled={!reportVersion || isPending}
        sx={{
          width: "fit-content",
        }}
      >
        Proceed to {`${inspectionData.is_history ? "Final" : ""} Report`}
      </Button>
    </Box>
  ) : (
    <Typography variant="subtitle2" py={3}>
      This inspection is closed.
    </Typography>
  );
};

export default InspectionReports;
