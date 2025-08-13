import { FileDownloadRounded } from "@mui/icons-material";
import { Button, CircularProgress } from "@mui/material";
import { useComplaintsExport } from "@/hooks/useComplaints";
import { ComplaintGridQueryParams } from "@/models/Complaint";
import { downloadFile } from "@/utils/appUtils";
import dateUtils from "@/utils/dateUtils";

interface ComplaintsGridExportProps {
  queryParams: ComplaintGridQueryParams;
}

export default function ComplaintsGridExport({
  queryParams,
}: ComplaintsGridExportProps) {
  const { mutate: downloadComplaintsExport, isPending } = useComplaintsExport(
    (data) => {
      downloadFile(
        data,
        `complaints-${dateUtils.formatDate(new Date().toISOString(), "YYYY-MM-DD-HH-mm-ss")}.xlsx`
      );
    }
  );

  return (
    <Button
      variant="text"
      size="small"
      startIcon={isPending ? <CircularProgress size={16} /> : <FileDownloadRounded />}
      sx={{ ml: -2 }}
      onClick={() => downloadComplaintsExport(queryParams)}
      disabled={isPending}
    >
      {isPending ? "Exporting..." : "Export as Excel"}
    </Button>
  );
} 
