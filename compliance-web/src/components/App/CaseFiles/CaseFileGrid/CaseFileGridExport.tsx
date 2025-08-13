import { FileDownloadRounded } from "@mui/icons-material";
import { Button, CircularProgress } from "@mui/material";
import { useCaseFilesExport } from "@/hooks/useCaseFiles";
import { CaseFileGridQueryParams } from "@/models/CaseFile";
import { downloadFile } from "@/utils/appUtils";
import dateUtils from "@/utils/dateUtils";

interface CaseFileGridExportProps {
  queryParams: CaseFileGridQueryParams;
}

export default function CaseFileGridExport({
  queryParams,
}: CaseFileGridExportProps) {
  const { mutate: downloadCaseFilesExport, isPending } = useCaseFilesExport(
    (data) => {
      downloadFile(
        data,
        `case-files-${dateUtils.formatDate(new Date().toISOString(), "YYYY-MM-DD-HH-mm-ss")}.xlsx`
      );
    }
  );

  return (
    <Button
      variant="text"
      size="small"
      startIcon={isPending ? <CircularProgress size={16} /> : <FileDownloadRounded />}
      sx={{ ml: -2 }}
      onClick={() => downloadCaseFilesExport(queryParams)}
      disabled={isPending}
    >
      {isPending ? "Exporting..." : "Export as Excel"}
    </Button>
  );
}
