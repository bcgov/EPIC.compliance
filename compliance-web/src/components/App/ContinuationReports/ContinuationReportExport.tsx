import { FileDownloadRounded } from "@mui/icons-material";
import { Button, CircularProgress } from "@mui/material";
import { downloadFile } from "@/utils/appUtils";
import dateUtils from "@/utils/dateUtils";
import { useContinuationReportExport } from "@/hooks/useContinuationReports";
import { useParams } from "@tanstack/react-router";

export default function ContinuationReportExport() {
  const params = useParams({ strict: false });
  const inspectionNumber = params?.inspectionNumber;
  const caseFileNumber = params?.caseFileNumber;

  const { mutate: downloadContinuationReport, isPending } =
    useContinuationReportExport((data) => {
      downloadFile(
        data,
        `continuation-reports-${dateUtils.formatDate(new Date().toISOString(), "YYYY-MM-DD-HH-mm-ss")}.pdf`,
      );
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
          inspection_number: inspectionNumber!,
        })
      }
      disabled={isPending}
    >
      {isPending ? "Exporting..." : "Export as PDF"}
    </Button>
  );
}
