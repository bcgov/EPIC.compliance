import { Box, DialogContent, Typography } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import { useCallback, useEffect, useMemo, ReactNode } from "react";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { BCDesignTokens } from "epic.theme";
import { WarningAmberOutlined } from "@mui/icons-material";
import {
  BaseEnforcementFormType,
  baseEnforcementSchema,
  initBaseFormData,
} from "./EnforcementUtils";

type EnforcementModalProps = {
  requirementsList: InspectionRequirement[];
  requirement?: InspectionRequirement;
  title: string;
  onSubmit: (data: BaseEnforcementFormType, additionalData?: Record<string, any>) => void;
  isLoading?: boolean;
  children?: ReactNode;
  additionalFormFields?: ReactNode;
};

const EnforcementModal = ({
  requirementsList,
  requirement,
  title,
  onSubmit,
  isLoading = false,
  children,
  additionalFormFields,
}: EnforcementModalProps) => {
  const defaultValues = useMemo(() => {
    if (requirement) {
      return {
        requirements: [requirement],
      };
    }
    return initBaseFormData;
  }, [requirement]);

  const methods = useForm<BaseEnforcementFormType>({
    resolver: yupResolver(baseEnforcementSchema),
    mode: "onBlur",
    defaultValues,
  });

  const { handleSubmit, reset, watch } = methods;

  const selectedRequirements = watch("requirements") as InspectionRequirement[];

  useEffect(() => {
    reset(defaultValues);
  }, [reset, defaultValues]);

  const onSubmitHandler = useCallback(
    (data: BaseEnforcementFormType) => {
      const formData = methods.getValues() as any;
      const additionalData: Record<string, any> = {};
      
      Object.keys(formData).forEach(key => {
        if (key !== 'requirements') {
          additionalData[key] = formData[key];
        }
      });
      
      onSubmit(data, additionalData);
    },
    [onSubmit, methods]
  );

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmitHandler)}>
        <ModalTitleBar title={title} titleVariant="h6" />
        <DialogContent dividers sx={{ p: 0 }}>
          <Box sx={{ p: "1rem 1.5rem" }}>
            <ControlledAutoComplete
              name="requirements"
              label="Select Requirements"
              options={requirementsList ?? []}
              getOptionLabel={(option) => {
                return `Requirement ${option.sort_order}`;
              }}
              getOptionKey={(option) => option.id}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              fullWidth
              multiple
              disabled={!requirementsList?.length}
            />
            {selectedRequirements?.map((requirement) => (
              <Box
                key={requirement.id}
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  gap: 1,
                  p: 1.5,
                  mb: 1.5,
                  borderRadius: BCDesignTokens.layoutBorderRadiusMedium,
                  background: BCDesignTokens.surfaceColorBackgroundLightBlue,
                }}
              >
                <Typography variant="caption" fontWeight={700}>
                  Requirement {requirement.sort_order}
                </Typography>
                <Typography variant="subtitle2">
                  {requirement.summary}
                </Typography>
              </Box>
            ))}
            {additionalFormFields}
          </Box>
          {selectedRequirements?.length > 1 && (
            <Box
              sx={{
                display: "flex",
                alignItems: "flex-start",
                gap: 1,
                p: "1rem 1.5rem",
                background: BCDesignTokens.supportSurfaceColorWarning,
                borderTop: `1px solid`,
                borderBottom: `1px solid`,
                borderColor: BCDesignTokens.supportBorderColorWarning,
              }}
            >
              <WarningAmberOutlined fontSize="small" color="warning" />
              <Typography variant="caption">
                Note: By selecting multiple requirements, a single enforcement
                action will be created to address all selected requirements
              </Typography>
            </Box>
          )}
          {children}
        </DialogContent>
        <ModalActions
          primaryActionButtonText="Create"
          isButtonValidation
          isLoading={isLoading}
        />
      </form>
    </FormProvider>
  );
};

export default EnforcementModal;
