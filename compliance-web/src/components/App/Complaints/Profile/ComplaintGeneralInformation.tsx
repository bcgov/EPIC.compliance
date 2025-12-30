import { ComplaintSourceEnum } from "@/components/App/Complaints/ComplaintFormUtils";
import FileProfileProperty from "@/components/App/FileProfileProperty";
import DynamicHeightBox from "@/components/Shared/DynamicHeightBox";
import { Complaint } from "@/models/Complaint";
import { RequirementSourceEnum } from "@/utils/constants";
import dateUtils from "@/utils/dateUtils";
import { EditRounded } from "@mui/icons-material";
import { Box, Button, Typography } from "@mui/material";
import React from "react";

interface ComplaintGeneralInformationProps {
  complaintData: Complaint;
  onEdit: () => void;
  allowEdit?: boolean;
}

const ComplaintGeneralInformation: React.FC<
  ComplaintGeneralInformationProps
> = ({ complaintData, onEdit, allowEdit }) => {
  const generalProperties = [
    { name: "Project Name", value: complaintData.case_file?.project?.name },
    {
      name: "Concern Description",
      value: complaintData.concern_description,
    },
    {
      name: "Topic",
      value: complaintData.topic?.name,
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
    if (complaintData.requirement_source.id === RequirementSourceEnum.ORDER) {
      generalProperties.push({
        name: "Order Number",
        value: complaintData.requirement_detail?.order_number ?? "",
      });
    } else {
      generalProperties.push({
        name: "Requirement Details",
        value: complaintData.requirement_source_description ?? "",
      });
    }
  }

  if (complaintData.resolution) {
    generalProperties.push({
      name: "Resolution",
      value: complaintData.resolution?.name,
    });
  }

  if (complaintData.resolution_agency) {
    generalProperties.push({
      name: "Resolution Agency",
      value: complaintData.resolution_agency?.name,
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
    case ComplaintSourceEnum.FIRST_NATIONS_ALLIANCE:
      complaintProperties.push({
        name: "Alliance Name",
        value: complaintData.source_contact?.alliance_name ?? "",
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
      ...(complaintData.source_type?.id === ComplaintSourceEnum.FIRST_NATIONS_ALLIANCE
        ? []
        : [{
          name: "Title",
          value: complaintData.source_contact?.title ?? "",
        }]),
      { name: "Email", value: complaintData.source_contact?.email ?? "" },
      {
        name: "Phone Number",
        value: complaintData.source_contact?.phone ?? "",
      },
      { name: "Comments", value: complaintData.source_contact?.comment ?? "" },
    ],
  ];

  return (
    <DynamicHeightBox
      display={"flex"}
      flexGrow={1}
      flexDirection={"column"}
      width={"75%"}
      bottomOffset={20}
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
    </DynamicHeightBox>
  );
};

export default ComplaintGeneralInformation;
