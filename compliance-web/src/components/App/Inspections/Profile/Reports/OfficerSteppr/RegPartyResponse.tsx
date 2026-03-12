import { yupResolver } from "@hookform/resolvers/yup";
import { Box, Button, Typography } from "@mui/material";
import { useEffect, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import dayjs, { Dayjs } from "dayjs";
import ControlledDateField from "@/components/Shared/Controlled/ControlledDateField";
import ControlledRadioButtonGroup from "@/components/Shared/Controlled/ControlledRadioButtonGroup";
import { InspectionRecordApprovalPayload } from "@/models/IRApproval";
import { useReportStore } from "../reportStore";
import dateUtils from "@/utils/dateUtils";

const regPartyResponseFormSchema = yup.object().shape({
  responseReceived: yup.string().required("Response selection is required"),
  responseDate: yup.mixed<Dayjs>().when("responseReceived", {
    is: "yes",
    then: (schema) =>
      schema.required("Date Received is required").typeError("Invalid date"),
    otherwise: (schema) => schema.nullable(),
  }),
});

type RegPartyResponseSchemaType = yup.InferType<
  typeof regPartyResponseFormSchema
>;

const initFormData: RegPartyResponseSchemaType = {
  responseReceived: "",
  responseDate: undefined as unknown as Dayjs,
};

type RegPartyResponseProps = {
  onUpdateIRApprovalStep: (
    approvalPayloads: InspectionRecordApprovalPayload[]
  ) => void;
  onNext: () => void;
  onBack: () => void;
  isPending?: boolean;
};

const RegPartyResponse: React.FC<RegPartyResponseProps> = ({
  onUpdateIRApprovalStep,
  onNext,
  onBack,
  isPending = false,
}) => {
  const { irApprovalsData } = useReportStore();

  const defaultValues = useMemo<RegPartyResponseSchemaType>(() => {
    const currentApproval = irApprovalsData?.[0];
    if (currentApproval) {
      return {
        responseReceived: currentApproval.date_response ? "yes" : "no",
        responseDate: currentApproval.date_response
          ? dayjs(currentApproval.date_response)
          : (undefined as unknown as Dayjs),
      };
    }
    return initFormData;
  }, [irApprovalsData]);

  const methods = useForm<RegPartyResponseSchemaType>({
    resolver: yupResolver(regPartyResponseFormSchema),
    mode: "onChange",
    defaultValues,
  });

  const {
    handleSubmit,
    watch,
    reset,
    formState: { isDirty, isValid },
  } = methods;

  // Reset form with defaultValues when they change
  useEffect(() => {
    if (defaultValues.responseReceived || defaultValues.responseDate) {
      reset(defaultValues);
    }
  }, [defaultValues, reset]);

  const responseReceived = watch("responseReceived");

  const onSubmitHandler = (data: RegPartyResponseSchemaType) => {
    if (isDirty) {
      const approvalPayloads: InspectionRecordApprovalPayload[] = [
        {
          field_name: "date_response",
          value:
            data.responseReceived === "yes" && data.responseDate
              ? dateUtils.dateToISO(data.responseDate)
              : null,
        },
      ];
      onUpdateIRApprovalStep(approvalPayloads);
    } else {
      onNext();
    }
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmitHandler)}>
        <Typography variant="body2" mb={1}>
          Have you received a response from Regulated Party (RP)?
        </Typography>
        <ControlledRadioButtonGroup
          name="responseReceived"
          options={[
            { id: "yes", name: "Yes, RP provided response" },
            { id: "no", name: "No, RP didn’t provide a response" },
          ]}
        />
        <Box
          sx={{
            display: "flex",
            flexDirection: "row",
            justifyContent:
              responseReceived === "yes" ? "space-between" : "flex-end",
            alignItems: "center",
            gap: 1,
            mt: 2,
          }}
        >
          {responseReceived === "yes" && (
            <Box maxWidth="270px">
              <ControlledDateField
                name="responseDate"
                label="Preliminary IR Response Date"
                height="2rem"
              />
            </Box>
          )}
          <Box
            sx={{
              display: "flex",
              gap: 1,
            }}
          >
            <Button variant="outlined" size="small" onClick={onBack}>
              Previous
            </Button>
            <Button size="small" type="submit" disabled={!isValid || isPending}>
              Save & Next
            </Button>
          </Box>
        </Box>
      </form>
    </FormProvider>
  );
};

export default RegPartyResponse;
