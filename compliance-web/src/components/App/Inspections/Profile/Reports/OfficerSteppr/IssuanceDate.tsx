import { yupResolver } from "@hookform/resolvers/yup";
import { Box, Button, Typography } from "@mui/material";
import { useEffect, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import dayjs, { Dayjs } from "dayjs";
import ControlledDateField from "@/components/Shared/Controlled/ControlledDateField";
import { useReportStore } from "../reportStore";
import dateUtils from "@/utils/dateUtils";
import { notify } from "@/store/snackbarStore";
import { useUpdateInspectionRecord } from "@/hooks/useInspectionReports";
import { InspectionRecord } from "@/models/InspectionRecord";

const issuanceDateFormSchema = yup.object().shape({
  issuanceDate: yup.mixed<Dayjs>().required("Issuance date is required"),
});

type IssuanceDateSchemaType = yup.InferType<typeof issuanceDateFormSchema>;

const initFormData: IssuanceDateSchemaType = {
  issuanceDate: undefined as unknown as Dayjs,
};

const IssuanceDate: React.FC = () => {
  const { inspectionData, inspectionReportsData, setInspectionReportsData } =
    useReportStore();

  const defaultValues = useMemo<IssuanceDateSchemaType>(() => {
    if (inspectionReportsData?.intended_issuance_date) {
      return {
        issuanceDate: dayjs(inspectionReportsData?.intended_issuance_date),
      };
    }
    return initFormData;
  }, [inspectionReportsData]);

  const methods = useForm<IssuanceDateSchemaType>({
    resolver: yupResolver(issuanceDateFormSchema),
    mode: "onBlur",
    defaultValues,
  });

  const {
    handleSubmit,
    reset,
    formState: { isDirty},
  } = methods;

  // Reset form with defaultValues when they change
  useEffect(() => {
    if (defaultValues.issuanceDate) {
      reset(defaultValues);
    }
  }, [defaultValues, reset]);

  const handleOnSuccess = (data: InspectionRecord) => {
    notify.success("Intended issuance date updated");
    setInspectionReportsData(data);
  };

  const { mutate: updateInspectionRecord, isPending } =
    useUpdateInspectionRecord(handleOnSuccess);

  const onSubmitHandler = (data: IssuanceDateSchemaType) => {
    if (isDirty) {
      updateInspectionRecord({
        inspectionId: inspectionData?.id ?? 0,
        inspectionRecordId: inspectionReportsData?.id ?? 0,
        updateRecord: {
          field_name: "intended_issuance_date",
          value: dateUtils.dateToISO(data.issuanceDate),
        },
      });
    }
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmitHandler)}>
        <Typography variant="body2" mb={1}>
          Indicate the IR issuance date. This date will be recorded in the
          Inspection Version Dates section. If the issuance date changes, be
          sure to update it here. On the date after the record is issued, don’t
          forget to update the continuation report.
        </Typography>
        <Box
          sx={{
            display: "flex",
            flexDirection: "row",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 1,
            mt: 2,
          }}
        >
          <ControlledDateField
            name="issuanceDate"
            label="Issuance Date"
            height="2rem"
            width="40%"
          />
          <Button
            size="small"
            type="submit"
            disabled={!isDirty || isPending}
            sx={{ width: "150px" }}
          >
            Save & Record
          </Button>
        </Box>
      </form>
    </FormProvider>
  );
};

export default IssuanceDate;
