import DynamicInputField, {
  DynamicInputFieldConfig,
} from "@/components/App/DynamicInputField";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import ControlledDateField from "@/components/Shared/Controlled/ControlledDateField";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";
import { Agency } from "@/models/Agency";
import { Attendance } from "@/models/Attendance";
import { FirstNation } from "@/models/FirstNation";
import { StaffUser } from "@/models/Staff";
import { useDrawer } from "@/store/drawerStore";
import { useModal } from "@/store/modalStore";
import { Box, Stack, Typography } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import { FC, useEffect } from "react";
import { useFormContext, useWatch } from "react-hook-form";
import { AttendanceEnum, DRAWER_WIDTHS } from "@/utils/constants";
import ControlledCheckbox from "@/components/Shared/Controlled/ControlledCheckbox";
import useIsDrawerConstrained from "@/hooks/useIsDrawerConstrained";

type InspectionFormRightProps = {
  attendanceList: Attendance[];
  agenciesList: Agency[];
  firstNationsList: FirstNation[];
  staffList: StaffUser[];
};

type AttendanceDynamicField =
  | AttendanceEnum.AGENCIES
  | AttendanceEnum.FIRST_NATIONS
  | AttendanceEnum.OTHER;

const sectionPadding = "1rem 2rem 0rem 1rem";

const InspectionFormRight: FC<InspectionFormRightProps> = ({
  attendanceList,
  agenciesList,
  firstNationsList,
  staffList,
}) => {
  const { isOpen } = useDrawer();
  const { setOpen, setClose } = useModal();
  const { control, resetField, getValues, setValue } = useFormContext();
  const isDrawerConstrained = useIsDrawerConstrained(DRAWER_WIDTHS.INSPECTION_DRAWER);

  const attendanceOptions = attendanceList.filter(
    (attendance) =>
      ![
        AttendanceEnum.INDIVIDUAL_ENV_MONITOR,
        AttendanceEnum.CH_RP_REPRESENTATIVE,
        AttendanceEnum.OFFICERS,
      ].includes(attendance.id as AttendanceEnum)
  );

  // Watch for changes in `inAttendance` field
  const selectedAttendance = useWatch({
    control,
    name: "inAttendance",
    defaultValue: getValues("inAttendance") ?? [],
  });

  useEffect(() => {
    // Reset inAttendance when the drawer is closed
    if (!isOpen) {
      setValue("inAttendance", []);
    }
  }, [isOpen, setValue]);

  const handleDeleteOption = (option: Attendance) => {
    const fieldName =
      dynamicFieldConfig[option.id as AttendanceDynamicField]?.name;
    const fieldValue = getValues(fieldName);

    if (fieldName && fieldValue?.length) {
      setOpen({
        content: (
          <ConfirmationModal
            title="Remove Group?"
            description="You have selected one or more options in this group. Deselecting will remove all selected items. Are you sure you want to remove it?"
            confirmButtonText="Remove"
            onConfirm={() => handleConfirmRemove(option)}
          />
        ),
      });
    } else {
      handleConfirmRemove(option); // Remove immediately if no values are filled
    }
  };

  const handleConfirmRemove = (selectedToRemove: Attendance) => {
    if (selectedToRemove) {
      const fieldName =
        dynamicFieldConfig[selectedToRemove.id as AttendanceDynamicField]?.name;
      if (fieldName) {
        resetField(fieldName); // Reset the corresponding field value
      }
      const inAttendanceValues: Attendance[] = getValues("inAttendance");
      const updatedAttendanceList: Attendance[] = inAttendanceValues.filter(
        (att) => att.id !== selectedToRemove.id
      );
      setValue("inAttendance", updatedAttendanceList); // Remove from the form field
    }
    setClose();
  };

  const dynamicFieldConfig: Record<
    AttendanceDynamicField,
    DynamicInputFieldConfig
  > = {
    [AttendanceEnum.AGENCIES]: {
      type: "autocomplete",
      name: "agencies",
      label: "Agencies",
      options: agenciesList,
      multiple: true,
      required: true,
    },
    [AttendanceEnum.FIRST_NATIONS]: {
      type: "autocomplete",
      name: "firstNations",
      label: "First Nations",
      options: firstNationsList,
      multiple: true,
      required: true,
    },
    [AttendanceEnum.OTHER]: {
      type: "text",
      name: "other",
      label: "Other",
      required: true,
    },
  };

  const isRelevantAttendanceSelected = selectedAttendance.some(
    (attendee: Attendance) =>
      Object.values(AttendanceEnum).includes(attendee.id as AttendanceEnum)
  );

  return (
    <>
      <Box
        sx={{
          width: isDrawerConstrained ? "auto" : "399px",
          boxSizing: "border-box",
          overflow: isDrawerConstrained ? "unset" : "auto",
          marginLeft: isDrawerConstrained ? 2 : "unset",
        }}
      >
        <Stack>
          <Box p={sectionPadding}>
            <ControlledDateField
              className="cy-debrief-date"
              name="debriefDate"
              label="Regulated Party Debrief Date"
            />
          </Box>
          <Box p={sectionPadding}>
            <Typography variant="body2" mb={1}>
              Inspection Attendees
            </Typography>
            <Typography component="p" variant="caption" mb={2}>
              Select the categories of people who attended this inspection in
              addition to yourself
            </Typography>
            <ControlledCheckbox
              name="isCHRepresentatives"
              label="Certificate Holder / Regulated Party Representatives"
              fontSize="small"
            />
            <ControlledCheckbox
              name="isIndependentEnvMonitor"
              label="Independent Environmental Monitor"
              fontSize="small"
            />
            <ControlledAutoComplete
              name="officers"
              label="Attending Officers"
              placeholder="Select officers that attended inspection"
              options={staffList}
              getOptionLabel={(option) => option.name}
              getOptionKey={(option) => option.id}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              multiple
              fullWidth
            />
            <ControlledAutoComplete
              name="inAttendance"
              label="In Attendance"
              placeholder="Select groups that attended inspection"
              options={attendanceOptions}
              getOptionLabel={(option) => option.name}
              getOptionKey={(option) => option.id}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              multiple
              fullWidth
              onDeleteOption={handleDeleteOption}
            />
          </Box>
          {/* Show this section only if relevant AttendanceEnum values are selected */}
          {isRelevantAttendanceSelected && (
            <Box
              p={sectionPadding}
              bgcolor={BCDesignTokens.surfaceColorBackgroundLightBlue}
            >
              {selectedAttendance.map((attendee: Attendance) => {
                return (
                  <DynamicInputField
                    key={attendee.name}
                    config={
                      dynamicFieldConfig[attendee.id as AttendanceDynamicField]
                    }
                  />
                );
              })}
            </Box>
          )}
        </Stack>
      </Box>
    </>
  );
};

export default InspectionFormRight;
