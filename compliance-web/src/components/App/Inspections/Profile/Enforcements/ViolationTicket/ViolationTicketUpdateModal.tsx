import { Box, DialogContent } from "@mui/material";
import { AttachMoneyRounded } from "@mui/icons-material";
import { FC, useCallback, useEffect, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import { useQueryClient } from "@tanstack/react-query";
import ModalTitleBar from "@/components/Shared/Modals/ModalTitleBar";
import ModalActions from "@/components/Shared/Modals/ModalActions";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";
import ControlledDateField from "@/components/Shared/Controlled/ControlledDateField";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";
import { useUpdateViolationTicket, useDeleteViolationTicket } from "@/hooks/useViolationTickets";
import {
  ViolationTicket,
  ViolationTicketAPIData,
} from "@/models/ViolationTicket";
import { ViolationTicketStatus } from "@/utils/constants";
import { Inspection } from "@/models/Inspection";
import { notify } from "@/store/snackbarStore";
import { useModal } from "@/store/modalStore";
import dayjs, { Dayjs } from "dayjs";

const violationTicketUpdateSchema = yup.object().shape({
  ticket_number: yup.string().required("Ticket Number is required"),
  date_issued: yup.mixed<Dayjs>().required("Date Issued is required").typeError("Invalid date"),
  fine_amount: yup.number().transform((value, originalValue) => {
    return originalValue === "" ? null : value;
  }).required("Fine Amount is required").min(0, "Fine Amount must be positive"),
  status: yup.mixed<StatusOption>().required("Status is required"),
  status_date: yup.mixed<Dayjs>().required("Status Date is required").typeError("Invalid date"),
});

type ViolationTicketUpdateFormType = yup.InferType<typeof violationTicketUpdateSchema> & {
  fine_amount?: number;
};

type StatusOption = {
  id: string;
  name: string;
};

const statusOptions: StatusOption[] = [
  { id: ViolationTicketStatus.ISSUED, name: "Issued" },
  { id: ViolationTicketStatus.PAID, name: "Paid" },
  { id: ViolationTicketStatus.DISPUTED, name: "Disputed" },
];

type ViolationTicketUpdateModalProps = {
  violationTicket: ViolationTicket;
  inspectionData: Inspection;
  onSuccess?: (data: ViolationTicket) => void;
  isReadonlyMode?: boolean;
};

const ViolationTicketUpdateModal: FC<ViolationTicketUpdateModalProps> = ({
  violationTicket,
  inspectionData,
  onSuccess,
  isReadonlyMode = false,
}) => {
  const queryClient = useQueryClient();
  const { setClose: setModalClose } = useModal();

  const defaultValues = useMemo(() => {
    const currentStatus = violationTicket.status?.id || "ISSUED";
    const selectedStatusOption = statusOptions.find(option => option.id === currentStatus) || statusOptions[0];

    return {
      ticket_number: violationTicket.ticket_number || "",
      date_issued: violationTicket.date_issued ? dayjs(violationTicket.date_issued) : undefined,
      fine_amount: violationTicket.fine_amount && violationTicket.fine_amount !== "" ? Number(violationTicket.fine_amount) : undefined,
      status: selectedStatusOption,
      status_date: violationTicket.status_date ? dayjs(violationTicket.status_date) : undefined,
    };
  }, [violationTicket]);

  const methods = useForm<ViolationTicketUpdateFormType>({
    resolver: yupResolver(violationTicketUpdateSchema),
    mode: "onBlur",
    defaultValues,
  });

  const { reset, handleSubmit } = methods;

  useEffect(() => {
    reset(defaultValues);
  }, [reset, defaultValues]);

  const onUpdateSuccess = (data: ViolationTicket) => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-violation-tickets", inspectionData.id],
    });
    notify.success("Violation Ticket updated successfully");
    onSuccess?.(data);
    setModalClose();
  };

  const { mutate: updateViolationTicket, isPending: isPendingUpdate } =
    useUpdateViolationTicket(onUpdateSuccess);

  const onDeleteSuccess = () => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-violation-tickets", inspectionData.id],
    });
    notify.success("Violation Ticket deleted successfully");
    onSuccess?.(violationTicket);
    setModalClose();
  };

  const { mutate: deleteViolationTicket, isPending: isPendingDelete } =
    useDeleteViolationTicket(onDeleteSuccess);

  const handleSubmitForm = useCallback(
    (data: ViolationTicketUpdateFormType) => {
      const updateData: ViolationTicketAPIData = {
        inspection_id: inspectionData?.id ?? 0,
        inspection_requirement_ids: violationTicket.violation_ticket_requirement_maps.map(
          (map) => map.inspection_requirement_id
        ),
        ticket_number: data.ticket_number,
        date_issued: data.date_issued.format("YYYY-MM-DDTHH:mm:ss.SSS[Z]"),
        fine_amount: data.fine_amount?.toString() || "",
        status: typeof data.status === 'string' ? data.status : data.status?.id || 'ISSUED',
        status_date: data.status_date.format("YYYY-MM-DDTHH:mm:ss.SSS[Z]"),
      };

      updateViolationTicket({
        violationTicketId: violationTicket.id,
        violationTicket: updateData,
      });
    },
    [updateViolationTicket, inspectionData, violationTicket]
  );

  const handleCancel = () => {
    setModalClose();
  };

  const handleDelete = () => {
    deleteViolationTicket({
      violationTicketId: violationTicket.id,
    });
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(handleSubmitForm)}>
        <ModalTitleBar title="Violation Ticket" />
        <DialogContent dividers sx={{ p: 0 }}>
          <Box sx={{ p: "1rem 1.5rem" }}>
            <Box sx={{ display: "flex", gap: 1 }}>
              <ControlledDateField
                name="date_issued"
                label="Date Issued"
                sx={{ width: "50%" }}
                isRequired={true}
                disabled={isReadonlyMode}
              />
              <ControlledTextField
                name="ticket_number"
                label="Ticket #"
                placeholder="Enter ticket number"
                sx={{ width: "100%" }}
                disabled
              />
            </Box>

            <Box sx={{ display: "flex", gap: 1 }}>
              <ControlledTextField
                name="fine_amount"
                label="Fine Amount"
                type="number"
                sx={{ width: "100%" }}
                inputProps={{
                  min: 0,
                  step: 0.01,
                }}
                InputProps={{
                  startAdornment: <AttachMoneyRounded sx={{
                    mr: 0.2,
                    color: "#9F9D9C",
                  }} />,
                }}
                isRequired={true}
                disabled={isReadonlyMode}
              />
              <ControlledAutoComplete
                name="status"
                label="Status"
                options={statusOptions}
                getOptionLabel={(option) => option.name}
                isOptionEqualToValue={(option, value) => option.id === value.id}
                placeholder="Select status"
                sx={{ width: "100%" }}
                disabled={isReadonlyMode}
              />
            </Box>
            <Box sx={{ display: "flex", gap: 1 }}>
              <ControlledDateField
                name="status_date"
                label="Status Date"
                sx={{ width: "100%" }}
                isRequired={true}
                disabled={isReadonlyMode}
              />
            </Box>
          </Box>
        </DialogContent>
        {!isReadonlyMode && (
          <ModalActions
            onSecondaryAction={handleCancel}
            onPrimaryAction={handleSubmit(handleSubmitForm)}
            isLoading={isPendingUpdate}
            primaryActionButtonText="Save"
            secondaryActionButtonText="Cancel"
            onDeleteAction={handleDelete}
            isDeleteActionLoading={isPendingDelete}
          />
        )}
      </form>
    </FormProvider>
  );
};

export default ViolationTicketUpdateModal;
