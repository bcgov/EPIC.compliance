import { FC, useCallback, useEffect, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import { useQueryClient } from "@tanstack/react-query";
import { Box, DialogContent, Typography } from "@mui/material";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { BCDesignTokens } from "epic.theme";
import { useModal } from "@/store/modalStore";
import {
  baseEnforcementSchema,
  getDefaultFormValues,
  ENFORCEMENT_MESSAGES,
} from "@/components/App/Inspections/Profile/Enforcements/EnforcementUtils";
import { useCreateViolationTicket } from "@/hooks/useViolationTickets";
import {
  ViolationTicket,
  ViolationTicketAPIData,
} from "@/models/ViolationTicket";
import { ViolationTicketStatus } from "@/utils/constants";
import { Inspection } from "@/models/Inspection";
import { notify } from "@/store/snackbarStore";
import ViolationTicketUpdateModal from "./ViolationTicketUpdateModal";
import { MODAL_WIDTHS } from "@/utils/constants";
const violationTicketSchema = baseEnforcementSchema.shape({
  ticket_number: yup.number().transform((value, originalValue) => {
    return originalValue === "" ? null : value;
  }).required("Ticket Number is required").integer("Ticket Number must be a whole number").positive("Ticket Number must be positive"),
});

type ViolationTicketFormType = yup.InferType<typeof violationTicketSchema>;

type ViolationTicketCreateModalProps = {
  inspectionData: Inspection;
  requirementsList: InspectionRequirement[];
  requirement?: InspectionRequirement;
  onSubmit: (data: ViolationTicket) => void;
};

const ViolationTicketCreateModal: FC<ViolationTicketCreateModalProps> = ({
  inspectionData,
  requirementsList,
  requirement,
  onSubmit,
}) => {
  const queryClient = useQueryClient();
  const { setOpen: setModalOpen, setClose: setModalClose } = useModal();

  const defaultValues = useMemo(() => {
    const baseValues = getDefaultFormValues(requirement, false);
    return {
      ...baseValues,
      ticket_number: undefined,
    };
  }, [requirement]);

  const methods = useForm<ViolationTicketFormType>({
    resolver: yupResolver(violationTicketSchema),
    mode: "onBlur",
    defaultValues,
  });

  const { reset, handleSubmit, watch } = methods;
  const selectedRequirements = watch("requirements") as InspectionRequirement[];

  useEffect(() => {
    reset(defaultValues);
  }, [reset, defaultValues]);

  const onSuccess = (data: ViolationTicket) => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-violation-tickets", inspectionData.id],
    });
    notify.success(ENFORCEMENT_MESSAGES.VIOLATION_TICKET_CREATED(data.vt_number || ""));

    setModalClose();

    setTimeout(() => {
      setModalOpen({
        content: (
          <ViolationTicketUpdateModal
            violationTicket={data}
            inspectionData={inspectionData}
            onSuccess={(updatedData) => {
              onSubmit(updatedData);
            }}
          />
        ),
        width: MODAL_WIDTHS.VIOLATION_TICKET
      });
    }, 100);
  };

  const { mutate: createViolationTicket, isPending: isPendingViolationTicket } =
    useCreateViolationTicket(onSuccess);

  const handleSubmitForm = useCallback(
    (data: ViolationTicketFormType) => {

      const violationTicketData: ViolationTicketAPIData = {
        inspection_id: inspectionData?.id ?? 0,
        inspection_requirement_ids: (
          data.requirements as InspectionRequirement[]
        ).map((requirement) => requirement.id),
        ticket_number: data.ticket_number?.toString() || "", // Convert number to string for API
      };

      createViolationTicket({
        violationTicket: violationTicketData,
      });
    },
    [createViolationTicket, inspectionData]
  );

  const handleCancel = () => {
    setModalClose();
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(handleSubmitForm)}>
        <ModalTitleBar title="Create Violation Ticket" />
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
            <ControlledTextField
              name="ticket_number"
              label="Ticket #"
              placeholder="Enter ticket number"
              type="number"
              fullWidth
              sx={{ mb: 2 }}
              inputProps={{
                min: 1,
                step: 1,
              }}
            />
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
                <strong>Note:</strong> You have selected multiple requirements. A single Violation Ticket will be created for all selected requirements.
              </Typography>
            </Box>
          )}
        </DialogContent>
        <ModalActions
          onSecondaryAction={handleCancel}
          onPrimaryAction={handleSubmit(handleSubmitForm)}
          isLoading={isPendingViolationTicket}
          primaryActionButtonText="Create"
          secondaryActionButtonText="Cancel"
        />
      </form>
    </FormProvider>
  );
};

export default ViolationTicketCreateModal;
