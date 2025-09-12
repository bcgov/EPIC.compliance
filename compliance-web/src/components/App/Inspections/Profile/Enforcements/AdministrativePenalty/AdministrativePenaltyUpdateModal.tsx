import { Box, DialogContent } from "@mui/material";
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
import {
  useUpdateAdministrativePenalty,
  useDeleteAdministrativePenalty,
} from "@/hooks/useAdministrativePenalties";
import {
  AdministrativePenalty,
  AdministrativePenaltyAPIData,
} from "@/models/AdministrativePenalty";
import { Inspection } from "@/models/Inspection";
import { notify } from "@/store/snackbarStore";
import { useModal } from "@/store/modalStore";
import dayjs, { Dayjs } from "dayjs";
import { APReferralStatus, APDecisionStatus } from "@/utils/constants";

const administrativePenaltyUpdateSchema = yup.object().shape({
  referral_status: yup
    .mixed<ReferralStatusOption>()
    .required("Referral Status is required"),
  date_referred: yup.mixed<Dayjs>().nullable().typeError("Invalid date"),
  decision_date: yup.mixed<Dayjs>().nullable().typeError("Invalid date"),
  decision: yup.mixed<DecisionOption>().nullable(),
  penalty_amount: yup
    .number()
    .transform((value) => (isNaN(value) ? undefined : value))
    .optional()
    .when("decision", {
      is: (decision: DecisionOption) => decision?.id === "AP_ISSUED",
      then: (schema) =>
        schema
          .required("Penalty Amount is required when AP is issued")
          .min(0, "Penalty Amount must be positive"),
      otherwise: (schema) => schema.optional(),
    }),
});

type AdministrativePenaltyUpdateFormType = yup.InferType<
  typeof administrativePenaltyUpdateSchema
>;

type ReferralStatusOption = {
  id: string;
  name: string;
};

type DecisionOption = {
  id: string;
  name: string;
};

const referralStatusOptions: ReferralStatusOption[] = Object.values(
  APReferralStatus
).map((status) => ({
  id: status.id,
  name: status.name,
}));

const decisionOptions: DecisionOption[] = Object.values(APDecisionStatus).map(
  (decision) => ({
    id: decision.id,
    name: decision.name,
  })
);

type AdministrativePenaltyUpdateModalProps = {
  administrativePenalty: AdministrativePenalty;
  inspectionData: Inspection;
  onSuccess?: (data: AdministrativePenalty) => void;
  isReadonlyMode?: boolean;
};

const AdministrativePenaltyUpdateModal: FC<
  AdministrativePenaltyUpdateModalProps
