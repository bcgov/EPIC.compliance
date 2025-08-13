import { FileDownloadRounded } from "@mui/icons-material";
import { Button, CircularProgress } from "@mui/material";
import { useInspectionRequirementExport } from "@/hooks/useInspectionRequirementsGrid";
import { InspectionRequirementGridQueryParams } from "@/models/InspectionRequirementGrid";
import { downloadFile } from "@/utils/appUtils";
import dateUtils from "@/utils/dateUtils";

interface RequirementsGridExportProps {
  queryParams: InspectionRequirementGridQueryParams;
}

export default function RequirementsGridExport({
  queryParams,
}: RequirementsGridExportProps) {
  const { mutate: downloadRequirementExport, isPending } = useInspectionRequirementExport(
    (data) => {
      downloadFile(
        data,
        `requirements-${dateUtils.formatDate(new Date().toISOString(), "YYYY-MM-DD-HH-mm-ss")}.xlsx`
      );
    }
  );

  return (
    <Button
      variant="text"
      size="small"
      startIcon={isPending ? <CircularProgress size={16} /> : <FileDownloadRounded />}
      sx={{ ml: -2 }}
      onClick={() => downloadRequirementExport(queryParams)}
      disabled={isPending}
    >
      {isPending ? "Exporting..." : "Export as Excel"}
    </Button>
  );
}
