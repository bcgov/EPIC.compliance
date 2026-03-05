import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import ControlledDateField from "@/components/Shared/Controlled/ControlledDateField";
import ControlledSwitch from "@/components/Shared/Controlled/ControlledSwitch";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";
import { Initiation } from "@/models/Initiation";
import { IRType } from "@/models/IRType";
import { ProjectStatus } from "@/models/ProjectStatus";
import { StaffUser } from "@/models/Staff";
import { Box, Stack } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import { FC } from "react";
import { useFormContext } from "react-hook-form";
import useIsDrawerConstrained from "@/hooks/useIsDrawerConstrained";
import { DRAWER_WIDTHS } from "@/utils/constants";

type InspectionFormLeftProps = {
  initiationList: Initiation[];
  staffUsersList: StaffUser[];
  irTypeList: IRType[];
  projectStatusList: ProjectStatus[];
};

const InspectionFormLeft: FC<InspectionFormLeftProps> = ({
  initiationList,
  staffUsersList,
  irTypeList,
  projectStatusList,
}) => {
  const isDrawerConstrained = useIsDrawerConstrained(DRAWER_WIDTHS.INSPECTION_DRAWER);
  const { watch } = useFormContext();
  const startDate = watch("startDate");
  const endDate = watch("endDate");

  return (
    <>
      <Box
        sx={{
          background: BCDesignTokens.surfaceColorBackgroundLightGray,
          padding: "1rem 1rem 1rem 2rem",
          width: isDrawerConstrained ? "auto" : "718px",
          overflow: isDrawerConstrained ? "unset" : "auto",
          paddingRight: isDrawerConstrained ? 4 : "1rem",
          boxSizing: "border-box",
        }}
      >
        <ControlledSwitch
          name="isHistory"
          label="Log as Historical Record"
          sx={{ marginBottom: "1rem" }}
        />
        <ControlledTextField
          name="projectDescription"
          label="Project Description"
          placeholder="Project Description"
          multiline
          fullWidth
          minRows={4}
        />
        <ControlledTextField
          name="locationDescription"
          label="Location Description"
          placeholder="Specify the project location"
          multiline
          fullWidth
          minRows={2}
        />
        <ControlledTextField
          name="utm"
          label="UTM"
          placeholder="eg. 9U 454135 6399452"
          fullWidth
        />
        <ControlledTextField
          name="areaInspected"
          label="Project Components / Area Inspected"
          placeholder="Provide a brief description of Project Components / Area Inspected"
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
          <ControlledAutoComplete
            name="initiation"
            label="Initiation"
            options={initiationList}
            getOptionLabel={(option) => option.name}
            getOptionKey={(option) => option.id}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            fullWidth
            isRequired={true}
          />
        </Stack>
        <Stack direction={"row"} gap={2}>
          <ControlledAutoComplete
            name="irTypes"
            label="Type"
            options={irTypeList}
            getOptionLabel={(option) => option.name}
            getOptionKey={(option) => option.id}
            isOptionEqualToValue={(option, value) =>
              option.id.toString() === value.id.toString()
            }
            multiple
            fullWidth
            isRequired={true}
          />
          <Stack direction={"row"} gap={2} sx={{ width: "100%" }}>
            <ControlledDateField
              className="cy-start-date"
              name="startDate"
              label="Start Date"
              maxDate={endDate}
              isRequired={true}
            />
            <ControlledDateField
              className="cy-end-date"
              name="endDate"
              label="End Date"
              minDate={startDate}
            />
          </Stack>
        </Stack>
        <Stack direction={"row"} gap={2}>
          <ControlledAutoComplete
            name="projectStatus"
            label="Project Status"
            options={projectStatusList}
            getOptionLabel={(option) => option.name}
            getOptionKey={(option) => option.id}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            fullWidth
          />
        </Stack>
      </Box>
    </>
  );
};

export default InspectionFormLeft;
