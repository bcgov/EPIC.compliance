import { FC, useCallback, useEffect, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import { useQueryClient } from "@tanstack/react-query";
import { Box, DialogContent, Typography } from "@mui/material";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { BCDesignTokens } from "epic.theme";
import { useModal } from "@/store/modalStore";
import {
  baseEnforcementSchema,
  getDefaultFormValues,
  ENFORCEMENT_MESSAGES,
} from "@/components/App/Inspections/Profile/Enforcements/EnforcementUtils";
import { useCreateRestorativeJustice } from "@/hooks/useRestorativeJustice";
import {
  RestorativeJustice,
  RestorativeJusticeAPIData,
} from "@/models/RestorativeJustice";
import { Inspection } from "@/models/Inspection";
import { notify } from "@/store/snackbarStore";
import RestorativeJusticeUpdateModal from "./RestorativeJusticeUpdateModal";
import { MODAL_WIDTHS } from "@/utils/constants";

const restorativeJusticeSchema = baseEnforcementSchema;

type RestorativeJusticeFormType = yup.InferType<typeof restorativeJusticeSchema>;

type RestorativeJusticeCreateModalProps = {
  inspectionData: Inspection;
  requirementsList: InspectionRequirement[];
  requirement?: InspectionRequirement;
  onSubmit: (data: RestorativeJustice) => void;
};

const RestorativeJusticeCreateModal: FC<RestorativeJusticeCreateModalProps> = ({
  inspectionData,
  requirementsList,
  requirement,
  onSubmit,
}) => {
  const queryClient = useQueryClient();
  const { setOpen: setModalOpen, setClose: setModalClose } = useModal();

  const defaultValues = useMemo(() => {
    const baseValues = getDefaultFormValues(requirement, false);
    return baseValues;
  }, [requirement]);

  const methods = useForm<RestorativeJusticeFormType>({
    resolver: yupResolver(restorativeJusticeSchema),
    mode: "onBlur",
    defaultValues,
  });

  const { reset, handleSubmit, watch } = methods;
  const selectedRequirements = watch("requirements") as InspectionRequirement[];

  useEffect(() => {
    reset(defaultValues);
  }, [reset, defaultValues]);

  const onSuccess = (data: RestorativeJustice) => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-restorative-justice", inspectionData.id],
    });
    notify.success(ENFORCEMENT_MESSAGES.RESTORATIVE_JUSTICE_CREATED(data.restorative_justice_number || ""));

    setModalClose();

    setTimeout(() => {
      setModalOpen({
        content: (
          <RestorativeJusticeUpdateModal
            restorativeJustice={data}
            inspectionData={inspectionData}
            onSuccess={(updatedData) => {
              onSubmit(updatedData);
            }}
          />
        ),
        width: MODAL_WIDTHS.RESTORATIVE_JUSTICE
      });
    }, 100);
  };

  const { mutate: createRestorativeJustice, isPending: isPendingRestorativeJustice } =
    useCreateRestorativeJustice(onSuccess);

  const handleSubmitForm = useCallback(
    (data: RestorativeJusticeFormType) => {
      const restorativeJusticeData: RestorativeJusticeAPIData = {
        inspection_id: inspectionData?.id ?? 0,
        inspection_requirement_ids: (
          data.requirements as InspectionRequirement[]
        ).map((requirement) => requirement.id),
      };

      createRestorativeJustice({
        restorativeJustice: restorativeJusticeData,
      });
    },
    [createRestorativeJustice, inspectionData]
  );

  const handleCancel = () => {
    setModalClose();
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(handleSubmitForm)}>
        <ModalTitleBar title="Create Restorative Justice" />
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
              sx={{ mb: 2 }}
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

          </Box>
          {selectedRequirements?.length > 1 && (
            <Box
              sx={{
                p: "1rem 1.5rem",
                backgroundColor: BCDesignTokens.supportSurfaceColorWarning,
                borderTop: `1px solid ${BCDesignTokens.supportBorderColorWarning}`,
              }}
            >
              <Typography variant="body2" color="warning.main">
                <strong>Note:</strong> You have selected multiple requirements. A single Restorative Justice record will be created for all selected requirements.
              </Typography>
            </Box>
          )}
        </DialogContent>
        <ModalActions
          onSecondaryAction={handleCancel}
          onPrimaryAction={handleSubmit(handleSubmitForm)}
          isLoading={isPendingRestorativeJustice}
          primaryActionButtonText="Create"
          secondaryActionButtonText="Cancel"
        />
      </form>
    </FormProvider>
  );
};

export default RestorativeJusticeCreateModal;
