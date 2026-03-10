import { FileDownloadRounded } from "@mui/icons-material";
import { Button, CircularProgress } from "@mui/material";
import { downloadFile } from "@/utils/appUtils";
import { useContinuationReportExport } from "@/hooks/useContinuationReports";
import { useParams } from "@tanstack/react-router";
import { useCaseFileByNumber } from "@/hooks/useCaseFiles";
import { useProjectAbbreviationById } from "@/hooks/useProjects";
import { useInspectionByNumber } from "@/hooks/useInspections";
import { useComplaintByNumber } from "@/hooks/useComplaints";

export default function ContinuationReportExport() {
  const params = useParams({ strict: false });

  const caseFileNumberFromParams = params?.caseFileNumber;
  const inspectionNumberFromParams = params?.inspectionNumber;
  const compliantNumberFromParams = params?.complaintNumber;

  const { data: caseFileData } = useCaseFileByNumber(caseFileNumberFromParams!);
  const { data: inspectionData } = useInspectionByNumber(
    inspectionNumberFromParams!,
  );
  const { data: complaintData } = useComplaintByNumber(
    compliantNumberFromParams!,
  );

  const caseFileNumber =
    caseFileData?.case_file_number ||
    inspectionData?.case_file?.case_file_number ||
    complaintData?.case_file?.case_file_number;

  const projectId =
    caseFileData?.project_id ||
    inspectionData?.case_file?.project?.id ||
    complaintData?.case_file?.project?.id;

  const { data: projectAbbreviation } = useProjectAbbreviationById(projectId!);

  const { mutate: downloadContinuationReport, isPending } =
    useContinuationReportExport((data) => {
      downloadFile(data, `${projectAbbreviation || "UNPRVD"}_${caseFileNumber}_CREP.pdf`);
    });

  return (
    <Button
      variant="text"
      size="small"
      startIcon={
        isPending ? <CircularProgress size={16} /> : <FileDownloadRounded />
      }
      sx={{ ml: -2 }}
      onClick={() =>
        downloadContinuationReport({
          case_file_number: caseFileNumber!,
        })
      }
      disabled={isPending}
    >
      {isPending ? "Exporting..." : "Export as PDF"}
    </Button>
  );
}
