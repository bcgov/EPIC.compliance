import { Box } from "@mui/material";
import * as yup from "yup";
import { FormProvider, useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import { useEffect, useMemo } from "react";
import PopoverActions from "@/components/Shared/Popover/PopoverActions";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import { StaffUser } from "@/models/Staff";
import { useReportStore } from "@/components/App/Inspections/Profile/Reports/reportStore";

type PreparedByPopoverProps = {
  onSubmit: (staffUserId: number) => void;
  currentPrimaryOfficer?: StaffUser;
};

const preparedByFormSchema = yup.object().shape({
  primaryOfficer: yup
    .object<StaffUser>()
    .nullable()
    .required("Primary Officer is required"),
});

type PreparedBySchemaType = yup.InferType<typeof preparedByFormSchema>;

const PreparedByPopover: React.FC<PreparedByPopoverProps> = ({
  onSubmit,
  currentPrimaryOfficer,
}) => {
  const { inspectionData, caseFileData } = useReportStore();

  // Combine and deduplicate staff users by their unique id
  const staffUserList = useMemo(
    () =>
      [
        inspectionData?.primary_officer,
        caseFileData?.primary_officer,
        ...(caseFileData?.officers ?? []),
      ]
        .filter(Boolean)
        .reduce((acc: StaffUser[], user) => {
          if (!acc.some((u) => u.id === user!.id)) {
            acc.push(user as StaffUser);
          }
          return acc;
        }, []),
    [inspectionData, caseFileData]
  );

  const defaultValues = useMemo(() => {
    return currentPrimaryOfficer
      ? {
          primaryOfficer: currentPrimaryOfficer,
        }
      : { primaryOfficer: undefined };
  }, [currentPrimaryOfficer]);

  const methods = useForm<PreparedBySchemaType>({
    resolver: yupResolver(preparedByFormSchema),
    mode: "onBlur",
    defaultValues,
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    reset(defaultValues);
  }, [defaultValues, reset]);

  const onSubmitHandler = (data: PreparedBySchemaType) => {
    if (data.primaryOfficer) {
      onSubmit((data.primaryOfficer as StaffUser).id);
    }
  };

  return (
    <>
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(onSubmitHandler)}>
          <Box display="flex" flexDirection="column" px={2} pt={2}>
            <ControlledAutoComplete
              name="primaryOfficer"
              label="Primary Officer"
              placeholder="Select Primary Officer"
              options={staffUserList ?? []}
              getOptionLabel={(option) => option.name}
              getOptionKey={(option) => option.id}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              fullWidth
              isRequired={true}
              isSortOptions
            />
          </Box>
          <PopoverActions
            primaryActionButtonText={currentPrimaryOfficer ? "Save" : "Add"}
          />
        </form>
      </FormProvider>
    </>
  );
};

export default PreparedByPopover;
