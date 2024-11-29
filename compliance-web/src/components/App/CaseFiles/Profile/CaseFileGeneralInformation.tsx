import dateUtils from "@/utils/dateUtils";
import { EditRounded } from "@mui/icons-material";
import { Box, Button, Stack, Typography } from "@mui/material";
import FileProfileProperty from "@/components/App/FileProfileProperty";
import { CaseFile } from "@/models/CaseFile";
import CaseFileInspectionsTable from "./CaseFileInspectionsTable";
import CaseFileComplaintsTable from "./CaseFileComplaintsTable";
import { formatAuthorization } from "@/utils/appUtils";

interface CaseFileGeneralInformationProps {
  caseFileData: CaseFile;
  onEdit: () => void;
  allowEdit?: boolean;
}

const CaseFileGeneralInformation: React.FC<CaseFileGeneralInformationProps> = ({
  caseFileData,
  onEdit,
  allowEdit,
}) => {
  return (
    <Box display={"flex"} flexGrow={1} flexDirection={"column"} width={"60%"}>
      <Box display={"flex"} justifyContent={"space-between"} my={3}>
        <Typography variant="h6">General Information</Typography>
        {allowEdit && (
          <Button
            variant="text"
            color="primary"
            size="small"
            onClick={onEdit}
            startIcon={<EditRounded />}
          >
            Edit
          </Button>
        )}
      </Box>
      <Box display={"flex"} gap={8}>
        <Stack flex={1}>
          <FileProfileProperty
            propertyName="Project"
            propertyValue={caseFileData.project.name}
            size="small"
          />
          <FileProfileProperty
            propertyName="Authorization"
            propertyValue={formatAuthorization(caseFileData.authorization)}
            size="small"
          />
          <FileProfileProperty
            propertyName="Certificate Holder"
            propertyValue={caseFileData.regulated_party}
            size="small"
          />
          <FileProfileProperty
            propertyName="Type"
            propertyValue={caseFileData.type}
            size="small"
          />
          <FileProfileProperty
            propertyName="Subtype"
            propertyValue={caseFileData.sub_type}
            size="small"
          />
        </Stack>
        <Stack flex={1}>
          <FileProfileProperty
            propertyName="Initiation"
            propertyValue={caseFileData.initiation.name}
            size="small"
          />
          <FileProfileProperty
            propertyName="Primary"
            propertyValue={caseFileData.primary_officer?.name}
            size="small"
          />
          <FileProfileProperty
            propertyName="Other Assigned Officers"
            propertyValue={caseFileData.officers
              ?.map((officer) => officer.name)
              .join(", ")}
            size="small"
          />
          <FileProfileProperty
            propertyName="Date Created"
            propertyValue={dateUtils.formatDate(caseFileData.date_created)}
            size="small"
          />
        </Stack>
      </Box>
      <FileProfileProperty
        propertyName="Project Description"
        propertyValue={caseFileData.project_description}
        size="small"
      />
      <CaseFileComplaintsTable caseFileId={caseFileData.id} />
      <CaseFileInspectionsTable caseFileId={caseFileData.id} />
    </Box>
  );
};

export default CaseFileGeneralInformation;
