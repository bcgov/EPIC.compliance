import { Box } from "@mui/material";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import { FC, useEffect } from "react";
import { ComplaintSource } from "@/models/ComplaintSource";
import { BCDesignTokens } from "epic.theme";
import { useFormContext, useWatch } from "react-hook-form";
import { ComplaintSourceEnum } from "./ComplaintFormUtils";
import { Agency } from "@/models/Agency";
import { FirstNation } from "@/models/FirstNation";
import ContactForm from "@/components/App/ContactForm";
import { useDrawer } from "@/store/drawerStore";
import DynamicInputField, {
  DynamicInputFieldConfig,
} from "@/components/App/DynamicInputField";
import { useModal } from "@/store/modalStore";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";

type ComplaintSourceProps = {
  complaintSourceList: ComplaintSource[];
  agenciesList: Agency[];
  firstNationsList: FirstNation[];
};

const sectionPadding = "1rem 2rem 0rem 1rem";

const ComplaintSourceForm: FC<ComplaintSourceProps> = ({
  complaintSourceList,
  agenciesList,
  firstNationsList,
}) => {
  const { isOpen } = useDrawer();
  const { setOpen, setClose } = useModal();
  const { control, resetField, setValue, getValues } = useFormContext();

  // Watch for changes in `complaintSource` field
  const selectedComplaintSource = useWatch({
    control,
    name: "complaintSource",
    defaultValue: undefined,
  });

  useEffect(() => {
    // Reset complaintSource when the drawer is closed
    if (!isOpen) {
      setValue("complaintSource", null);
    }
  }, [isOpen, setValue]);

  const getSelectedFieldNamesComplaintSource = (): string[] => {
    const dynamicFields =
      dynamicFieldConfigComplaintSource[
        selectedComplaintSource?.id as ComplaintSourceEnum
      ];

    const fieldNames: string[] = [
      "contactFullName",
      "contactTitle",
      "contactEmail",
      "contactPhoneNumber",
      "contactComments",
    ];
    if (dynamicFields) {
      fieldNames.push(dynamicFields.name);
    }

    return fieldNames;
  };

  const handleComplaintSourceChange = (
    _event: React.SyntheticEvent,
    newValue: ComplaintSource | ComplaintSource[] | null
  ) => {
    if (
      !selectedComplaintSource ||
      !newValue ||
      selectedComplaintSource.id === (newValue as ComplaintSource).id
    ) {
      setValue("complaintSource", newValue);
      return;
    }
    const isDynamicFieldsNotEmpty = getSelectedFieldNamesComplaintSource().some(
      (fieldName) => !!getValues(fieldName)
    );
    if (isDynamicFieldsNotEmpty) {
      // If dynamic fields contain values, prompt user
      setOpen({
        content: (
          <ConfirmationModal
            title="Change Complaint Source?"
            description="You have entered information for the current complaint source. Changing the complaint source will clear the fields that are specific to this source.
            Are you sure you want to proceed?"
            confirmButtonText="Yes"
            cancelButtonText="No"
            onConfirm={() => {
              resetFieldForComplaintSource();
              setClose();
            }}
            onCancel={() => {
              setValue("complaintSource", selectedComplaintSource);
            }}
          />
        ),
      });
    } else {
      // If dynamic fields are empty, proceed with the change
      setValue("complaintSource", newValue);
      resetFieldForComplaintSource();
    }
  };

  const resetFieldForComplaintSource = () => {
    getSelectedFieldNamesComplaintSource().forEach((fieldName) =>
      resetField(fieldName)
    );
  };

  const dynamicFieldConfigComplaintSource: Record<
    ComplaintSourceEnum,
    DynamicInputFieldConfig
  > = {
    [ComplaintSourceEnum.AGENCY]: {
      type: "autocomplete",
      name: "agency",
      label: "Agency",
      options: agenciesList,
      required: true,
    },
    [ComplaintSourceEnum.FIRST_NATION]: {
      type: "autocomplete",
      name: "firstNation",
      label: "First Nation",
      options: firstNationsList,
      required: true,
    },
    [ComplaintSourceEnum.OTHER]: {
      type: "text",
      name: "otherDescription",
      label: "Description",
      options: undefined,
      required: true,
    },
  };

  const isComplaintSourceSelected: boolean = !!selectedComplaintSource?.id;

  return (
    <>
      <Box p={sectionPadding}>
        <ControlledAutoComplete
          name="complaintSource"
          label="Complaint Source"
          options={complaintSourceList}
          getOptionLabel={(option) => option.name}
          getOptionKey={(option) => option.id}
          isOptionEqualToValue={(option, value) => option.id === value.id}
          onChange={handleComplaintSourceChange}
          fullWidth
          isRequired={true}
        />
      </Box>
      {isComplaintSourceSelected && (
        <Box
          p={sectionPadding}
          mb={"1.5rem"}
          bgcolor={BCDesignTokens.surfaceColorBackgroundLightBlue}
        >
          <DynamicInputField
            config={
              dynamicFieldConfigComplaintSource[
                selectedComplaintSource?.id as ComplaintSourceEnum
              ]
            }
          />
          <ContactForm />
        </Box>
      )}
    </>
  );
};

export default ComplaintSourceForm;
