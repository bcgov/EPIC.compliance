import {
  Box,
  Button,
  Checkbox,
  DialogActions,
  DialogContent,
  FormControlLabel,
  Typography,
} from "@mui/material";
import { WarningAmberOutlined } from "@mui/icons-material";
import { BCDesignTokens } from "epic.theme";
import { FC, useCallback, useEffect, useMemo, useState } from "react";
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
  useAdministrativePenaltyLinksData,
} from "@/hooks/useAdministrativePenalties";
import {
  AdministrativePenalty,
  AdministrativePenaltyAPIData,
} from "@/models/AdministrativePenalty";
import { Inspection } from "@/models/Inspection";
import { notify } from "@/store/snackbarStore";
import { useModal } from "@/store/modalStore";
import dayjs, { Dayjs } from "dayjs";
import {
  APReferralStatus,
  APDecisionStatus,
  APJudicialReviewDecision,
  APJudicialReviewStatus,
} from "@/utils/constants";
import { KC_USER_GROUPS, useCurrentLoggedInUser, useIsRolesAllowed } from "@/hooks/useAuthorization";
import { useInspectionById } from "@/hooks/useInspections";

const administrativePenaltyUpdateSchema = yup.object().shape({
  referral_status: yup
    .mixed<ReferralStatusOption>()
    .required("Status is required"),
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
  is_jr: yup.boolean().default(false),
  jr_decision_date: yup
    .mixed<Dayjs>()
    .nullable()
    .typeError("Invalid date")
    .when("is_jr", {
      is: true,
      then: (schema) => schema.required("Decision Date is required"),
    }),
  jr_decision: yup.mixed<DecisionOption>().nullable(),
  jr_new_penalty_amount: yup
    .number()
    .transform((value) => (isNaN(value) ? undefined : value))
    .optional()
    .min(0, "New Penalty Amount must be positive"),
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

const jrDecisionOptions: DecisionOption[] = Object.values(
  APJudicialReviewDecision
);

// The AP's own fields; during a judicial review only a superuser can change them.
const AP_FORM_FIELDS = ["date_referred", "decision_date", "decision", "penalty_amount"] as const;

const JR_DISCARD_MESSAGE =
  "This will delete all Judicial Review information and restore the AP to its previous closed status.";
const JR_DISCARD_EDITED_MESSAGE =
  "JR information will be deleted. Changes to other AP fields will remain. Review these values before saving.";

const formatDate = (date?: Dayjs | null) =>
  date ? date.format("YYYY-MM-DDTHH:mm:ss.SSS[Z]") : undefined;

type AdministrativePenaltyUpdateModalProps = {
  administrativePenalty: AdministrativePenalty;
  inspectionData: Inspection;
  isPrimaryOfficerOrSuperUser: boolean;
  onSuccess?: (data: AdministrativePenalty) => void;
};

const AdministrativePenaltyUpdateModal: FC<
  AdministrativePenaltyUpdateModalProps
> = ({ administrativePenalty, inspectionData, isPrimaryOfficerOrSuperUser, onSuccess }) => {
  const queryClient = useQueryClient();
  const { setClose: setModalClose } = useModal();
  const isSuperUser = useIsRolesAllowed([KC_USER_GROUPS.SUPERUSER]);
  const savedInJr =
    administrativePenalty.referral_status?.id === APJudicialReviewStatus.id;
  // Ticked "subject to a judicial review" but not yet confirmed with Proceed.
  const [jrPending, setJrPending] = useState(false);
  // Unticked a saved JR; waiting for Yes, Discard / No, Keep.
  const [discardPending, setDiscardPending] = useState(false);

  // The API checks the JR against the AP's own inspection, which differs when viewed from a linked inspection.
  const isOwnInspection = administrativePenalty.inspection_id === inspectionData.id;
  const { data: fetchedApInspection } = useInspectionById(
    isOwnInspection ? 0 : administrativePenalty.inspection_id
  );
  const apInspection = isOwnInspection ? inspectionData : fetchedApInspection;
  const currentUser = useCurrentLoggedInUser();
  // The API also checks the page's inspection, since the requirement links are written against it.
  const canEditJr =
    isPrimaryOfficerOrSuperUser &&
    (isOwnInspection ||
      isSuperUser ||
      (!!currentUser?.preferred_username &&
        apInspection?.primary_officer?.auth_user_guid === currentUser.preferred_username));

  // JR can start on a closed AP Issued AP in an open case file, by the primary officer or a superuser.
  const canStartJr =
    !savedInJr &&
    administrativePenalty.is_closed &&
    administrativePenalty.referral_status?.id === APReferralStatus.REFERRED_TO_AEO.id &&
    administrativePenalty.decision?.id === APDecisionStatus.AP_ISSUED.id &&
    apInspection?.case_file?.case_file_status?.toLowerCase() === "open" &&
    canEditJr;

  const defaultValues = useMemo(() => {
    const currentReferralStatus =
      administrativePenalty.referral_status?.id ||
      APReferralStatus.PREPARING_REFERRAL_FOR_AEO.id;
    const selectedReferralOption = savedInJr
      ? APJudicialReviewStatus
      : referralStatusOptions.find(
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
      is_jr: savedInJr,
      jr_decision_date: administrativePenalty.jr_decision_date
        ? dayjs(administrativePenalty.jr_decision_date)
        : (undefined as unknown as Dayjs),
      jr_decision:
        jrDecisionOptions.find(
          (option) => option.id === administrativePenalty.jr_decision?.id
        ) || null,
      jr_new_penalty_amount:
        administrativePenalty.jr_new_penalty_amount != null
          ? Number(administrativePenalty.jr_new_penalty_amount)
          : undefined,
    };
  }, [administrativePenalty, savedInJr]);

  const methods = useForm<AdministrativePenaltyUpdateFormType>({
    resolver: yupResolver(administrativePenaltyUpdateSchema),
    mode: "onBlur",
    defaultValues,
  });

  const { reset, handleSubmit, watch, setValue, getFieldState } = methods;
  const decision = watch("decision");
  const referralStatus = watch("referral_status");
  const isJr = watch("is_jr");
  const penaltyAmount = watch("penalty_amount");
  const jrDecisionDate = watch("jr_decision_date");
  const jrDecision = watch("jr_decision");
  const jrNewPenaltyAmount = watch("jr_new_penalty_amount");
  const jrInProgress = isJr && !jrPending && !administrativePenalty.is_jr_complete;

  // Calculate readonly mode based on inspection status and administrative penalty status
  const isReadonlyMode = useMemo(() => {
    if (jrInProgress) {
      return !canEditJr;
    }
    if (administrativePenalty.is_closed) {
      return !isSuperUser;
    }
    return !isPrimaryOfficerOrSuperUser;
  }, [jrInProgress, canEditJr, administrativePenalty.is_closed, isPrimaryOfficerOrSuperUser, isSuperUser]);
  const apFieldsReadonly = isReadonlyMode || ((savedInJr || isJr) && !isSuperUser);
  const { dirtyFields } = methods.formState;
  const apFieldsEdited = AP_FORM_FIELDS.some((field) => dirtyFields[field]);

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

  // JR amount rules: Reversed is 0, Upheld keeps the penalty amount, the others default to 0.
  // Only Upheld follows the penalty amount; editing it must not reset an amount typed for the others.
  useEffect(() => {
    if (!isJr || !jrDecision || jrDecision.id === APJudicialReviewDecision.UPHELD.id) return;
    if (
      jrDecision.id === APJudicialReviewDecision.REVERSED.id ||
      getFieldState("jr_decision").isDirty
    ) {
      setValue("jr_new_penalty_amount", 0);
    }
  }, [isJr, jrDecision, setValue, getFieldState]);
  useEffect(() => {
    if (isJr && jrDecision?.id === APJudicialReviewDecision.UPHELD.id) {
      setValue("jr_new_penalty_amount", Number(penaltyAmount) || 0);
    }
  }, [isJr, jrDecision, penaltyAmount, setValue]);
  const jrAmountLocked =
    jrDecision?.id === APJudicialReviewDecision.REVERSED.id ||
    jrDecision?.id === APJudicialReviewDecision.UPHELD.id;

  const handleJrCheckbox = (checked: boolean) => {
    if (checked && savedInJr) {
      // Re-ticked after a discard: back to the saved JR.
      reset(defaultValues);
    } else if (checked) {
      setValue("is_jr", true);
      setJrPending(true);
    } else if (savedInJr) {
      setDiscardPending(true);
    } else {
      reset(defaultValues);
      setJrPending(false);
    }
  };

  const handleJrDiscard = () => {
    setValue("is_jr", false);
    setValue("referral_status", APReferralStatus.REFERRED_TO_AEO);
    setValue("jr_decision_date", undefined as unknown as Dayjs);
    setValue("jr_decision", null);
    setValue("jr_new_penalty_amount", undefined);
    setDiscardPending(false);
  };

  const handleJrProceed = () => {
    setValue("referral_status", APJudicialReviewStatus);
    setJrPending(false);
  };

  // Determine if save confirmation is required
  const requireSaveConfirmation = useMemo(() => {
    if (isJr) {
      return (
        !!jrDecisionDate &&
        !!jrDecision &&
        jrNewPenaltyAmount != null &&
        String(jrNewPenaltyAmount) !== ""
      );
    }
    const isAPNotProceeding =
      referralStatus?.id === APReferralStatus.AP_NOT_PROCEEDING.id;
    const isReferredToAEOWithDecision =
      referralStatus?.id === APReferralStatus.REFERRED_TO_AEO.id &&
      decision !== null;

    return isAPNotProceeding || isReferredToAEOWithDecision;
  }, [isJr, jrDecisionDate, jrDecision, jrNewPenaltyAmount, referralStatus, decision]);

  const onUpdateSuccess = (data: AdministrativePenalty) => {
    //  Invalidate all administrative penalties because of the AP can be linked to
    //  other inspections
    queryClient.invalidateQueries({
      queryKey: ["inspection-administrative-penalties"],
    });
    queryClient.invalidateQueries({
      queryKey: ["administrative-penalty-links"]
    })
    notify.success("Administrative Penalty updated successfully");
    onSuccess?.(data);
    setModalClose();
  };

  const { mutate: updateAdministrativePenalty, isPending: isPendingUpdate } =
    useUpdateAdministrativePenalty(onUpdateSuccess);

  const onDeleteSuccess = () => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-administrative-penalties"],
    });
    queryClient.invalidateQueries({
      queryKey: ["administrative-penalty-links"]
    })
    notify.success("Administrative Penalty deleted successfully");
    onSuccess?.(administrativePenalty);
    setModalClose();
  };

  const { mutate: deleteAdministrativePenalty, isPending: isPendingDelete } =
    useDeleteAdministrativePenalty(onDeleteSuccess);

  // Fetch linked inspections and requirements for this AP
  const { data: linkedData } = useAdministrativePenaltyLinksData(administrativePenalty.id);

  // Check if AP is linked to other inspections by comparing inspection IDs
  const isLinkedToOtherInspections = useMemo(()=>{
    const isParent = administrativePenalty.inspection_id == inspectionData.id;
    return (linkedData?.some(
        (linkData) => linkData.inspection.id !== inspectionData.id
    ) ?? false) && isParent;
  }, [linkedData, inspectionData, administrativePenalty]);

  const handleSubmitForm = useCallback(
    (data: AdministrativePenaltyUpdateFormType) => {
      const updateData: AdministrativePenaltyAPIData = {
        inspection_id: inspectionData?.id ?? 0,
        inspection_requirement_ids:
          administrativePenalty.administrative_penalty_requirement_maps
          .filter((ap_map) => ap_map.inspection_requirement.inspection_id === inspectionData.id)
          .map(
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

      if (data.is_jr) {
        updateData.referral_status = APJudicialReviewStatus.id;
        updateData.jr_decision_date = formatDate(data.jr_decision_date);
        updateData.jr_decision = data.jr_decision?.id;
        if (data.jr_new_penalty_amount != null) {
          updateData.jr_new_penalty_amount = Number(data.jr_new_penalty_amount);
        }
        updateData.jr_ap_fields_edited = apFieldsEdited;
      }

      updateAdministrativePenalty({
        administrativePenaltyId: administrativePenalty.id,
        administrativePenalty: updateData,
      });
    },
    [updateAdministrativePenalty, inspectionData, administrativePenalty, apFieldsEdited]
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
              label="Status"
              options={
                isJr && !jrPending ? [APJudicialReviewStatus] : referralStatusOptions
              }
              getOptionLabel={(option) => option.name}
              isOptionEqualToValue={(option, value) => option.id === value.id}
              placeholder="Select status"
              fullWidth
              disabled={isReadonlyMode || isJr || savedInJr}
            />
            <Box sx={{ display: "flex", gap: 1 }}>
              <ControlledDateField
                name="date_referred"
                label="Date Referred to AEO"
                sx={{ width: "100%" }}
                disabled={apFieldsReadonly}
              />
              <ControlledDateField
                name="decision_date"
                label="DM Decision Date"
                sx={{ width: "100%" }}
                disabled={apFieldsReadonly}
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
              disabled={apFieldsReadonly}
            />
            {decision?.id === "AP_ISSUED" && (
              <ControlledTextField
                name="penalty_amount"
                label="Penalty Amount"
                placeholder="Enter penalty amount"
                type={apFieldsReadonly ? "text" : "number"}
                {...(apFieldsReadonly && { value: formatAmount(penaltyAmount) })}
                fullWidth
                disabled={apFieldsReadonly}
              />
            )}
            {(canStartJr || savedInJr) && (
              <Box
                sx={{
                  backgroundColor: BCDesignTokens.surfaceColorBackgroundLightBlue,
                  borderRadius: "4px",
                  p: "1rem 1rem 0 1rem",
                }}
              >
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={!!isJr}
                      onChange={(event) => handleJrCheckbox(event.target.checked)}
                      disabled={savedInJr ? isReadonlyMode : !canStartJr}
                      sx={{ paddingY: 0 }}
                      data-testid="jr-checkbox"
                    />
                  }
                  label="This AP was subject to a judicial review"
                  sx={{
                    mb: "1rem",
                    "& .MuiFormControlLabel-label": {
                      fontWeight: isJr && !jrPending ? "bold" : "normal",
                    },
                  }}
                />
                {isJr && !jrPending && (
                  <>
                    <Box sx={{ display: "flex", gap: 1 }}>
                      <Box sx={{ flex: "0 0 40%" }}>
                        <ControlledDateField
                          name="jr_decision_date"
                          label="Decision Date"
                          disabled={isReadonlyMode}
                        />
                      </Box>
                      <ControlledAutoComplete
                        name="jr_decision"
                        label="Decision"
                        options={jrDecisionOptions}
                        getOptionLabel={(option) => option.name}
                        isOptionEqualToValue={(option, value) => option.id === value.id}
                        placeholder="Select an option..."
                        fullWidth
                        disabled={isReadonlyMode}
                      />
                    </Box>
                    <ControlledTextField
                      name="jr_new_penalty_amount"
                      label="New Penalty Amount"
                      placeholder="0"
                      type={isReadonlyMode || jrAmountLocked ? "text" : "number"}
                      {...((isReadonlyMode || jrAmountLocked) && {
                        value: formatAmount(jrNewPenaltyAmount),
                      })}
                      fullWidth
                      disabled={isReadonlyMode || jrAmountLocked}
                    />
                  </>
                )}
              </Box>
            )}
          </Box>
        </DialogContent>
        {jrPending && (
          <WarningBar
            message="Note: Checking this reopens the AP to record a judicial review outcome and sets its status to Judicial Review. The original decision is kept; uncheck to cancel before completing the review."
            secondaryText="Cancel"
            onSecondary={() => handleJrCheckbox(false)}
            primaryText="Proceed"
            onPrimary={handleJrProceed}
          />
        )}
        {discardPending && (
          <Box
            sx={{
              background: BCDesignTokens.supportSurfaceColorDanger,
              borderTop: `${BCDesignTokens.layoutBorderWidthSmall} solid ${BCDesignTokens.surfaceColorBorderDefault}`,
              padding: ".5rem 1.5rem",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
            }}
          >
            <Box sx={{ display: "flex", flexDirection: "column", flex: 1 }}>
              <Typography variant="body1" fontWeight="bold">
                Discard Judicial Review?
              </Typography>
              <Typography variant="body1">
                {administrativePenalty.jr_ap_fields_edited || apFieldsEdited
                  ? JR_DISCARD_EDITED_MESSAGE
                  : JR_DISCARD_MESSAGE}
              </Typography>
            </Box>
            <Button
              sx={{ minWidth: 100, height: 40 }}
              color="secondary"
              onClick={() => setDiscardPending(false)}
            >
              No, Keep
            </Button>
            <Button
              sx={{ minWidth: 100, height: 40 }}
              color="error"
              onClick={handleJrDiscard}
            >
              Yes, Discard
            </Button>
          </Box>
        )}
        {!isReadonlyMode && !jrPending && !discardPending && (
          <ModalActions
            onSecondaryAction={handleCancel}
            onPrimaryAction={handleSubmit(handleSubmitForm)}
            isLoading={isPendingUpdate}
            primaryActionButtonText="Save"
            secondaryActionButtonText="Cancel"
            onDeleteAction={isJr || savedInJr ? undefined : handleDelete}
            isDeleteActionLoading={isPendingDelete}
            onDeleteConfirmationText={
              isLinkedToOtherInspections
                ? "This AP is linked to other files. Deleting it will remove all linked APs."
                : undefined
            }
            requireSaveConfirmation={requireSaveConfirmation}
          />
        )}
      </form>
    </FormProvider>
  );
};

