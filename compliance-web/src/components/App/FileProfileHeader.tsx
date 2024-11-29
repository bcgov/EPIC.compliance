import { ExpandMoreRounded } from "@mui/icons-material";
import { Box, Typography, Chip, Button } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import BreadcrumbsNav, {
  BreadcrumbItem,
} from "@/components/Shared/BreadcrumbsNav";
import CaseFileCreateInspection from "@/components/App/CaseFiles/Profile/CaseFileCreateInspection";
import CaseFileCreateComplaint from "@/components/App/CaseFiles/Profile/CaseFileCreateComplaint";
interface FileProfileHeaderProps {
  fileNumber: string;
  status: string;
  breadcrumbs: BreadcrumbItem[];
  showInspectionComplaintButton?: boolean;
}

const FileProfileHeader: React.FC<FileProfileHeaderProps> = ({
  fileNumber,
  status,
  breadcrumbs,
  showInspectionComplaintButton = false,
}) => {
  return (
    <Box
      display={"flex"}
      justifyContent={"space-between"}
      bgcolor={BCDesignTokens.surfaceColorBackgroundLightGray}
      padding={"1.5rem 2.5rem 1.5rem 3.75rem"}
    >
      <Box display={"flex"} flexDirection={"column"} gap={1}>
        <BreadcrumbsNav items={breadcrumbs} />
        <Box display={"flex"} gap={1} alignItems={"center"}>
          <Typography variant="h3">{fileNumber}</Typography>
          <Chip
            label={status}
            color={status?.toLowerCase() === "open" ? "success" : "error"}
            variant="outlined"
            size="small"
          />
        </Box>
      </Box>
      <Box display={"flex"} gap={1}>
        {showInspectionComplaintButton && (
          <>
            <CaseFileCreateInspection />
            <CaseFileCreateComplaint />
          </>
        )}
        <Button
          variant="text"
          size="small"
          onClick={() => {}}
          startIcon={<ExpandMoreRounded />}
        >
          Actions
        </Button>
      </Box>
    </Box>
  );
};

export default FileProfileHeader;
