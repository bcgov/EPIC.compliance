import { Box, Stack } from "@mui/material";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import { FC, useEffect } from "react";
import { Attendance } from "@/models/Attendance";
import { BCDesignTokens } from "epic.theme";
import { Agency } from "@/models/Agency";
import { FirstNation } from "@/models/FirstNation";
import { useFormContext, useWatch } from "react-hook-form";
import { useModal } from "@/store/modalStore";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";
import { AttendanceEnum } from "./InspectionFormUtils";
import { useDrawer } from "@/store/drawerStore";
import DynamicInputField, {
  DynamicInputFieldConfig,
} from "@/components/App/DynamicInputField";
import { StaffUser } from "@/models/Staff";

type InspectionFormRightProps = {
  attendanceList: Attendance[];
  agenciesList: Agency[];
  firstNationsList: FirstNation[];
  staffList: StaffUser[];
};

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

  // Watch for changes in `inAttendance` field
  const selectedAttendance = useWatch({
    control,
    name: "inAttendance",
    defaultValue: [],
  });

  useEffect(() => {
    // Reset inAttendance when the drawer is closed
    if (!isOpen) {
      setValue("inAttendance", []);
    }
  }, [isOpen, setValue]);

  const handleDeleteOption = (option: Attendance) => {
    const fieldName = dynamicFieldConfig[option.id as AttendanceEnum]?.name;
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
        dynamicFieldConfig[selectedToRemove.id as AttendanceEnum]?.name;
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

  const dynamicFieldConfig: Record<AttendanceEnum, DynamicInputFieldConfig> = {
    [AttendanceEnum.AGENCIES]: {
      type: "autocomplete",
      name: "agencies",
      label: "Agencies",
      options: agenciesList,
      multiple: true,
    },
    [AttendanceEnum.FIRST_NATIONS]: {
      type: "autocomplete",
      name: "firstNations",
      label: "First Nations",
      options: firstNationsList,
      multiple: true,
    },
    [AttendanceEnum.OFFICERS]: {
      type: "autocomplete",
      name: "officers",
      label: "Attending Officers",
      options: staffList,
      multiple: true,
    },
    [AttendanceEnum.MUNICIPAL]: {
      type: "text",
      name: "municipal",
      label: "Municipal",
    },
    [AttendanceEnum.OTHER]: { type: "text", name: "other", label: "Other" },
  };

  const isRelevantAttendanceSelected = selectedAttendance.some(
    (attendee: Attendance) =>
      Object.values(AttendanceEnum).includes(attendee.id as AttendanceEnum)
  );

  return (
    <>
      <Box
        sx={{
          width: "399px",
          boxSizing: "border-box",
          overflow: "auto",
        }}
      >
        <Stack>
          <Box p={sectionPadding}>
            <ControlledAutoComplete
              name="inAttendance"
              label="In Attendance (optional)"
              placeholder="Select groups that attended inspection"
              options={attendanceList}
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
                    config={dynamicFieldConfig[attendee.id as AttendanceEnum]}
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