// Disabled amount fields show thousands separators ("1,000"); editable ones stay plain numbers.
const formatAmount = (value: unknown) =>
  value === "" || value == null || isNaN(Number(value))
    ? ""
    : Number(value).toLocaleString("en-CA", { maximumFractionDigits: 2 });

type WarningBarProps = {
  message: string;
  secondaryText: string;
  onSecondary: () => void;
  primaryText: string;
  onPrimary: () => void;
};

// Yellow note with two buttons, shown in place of the modal actions.
const WarningBar: FC<WarningBarProps> = ({
  message,
  secondaryText,
  onSecondary,
  primaryText,
  onPrimary,
}) => (
  <>
    <Box
      sx={{
        display: "flex",
        gap: 1,
        p: "1rem 1.5rem",
        backgroundColor: BCDesignTokens.supportSurfaceColorWarning,
        borderTop: `1px solid ${BCDesignTokens.supportBorderColorWarning}`,
        borderBottom: `1px solid ${BCDesignTokens.supportBorderColorWarning}`,
      }}
    >
      <WarningAmberOutlined sx={{ color: BCDesignTokens.iconsColorWarning }} />
      <Typography variant="body2">{message}</Typography>
    </Box>
    <DialogActions sx={{ padding: "1rem 1.5rem" }}>
      <Button variant="text" onClick={onSecondary}>
        {secondaryText}
      </Button>
      <Button variant="contained" onClick={onPrimary}>
        {primaryText}
      </Button>
    </DialogActions>
  </>
);

export default AdministrativePenaltyUpdateModal;
