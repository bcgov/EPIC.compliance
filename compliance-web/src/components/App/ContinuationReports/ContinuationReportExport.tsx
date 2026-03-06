import { FileDownloadRounded } from "@mui/icons-material";
import { Button, CircularProgress } from "@mui/material";
import { downloadFile } from "@/utils/appUtils";
import { useContinuationReportExport } from "@/hooks/useContinuationReports";
import { useParams } from "@tanstack/react-router";
import { useCaseFileByNumber } from "@/hooks/useCaseFiles";
import { useProjectAbbreviationById } from "@/hooks/useProjects";

export default function ContinuationReportExport() {
  const params = useParams({ strict: false });
  const caseFileNumber = params?.caseFileNumber;
  const { data: caseFileData } = useCaseFileByNumber(caseFileNumber!);
  const { data: projectAbbreviation } = useProjectAbbreviationById(caseFileData?.project_id);


  const { mutate: downloadContinuationReport, isPending } =
    useContinuationReportExport((data) => {
      downloadFile(
        data,
        `${projectAbbreviation}_${caseFileNumber}_CREP.pdf`,
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
        })
      }
      disabled={isPending}
    >
      {isPending ? "Exporting..." : "Export as PDF"}
    </Button>
  );
}
