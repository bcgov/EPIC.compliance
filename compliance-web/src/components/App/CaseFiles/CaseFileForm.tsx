import React from "react";
import { Box, Stack, Typography } from "@mui/material";
import { StaffUser } from "@/models/Staff";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import { BCDesignTokens } from "epic.theme";
import { Project } from "@/models/Project";
import { Initiation } from "@/models/Initiation";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";
import ControlledDateField from "@/components/Shared/Controlled/ControlledDateField";
import ProjectDetailsForm from "@/components/App/ProjectDetailsForm";

type CaseFileFormProps = {
  projectList: Project[];
  initiationList: Initiation[];
  staffUsersList: StaffUser[];
  isEditMode: boolean;
  isSuperUser: boolean;
  caseFileProjectId?: number | null;
};

const CaseFileForm: React.FC<CaseFileFormProps> = ({
  projectList,
  initiationList,
  staffUsersList,
  isEditMode,
  isSuperUser,
  caseFileProjectId,
}) => {
  return (
    <>
      <Box padding={"0.75rem 2rem"}>
        <Typography
          variant="body2"
          sx={{
            fontWeight: BCDesignTokens.typographyFontWeightsBold,
            color: BCDesignTokens.typographyColorPrimary,
            marginBottom: BCDesignTokens.layoutMarginMedium,
          }}
        >
          General Information
        </Typography>
        <Stack direction={"row"} gap={2}>
          <ProjectDetailsForm
            projectList={projectList}
            isEditMode={isEditMode}
            caseFileProjectId={caseFileProjectId}
          />
          <Stack flex={1}>
            <ControlledAutoComplete
              name="initiation"
              label="Initiation"
              options={initiationList}
              getOptionLabel={(option) => option.name}
              getOptionKey={(option) => option.id}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              fullWidth
              disabled={isEditMode}
              isRequired={true}
            />
            <ControlledAutoComplete
              name="primaryOfficer"
              label="Primary"
              options={staffUsersList}
              getOptionLabel={(option) => option.name}
              getOptionKey={(option) => option.id}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              fullWidth
              isRequired={true}
            />
            <ControlledAutoComplete
              name="officers"
              label="Other Assigned Officers"
              options={staffUsersList}
              getOptionLabel={(option) => option.name}
              getOptionKey={(option) => option.id}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              multiple
              fullWidth
            />
            {isSuperUser && (
              <>
                <ControlledDateField
                  name="dateCreated"
                  label="Date Created"
                  sx={{ width: "100%" }}
                  disabled={isEditMode}
                />
                <ControlledTextField
                  label="Manual Case File Number"
                  name="caseFileNumber"
                  placeholder="Enter Case File Number"
                  fullWidth
                  disabled={isEditMode}
                />
              </>
            )}
          </Stack>
        </Stack>
        <ControlledTextField
          name="projectDescription"
          label="Project Description"
          multiline
          fullWidth
          minRows={5}
        />
      </Box>
    </>
  );
};

export default CaseFileForm;
