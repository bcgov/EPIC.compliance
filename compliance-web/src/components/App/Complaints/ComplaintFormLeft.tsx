import { FC } from "react";
import { Box, Stack, useMediaQuery } from "@mui/material";
import { StaffUser } from "@/models/Staff";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import { BCDesignTokens } from "epic.theme";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";
import ControlledDateField from "@/components/Shared/Controlled/ControlledDateField";
import { Topic } from "@/models/Topic";
import RequirementSourceForm from "./RequirementSourceForm";
import { RequirementSource } from "@/models/RequirementSource";

import { Complaint } from "@/models/Complaint";
import { MQ } from "@/styles/responsive";

type ComplaintFormLeftProps = {
  staffUsersList: StaffUser[];
  topicsList: Topic[];
  requirementSourceList: RequirementSource[];
  complaint?: Complaint;
  caseFileId: number;
};

const ComplaintFormLeft: FC<ComplaintFormLeftProps> = ({
  staffUsersList,
  topicsList,
  requirementSourceList,
  complaint,
  caseFileId,
}) => {
  const isMdToLg = useMediaQuery(MQ.mdToLg);
  
  return (
    <>
      <Box
        sx={{
          background: BCDesignTokens.surfaceColorBackgroundLightGray,
          padding: "1rem 1rem 1rem 2rem",
          width: isMdToLg ? "auto" : "718px",
          overflow: isMdToLg ? "unset" : "auto",
          paddingRight: isMdToLg ? 4 : "1rem",
          boxSizing: "border-box",
        }}
      >
        <ControlledTextField
          name="concernDescription"
          label="Concern Description"
          placeholder="Specify concern"
          multiline
          fullWidth
          minRows={2}
          isRequired={true}
        />
        <ControlledAutoComplete
          name="topic"
          label="Topic"
          options={topicsList}
          getOptionLabel={(option) => option.name}
          getOptionKey={(option) => option.id}
          isOptionEqualToValue={(option, value) =>
            option.id.toString() === value.id.toString()
          }
          fullWidth
          isRequired={true}
        />
        <ControlledTextField
          name="locationDescription"
          label="Location Description"
          placeholder="Specify inspected location"
          multiline
          fullWidth
          minRows={2}
        />
        <Stack direction={"row"} gap={2}>
          <ControlledAutoComplete
            name="primaryOfficer"
            label="Primary"
            options={staffUsersList}
            getOptionLabel={(option) => option.name}
            getOptionKey={(option) => option.id}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            fullWidth
            isSortOptions
            isRequired={true}
          />
          <ControlledDateField
            name="dateReceived"
            label="Date Received"
            sx={{ width: "100%" }}
            isRequired={true}
          />
        </Stack>
        <RequirementSourceForm
          requirementSourceList={requirementSourceList ?? []}
          complaint={complaint}
          caseFileId={caseFileId}
        />
      </Box>
    </>
  );
};

export default ComplaintFormLeft;
