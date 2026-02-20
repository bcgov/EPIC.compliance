import FileProfileProperty from "@/components/App/FileProfileProperty";
import { Inspection } from "@/models/Inspection";
import { CaseFile } from "@/models/CaseFile";
import dateUtils from "@/utils/dateUtils";
import { EditRounded } from "@mui/icons-material";
import { Box, Button, Typography } from "@mui/material";
import React, { useMemo } from "react";
import { formatInAttendance } from "../InspectionFormUtils";
import DynamicHeightBox from "@/components/Shared/DynamicHeightBox";

interface InspectionGeneralInformationProps {
  inspectionData: Inspection;
  caseFileData: CaseFile;
  onEdit: () => void;
  allowEdit?: boolean;
}

const InspectionGeneralInformation: React.FC<
  InspectionGeneralInformationProps
> = ({ inspectionData, caseFileData, onEdit, allowEdit }) => {
  const inAttendance = useMemo(
    () => formatInAttendance(inspectionData, caseFileData),
    [inspectionData, caseFileData]
  );

  const dateRange = useMemo(() => {
    const startDate = dateUtils.formatDate(inspectionData.start_date);
    const endDate = dateUtils.formatDate(inspectionData.end_date);
    if (startDate === endDate) {
      return startDate;
    }
    return `${startDate} — ${endDate}`;
  }, [inspectionData.start_date, inspectionData.end_date]);

  const properties = [
    { name: "Project", value: inspectionData.case_file?.project?.name },
    { name: "Project Description", value: inspectionData.project_description },
    {
      name: "Location Description",
      value: inspectionData.location_description,
    },
    { name: "UTM", value: inspectionData.utm },
    { name: "Project Components / Area Inspected", value: inspectionData.area_inspected },
    { name: "Primary", value: inspectionData.primary_officer?.name },
    { name: "Initiation", value: inspectionData.initiation?.name },
    {
      name: "Type",
      value: inspectionData.types?.map((type) => type.name).join(", "),
    },
    {
      name: "Dates",
      value: dateRange,
    },
    { name: "Project Status", value: inspectionData.project_status?.name },
    { name: "In Attendance", value: inAttendance },
  ];

  return (
    <DynamicHeightBox
      display={"flex"}
      flexGrow={1}
      flexDirection={"column"}
      overflow={"auto"}
      bottomOffset={20}
    >
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
      <Box display={"flex"} flexDirection={"column"}>
        {properties.map((property) => (
          <FileProfileProperty
            key={property.name}
            propertyName={property.name}
            propertyValue={property.value}
          />
        ))}
      </Box>
    </DynamicHeightBox>
  );
};

export default InspectionGeneralInformation;
