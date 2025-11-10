import { FC, useCallback, useEffect, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import { useQueryClient } from "@tanstack/react-query";
import EnforcementModal from "@/components/App/Inspections/Profile/Enforcements/EnforcementModal";
import {
  baseEnforcementSchema,
  getDefaultFormValues,
  ENFORCEMENT_MESSAGES,
  BaseEnforcementFormType,
} from "@/components/App/Inspections/Profile/Enforcements/EnforcementUtils";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";
import { useCreateViolationTicket } from "@/hooks/useViolationTickets";
import {
  ViolationTicket,
  ViolationTicketAPIData,
} from "@/models/ViolationTicket";
import { Inspection } from "@/models/Inspection";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { notify } from "@/store/snackbarStore";

const violationTicketSchema = baseEnforcementSchema.shape({
  ticket_number: yup.string().required("Ticket Number is required").trim(),
});

type ViolationTicketFormType = yup.InferType<typeof violationTicketSchema>;

const ViolationTicketFormFields = () => {
  return (
    <ControlledTextField
      name="ticket_number"
      label="Ticket #"
      placeholder="Enter ticket number"
      type="text"
      fullWidth
      isRequired={true}
      sx={{ mt: 2 }}
    />
  );
};

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

  const defaultValues = useMemo(() => {
    const baseValues = getDefaultFormValues(requirement, false, undefined);
    return {
      ...baseValues,
      ticket_number: "",
    };
  }, [requirement]);

  const methods = useForm<ViolationTicketFormType>({
    resolver: yupResolver(violationTicketSchema),
    mode: "onBlur",
    defaultValues,
  });

  const { reset } = methods;

  useEffect(() => {
    reset(defaultValues);
  }, [reset, defaultValues]);

  const onSuccess = (data: ViolationTicket) => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-violation-tickets", inspectionData.id],
    });
    queryClient.invalidateQueries({
      queryKey: ["pending-items", inspectionData.id],
    });
    notifyAndSubmit(data);
  };

  const notifyAndSubmit = (data: ViolationTicket) => {
    notify.success(ENFORCEMENT_MESSAGES.VIOLATION_TICKET_CREATED(data.vt_number || ""));
    onSubmit(data);
  };

  const { mutate: createViolationTicket, isPending: isPendingViolationTicket } =
    useCreateViolationTicket(onSuccess);



  const handleBaseSubmit = useCallback(
    (data: BaseEnforcementFormType, additionalData?: Record<string, unknown>) => {
      const ticketNumber = (additionalData?.ticket_number as string) || "";
      

      if (!ticketNumber || ticketNumber.trim() === "") {
        notify.error("Ticket Number is required");
        return;
      }
      
      const violationTicketData: ViolationTicketAPIData = {
        inspection_id: inspectionData?.id ?? 0,
        inspection_requirement_ids: (data.requirements as InspectionRequirement[]).map((requirement) => requirement.id),
        ticket_number: ticketNumber.trim(),
      };

      createViolationTicket({
        violationTicket: violationTicketData,
      });
    },
    [createViolationTicket, inspectionData]
  );

  return (
    <FormProvider {...methods}>
      <EnforcementModal
        requirementsList={requirementsList}
        requirement={requirement}
        title="Create Violation Ticket"
        onSubmit={handleBaseSubmit}
        isLoading={isPendingViolationTicket}
        additionalFormFields={<ViolationTicketFormFields />}
      />
    </FormProvider>
  );
};

export default ViolationTicketCreateModal;
