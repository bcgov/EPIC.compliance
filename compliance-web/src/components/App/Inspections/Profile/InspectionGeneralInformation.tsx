import React, { useMemo } from "react";
import { EditRounded } from "@mui/icons-material";
import { Box, Button, Typography } from "@mui/material";
import FileProfileProperty from "@/components/App/FileProfileProperty";
import { Inspection } from "@/models/Inspection";
import dateUtils from "@/utils/dateUtils";
import { useMenuStore } from "@/store/menuStore";

interface InspectionGeneralInformationProps {
  inspectionData: Inspection;
  onEdit: () => void;
  allowEdit?: boolean;
}

const InspectionGeneralInformation: React.FC<
  InspectionGeneralInformationProps
> = ({ inspectionData, onEdit, allowEdit }) => {
  const { appHeaderHeight } = useMenuStore();

  const inAttendance = useMemo(() => {
    return inspectionData.inspectionAttendances
      ?.map((attendance) => {
        if (attendance.data) {
          if (Array.isArray(attendance.data)) {
            return attendance.data.map((item) => item.name).join(", ");
          } else if (typeof attendance.data === "string") {
            return attendance.data;
          }
        } else {
          return attendance.attendance_option.name;
        }
      })
      .join(", ");
  }, [inspectionData.inspectionAttendances]);

  const properties = [
    { name: "Project", value: inspectionData.case_file?.project?.name },
    { name: "Project Description", value: inspectionData.project_description },
    {
      name: "Location Description",
      value: inspectionData.location_description,
    },
    { name: "UTM", value: inspectionData.utm },
    { name: "Primary", value: inspectionData.primary_officer?.name },
    { name: "Initiation", value: inspectionData.initiation?.name },
    {
      name: "Type",
      value: inspectionData.types?.map((type) => type.name).join(", "),
    },
    {
      name: "Dates",
      value: `${dateUtils.formatDate(inspectionData.start_date)} — ${dateUtils.formatDate(inspectionData.end_date)}`,
    },
    { name: "IR Status", value: inspectionData.ir_status?.name },
    { name: "Project Status", value: inspectionData.project_status?.name },
    { name: "In Attendance", value: inAttendance },
  ];

  return (
    <Box
      display={"flex"}
      flexGrow={1}
      flexDirection={"column"}
      width={"75%"}
      height={`calc(100vh - ${appHeaderHeight + 158}px)`} // 158px is the height of the FileProfileHeader and the padding
      overflow={"auto"}
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
    </Box>
  );
};

export default InspectionGeneralInformation;
