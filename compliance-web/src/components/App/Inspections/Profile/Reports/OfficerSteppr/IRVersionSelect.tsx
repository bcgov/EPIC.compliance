import { yupResolver } from "@hookform/resolvers/yup";
import { Box, Button, Typography } from "@mui/material";
import { useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import ControlledRadioButtonGroup from "@/components/Shared/Controlled/ControlledRadioButtonGroup";

const irVersionSelectFormSchema = yup.object().shape({
  versionSelection: yup.string().required("Version selection is required"),
});

type IRVersionSelectSchemaType = yup.InferType<
  typeof irVersionSelectFormSchema
>;

const initFormData: IRVersionSelectSchemaType = {
  versionSelection: "",
};

type IRVersionSelectProps = {
  onBack: () => void;
  onUpdateIRReportToFinal: () => void;
  onUpdateIRReportToPreliminary: () => void;
};

const IRVersionSelect: React.FC<IRVersionSelectProps> = ({
  onBack,
  onUpdateIRReportToFinal,
  onUpdateIRReportToPreliminary,
}) => {
  const defaultValues = useMemo<IRVersionSelectSchemaType>(() => {
    return initFormData;
  }, []);

  const methods = useForm<IRVersionSelectSchemaType>({
    resolver: yupResolver(irVersionSelectFormSchema),
    mode: "onChange",
    defaultValues,
  });

  const {
    handleSubmit,
    formState: { isValid },
  } = methods;

  const onSubmitHandler = (data: IRVersionSelectSchemaType) => {
    if (data.versionSelection === "final") {
      onUpdateIRReportToFinal();
    } else {
      onUpdateIRReportToPreliminary();
    }
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmitHandler)}>
        <Typography variant="body2" mb={1}>
          Review the Regulated Party's response and decide how to proceed.
          Select whether to finalize the Inspection Record or conduct another
          round of Preliminary Review.
        </Typography>
        <ControlledRadioButtonGroup
          name="versionSelection"
          options={[
            { id: "final", name: "Proceed with Final IR" },
            { id: "preliminary", name: "Continue with Preliminary IR" },
          ]}
        />
        <Box
          sx={{
            display: "flex",
            flexDirection: "row",
            justifyContent: "flex-end",
            alignItems: "center",
            gap: 1,
            mt: 2,
          }}
        >
          <Box
            sx={{
              display: "flex",
              gap: 1,
            }}
          >
            <Button variant="outlined" size="small" onClick={onBack}>
              Previous
            </Button>
            <Button size="small" type="submit" disabled={!isValid}>
              Save & Finish
            </Button>
          </Box>
        </Box>
      </form>
    </FormProvider>
  );
};

export default IRVersionSelect;