> = ({ administrativePenalty, inspectionData, onSuccess, isReadonlyMode = false }) => {
  const queryClient = useQueryClient();
  const { setClose: setModalClose } = useModal();

  const defaultValues = useMemo(() => {
    const currentReferralStatus =
      administrativePenalty.referral_status?.id || "DRAFTING";
    const selectedReferralOption =
      referralStatusOptions.find(
        (option) => option.id === currentReferralStatus
      ) || referralStatusOptions[0];

    const currentDecision = administrativePenalty.decision?.id || "";
    const selectedDecisionOption =
      decisionOptions.find((option) => option.id === currentDecision) || null;

    return {
      referral_status: selectedReferralOption,
      date_referred: administrativePenalty.date_referred
        ? dayjs(administrativePenalty.date_referred)
        : (undefined as unknown as Dayjs),
      decision_date: administrativePenalty.decision_date
        ? dayjs(administrativePenalty.decision_date)
        : (undefined as unknown as Dayjs),
      decision: selectedDecisionOption,
      penalty_amount: administrativePenalty.penalty_amount
        ? Number(administrativePenalty.penalty_amount)
        : 0,
    };
  }, [administrativePenalty]);

  const methods = useForm<AdministrativePenaltyUpdateFormType>({
    resolver: yupResolver(administrativePenaltyUpdateSchema),
    mode: "onBlur",
    defaultValues,
  });

  const { reset, handleSubmit, watch } = methods;
  const decision = watch("decision");

  useEffect(() => {
    reset(defaultValues);
  }, [reset, defaultValues]);

  useEffect(() => {
    if (decision?.id === "AP_NOT_PROCEEDING") {
      methods.setValue("penalty_amount", 0);
    } else if (decision?.id === "AP_ISSUED") {
      // Ensure penalty_amount has a valid value when AP_ISSUED is selected
      const currentValue = methods.getValues("penalty_amount");
      if (currentValue === null || currentValue === undefined) {
        methods.setValue("penalty_amount", 0);
      }
    }
  }, [decision, methods]);

  const onUpdateSuccess = (data: AdministrativePenalty) => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-administrative-penalties", inspectionData.id],
    });
    notify.success("Administrative Penalty updated successfully");
    onSuccess?.(data);
    setModalClose();
  };

  const { mutate: updateAdministrativePenalty, isPending: isPendingUpdate } =
    useUpdateAdministrativePenalty(onUpdateSuccess);

  const onDeleteSuccess = () => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-administrative-penalties", inspectionData.id],
    });
    notify.success("Administrative Penalty deleted successfully");
    onSuccess?.(administrativePenalty);
    setModalClose();
  };

  const { mutate: deleteAdministrativePenalty, isPending: isPendingDelete } =
    useDeleteAdministrativePenalty(onDeleteSuccess);

  // Check if AP is linked to other inspections
  const isLinkedToOtherInspections = administrativePenalty.inspection_id !== inspectionData.id;

  const handleSubmitForm = useCallback(
    (data: AdministrativePenaltyUpdateFormType) => {
      const updateData: AdministrativePenaltyAPIData = {
        inspection_id: inspectionData?.id ?? 0,
        inspection_requirement_ids:
          administrativePenalty.administrative_penalty_requirement_maps.map(
            (map) => map.inspection_requirement_id
          ),
        referral_status:
          typeof data.referral_status === "string"
            ? data.referral_status
            : data.referral_status?.id || "",
      };

      if (data.date_referred) {
        updateData.date_referred = data.date_referred.format(
          "YYYY-MM-DDTHH:mm:ss.SSS[Z]"
        );
      }

      if (data.decision_date) {
        updateData.decision_date = data.decision_date.format(
          "YYYY-MM-DDTHH:mm:ss.SSS[Z]"
        );
      }

      if (data.decision) {
        updateData.decision =
          typeof data.decision === "string"
            ? data.decision
            : data.decision?.id || "";
      }

      if (data.decision) {
        const decisionId =
          typeof data.decision === "string"
            ? data.decision
            : data.decision?.id || "";
        if (decisionId === "AP_ISSUED") {
          if (data.penalty_amount && !isNaN(Number(data.penalty_amount))) {
            updateData.penalty_amount = Number(data.penalty_amount);
          }
        } else if (decisionId === "AP_NOT_PROCEEDING") {
          updateData.penalty_amount = 0;
        }
      }

      updateAdministrativePenalty({
        administrativePenaltyId: administrativePenalty.id,
        administrativePenalty: updateData,
      });
    },
    [updateAdministrativePenalty, inspectionData, administrativePenalty]
  );

  const handleCancel = () => {
    setModalClose();
  };

  const handleDelete = () => {
    deleteAdministrativePenalty({
      administrativePenaltyId: administrativePenalty.id,
      inspectionId: inspectionData.id,
    });
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(handleSubmitForm)}>
        <ModalTitleBar title={administrativePenalty.administrative_penalty_number} />
        <DialogContent dividers sx={{ p: 0 }}>
          <Box sx={{ p: "1rem 1.5rem" }}>
            <ControlledAutoComplete
              name="referral_status"
              label="Referral Status"
              options={referralStatusOptions}
              getOptionLabel={(option) => option.name}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              placeholder="Select referral status"
              fullWidth
              disabled={isReadonlyMode}
            />
            <Box sx={{ display: "flex", gap: 1 }}>
              <ControlledDateField
                name="date_referred"
                label="Date Referred to Decision Maker"
                sx={{ width: "100%" }}
                disabled={isReadonlyMode}
              />
              <ControlledDateField
                name="decision_date"
                label="Decision Date"
                sx={{ width: "100%" }}
                disabled={isReadonlyMode}
              />
            </Box>
            <ControlledAutoComplete
              name="decision"
              label="DM Decision"
              options={decisionOptions}
              getOptionLabel={(option) => option.name}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              placeholder="Select an option..."
              fullWidth
              disabled={isReadonlyMode}
            />
            {decision?.id === "AP_ISSUED" && (
              <ControlledTextField
                name="penalty_amount"
                label="Penalty Amount"
                placeholder="Enter penalty amount"
                type="number"
                fullWidth
                disabled={isReadonlyMode}
              />
            )}
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
            onDeleteConfirmationText={
              isLinkedToOtherInspections
                ? "This AP is linked to other files. Deleting it will remove all linked APs."
                : undefined
            }
          />
        )}
      </form>
    </FormProvider>
  );
};

export default AdministrativePenaltyUpdateModal;
