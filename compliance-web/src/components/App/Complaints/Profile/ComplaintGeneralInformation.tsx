import React from "react";
import { EditRounded } from "@mui/icons-material";
import { Box, Button, Typography } from "@mui/material";
import FileProfileProperty from "@/components/App/FileProfileProperty";
import dateUtils from "@/utils/dateUtils";
import { Complaint } from "@/models/Complaint";
import { useMenuStore } from "@/store/menuStore";
import {
  ComplaintSourceEnum,
  RequirementSourceEnum,
} from "@/components/App/Complaints/ComplaintFormUtils";

interface ComplaintGeneralInformationProps {
  complaintData: Complaint;
  onEdit: () => void;
  allowEdit?: boolean;
}

const ComplaintGeneralInformation: React.FC<
  ComplaintGeneralInformationProps
> = ({ complaintData, onEdit, allowEdit }) => {
  const { appHeaderHeight } = useMenuStore();

  const generalProperties = [
    { name: "Project Name", value: complaintData.case_file?.project?.name },
    {
      name: "Concern Description",
      value: complaintData.concern_description,
    },
    {
      name: "Location Description",
      value: complaintData.location_description,
    },
    { name: "Primary", value: complaintData.primary_officer?.name },
    {
      name: "Date Received",
      value: dateUtils.formatDate(complaintData.date_received),
    },
  ];

  if (complaintData.requirement_source) {
    generalProperties.push({
      name: "Requirement Source",
      value: complaintData.requirement_source.name,
    });
    switch (complaintData.requirement_source.id) {
      case RequirementSourceEnum.SCHEDULE_B:
        generalProperties.push({
          name: "Condition #",
          value:
            complaintData.requirement_detail?.additional_details
              ?.condition_number ?? "",
        });
        break;
      case RequirementSourceEnum.EAC:
        generalProperties.push({
          name: "Amendment #",
          value:
            complaintData.requirement_detail?.additional_details
              ?.amendment_number ?? "",
        });
        generalProperties.push({
          name: "Condition #",
          value:
            complaintData.requirement_detail?.additional_details
              ?.amendment_condition_number ?? "",
        });
        generalProperties.push({
          name: "Condition Description",
          value: complaintData.requirement_detail?.description ?? "",
        });
        break;
      case RequirementSourceEnum.ACT2018:
      case RequirementSourceEnum.ACT2022:
      case RequirementSourceEnum.CPD:
      case RequirementSourceEnum.COMPLAINCE_AGREEMENT:
      case RequirementSourceEnum.NOT_EA_ACT:
      case RequirementSourceEnum.OTHER:
        generalProperties.push({
          name: "Condition Description",
          value: complaintData.requirement_detail?.description ?? "",
        });
    }
    generalProperties.push({
      name: "Topic",
      value: complaintData.requirement_detail?.topic?.name,
    });
  }

  let complaintProperties = [
    { name: "Complaint Source", value: complaintData.source_type?.name },
  ];

  switch (complaintData.source_type?.id) {
    case ComplaintSourceEnum.AGENCY:
      complaintProperties.push({
        name: "Organization Name",
        value: complaintData.agency?.name ?? "",
      });
      break;
    case ComplaintSourceEnum.FIRST_NATION:
      complaintProperties.push({
        name: "Organization Name",
        value: complaintData.first_nation?.name ?? "",
      });
      break;
    case ComplaintSourceEnum.OTHER:
      complaintProperties.push({
        name: "Description",
        value: complaintData.source_contact?.description ?? "",
      });
      break;
  }

  complaintProperties = [
    ...complaintProperties,
    ...[
      {
        name: "Full Name",
        value: complaintData.source_contact?.full_name ?? "",
      },
      { name: "Email", value: complaintData.source_contact?.email ?? "" },
      {
        name: "Phone Number",
        value: complaintData.source_contact?.phone ?? "",
      },
      { name: "Comments", value: complaintData.source_contact?.comment ?? "" },
    ],
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
        {generalProperties.map((property) => (
          <FileProfileProperty
            key={property.name}
            propertyName={property.name}
            propertyValue={property.value}
          />
        ))}
      </Box>
      <Box mb={"1rem"} mt={"1.5rem"}>
        <Typography variant="h6">Complainant Information</Typography>
      </Box>
      <Box display={"flex"} flexDirection={"column"}>
        {complaintProperties.map((property) => (
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

export default ComplaintGeneralInformation;
