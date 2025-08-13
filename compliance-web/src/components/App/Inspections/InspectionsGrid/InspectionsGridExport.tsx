import { FileDownloadRounded } from "@mui/icons-material";
import { Button, CircularProgress } from "@mui/material";
import { useInspectionsExport } from "@/hooks/useInspections";
import { InspectionGridQueryParams } from "@/models/Inspection";
import { downloadFile } from "@/utils/appUtils";
import dateUtils from "@/utils/dateUtils";

interface InspectionsGridExportProps {
  queryParams: InspectionGridQueryParams;
}

export default function InspectionsGridExport({
  queryParams,
}: InspectionsGridExportProps) {
  const { mutate: downloadInspectionExport, isPending } = useInspectionsExport(
    (data) => {
      downloadFile(
        data,
        `inspections-${dateUtils.formatDate(new Date().toISOString(), "YYYY-MM-DD-HH-mm-ss")}.xlsx`
      );
    }
  );

  return (
    <Button
      variant="text"
      size="small"
      startIcon={isPending ? <CircularProgress size={16} /> : <FileDownloadRounded />}
      sx={{ ml: -2 }}
      onClick={() => downloadInspectionExport(queryParams)}
      disabled={isPending}
    >
      {isPending ? "Exporting..." : "Export as Excel"}
    </Button>
  );
}
