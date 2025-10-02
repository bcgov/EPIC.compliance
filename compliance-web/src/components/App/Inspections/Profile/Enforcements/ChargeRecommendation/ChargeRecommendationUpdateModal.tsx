import { DialogContent, Box } from "@mui/material";
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
  useUpdateChargeRecommendation,
  useDeleteChargeRecommendation,
} from "@/hooks/useChargeRecommendations";
import {
  ChargeRecommendation,
  ChargeRecommendationAPIData,
} from "@/models/ChargeRecommendation";
import { Inspection } from "@/models/Inspection";
import { notify } from "@/store/snackbarStore";
import { useModal } from "@/store/modalStore";
import { CRStatus, CRDecision, CRJudgment } from "@/utils/constants";
import dayjs, { Dayjs } from "dayjs";

const chargeRecommendationUpdateSchema = yup.object().shape({
  status: yup.mixed<StatusOption>().required("Status is required"),
  date_to_crown_counsel: yup
    .mixed<Dayjs>()
    .nullable()
    .typeError("Invalid date"),
  charge_decision: yup.mixed<DecisionOption>().nullable(),
  charge_decision_date: yup.mixed<Dayjs>().nullable().typeError("Invalid date"),
  court_file_number: yup.string().nullable(),
  court_appearances: yup.string().nullable(),
  judgment: yup.mixed<JudgmentOption>().nullable(),
  judgment_date: yup.mixed<Dayjs>().nullable().typeError("Invalid date"),
  sentence_date: yup.mixed<Dayjs>().nullable().typeError("Invalid date"),
  sentence_type: yup.string().nullable(),
});

type ChargeRecommendationUpdateFormType = yup.InferType<
  typeof chargeRecommendationUpdateSchema
>;

type StatusOption = {
  id: string;
  name: string;
};

type DecisionOption = {
  id: string;
  name: string;
};

type JudgmentOption = {
  id: string;
  name: string;
};

const statusOptions: StatusOption[] = Object.values(CRStatus).map((status) => ({
  id: status.id,
  name: status.name,
}));

const decisionOptions: DecisionOption[] = Object.values(CRDecision).map(
  (decision) => ({
    id: decision.id,
    name: decision.name,
  })
);

const judgmentOptions: JudgmentOption[] = Object.values(CRJudgment).map(
  (judgment) => ({
    id: judgment.id,
    name: judgment.name,
  })
);

type ChargeRecommendationUpdateModalProps = {
  chargeRecommendationData: ChargeRecommendation;
  inspectionData: Inspection;
  onSubmit: (data: ChargeRecommendation) => void;
  isReadonlyMode?: boolean;
};

const ChargeRecommendationUpdateModal: FC<
  ChargeRecommendationUpdateModalProps
> = ({ chargeRecommendationData, inspectionData, onSubmit, isReadonlyMode = false }) => {
  const queryClient = useQueryClient();
  const { setClose: setModalClose } = useModal();

  const defaultValues = useMemo(() => {
    const currentStatus = chargeRecommendationData.status || CRStatus.DRAFTING;
    const selectedStatusOption =
      statusOptions.find((option) => option.id === currentStatus?.id) ||
      statusOptions[0];

    const currentDecision = chargeRecommendationData.charge_decision;
    const selectedDecisionOption =
      decisionOptions.find((option) => option.id === currentDecision?.id) ||
      null;

    const currentJudgment = chargeRecommendationData.judgment;
    const selectedJudgmentOption =
      judgmentOptions.find((option) => option.id === currentJudgment?.id) ||
      null;

    return {
      status: selectedStatusOption,
      date_to_crown_counsel: chargeRecommendationData.date_to_crown_counsel
        ? dayjs(chargeRecommendationData.date_to_crown_counsel)
        : null,
      charge_decision: selectedDecisionOption,
      charge_decision_date: chargeRecommendationData.charge_decision_date
        ? dayjs(chargeRecommendationData.charge_decision_date)
        : null,
      court_file_number: chargeRecommendationData.court_file_number || "",
      court_appearances: chargeRecommendationData.court_appearances || "",
      judgment: selectedJudgmentOption,
      judgment_date: chargeRecommendationData.judgment_date
        ? dayjs(chargeRecommendationData.judgment_date)
        : null,
      sentence_date: chargeRecommendationData.sentence_date
        ? dayjs(chargeRecommendationData.sentence_date)
        : null,
      sentence_type: chargeRecommendationData.sentence_type || "",
    };
  }, [chargeRecommendationData]);

  const methods = useForm<ChargeRecommendationUpdateFormType>({
    resolver: yupResolver(chargeRecommendationUpdateSchema),
    mode: "onBlur",
    defaultValues,
  });

  const onUpdateSuccess = (
    updatedChargeRecommendation: ChargeRecommendation
  ) => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-charge-recommendations", inspectionData.id],
    });
    notify.success(
      `Charge Recommendation ${updatedChargeRecommendation.charge_recommendation_number || ""} updated successfully`
    );
    onSubmit(updatedChargeRecommendation);
    setModalClose();
  };

  const { mutate: updateChargeRecommendation, isPending: isUpdating } =
    useUpdateChargeRecommendation(onUpdateSuccess);
  const onDeleteSuccess = () => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-charge-recommendations", inspectionData.id],
    });
    notify.success("Charge Recommendation deleted successfully");
    setModalClose();
  };

  const { mutate: deleteChargeRecommendation, isPending: isDeleting } =
    useDeleteChargeRecommendation(onDeleteSuccess);

  const handleSubmit = useCallback(
    (data: ChargeRecommendationUpdateFormType) => {
      const updateData: Partial<ChargeRecommendationAPIData> = {
        inspection_id: inspectionData.id,
        inspection_requirement_ids:
          chargeRecommendationData.charge_recommendation_requirement_maps
            .map((map) => map.inspection_requirement_id)
            .filter((id) => id != null),
      };

      if (data.status?.id) {
        updateData.status = data.status.id;
      }

      if (data.date_to_crown_counsel) {
        updateData.date_to_crown_counsel = data.date_to_crown_counsel.format(
          "YYYY-MM-DDTHH:mm:ss.SSS[Z]"
        );
      }

      if (data.charge_decision?.id) {
        updateData.charge_decision = data.charge_decision.id;
      }

      if (data.charge_decision_date) {
        updateData.charge_decision_date = data.charge_decision_date.format(
          "YYYY-MM-DDTHH:mm:ss.SSS[Z]"
        );
      }

      if (data.court_file_number) {
        updateData.court_file_number = data.court_file_number;
      }

      if (data.court_appearances) {
        updateData.court_appearances = data.court_appearances;
      }

      if (data.judgment?.id) {
        updateData.judgment = data.judgment.id;
      }

      if (data.judgment_date) {
        updateData.judgment_date = data.judgment_date.format(
          "YYYY-MM-DDTHH:mm:ss.SSS[Z]"
        );
      }

      if (data.sentence_date) {
        updateData.sentence_date = data.sentence_date.format(
          "YYYY-MM-DDTHH:mm:ss.SSS[Z]"
        );
      }

      if (data.sentence_type) {
        updateData.sentence_type = data.sentence_type;
      }

      updateChargeRecommendation({
        chargeRecommendationId: chargeRecommendationData.id,
        chargeRecommendation: updateData as ChargeRecommendationAPIData,
      });
    },
    [
      inspectionData.id,
      chargeRecommendationData.id,
      chargeRecommendationData.charge_recommendation_requirement_maps,
      updateChargeRecommendation,
    ]
  );

  const handleDelete = useCallback(() => {
    deleteChargeRecommendation({
      chargeRecommendationId: chargeRecommendationData.id,
    });
  }, [deleteChargeRecommendation, chargeRecommendationData.id]);

  useEffect(() => {
    methods.reset(defaultValues);
  }, [defaultValues, methods]);

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(handleSubmit)}>
        <ModalTitleBar
          title={`${chargeRecommendationData.charge_recommendation_number}`}
          onClose={setModalClose}
          titleVariant="h6"
        />
        <DialogContent dividers sx={{ p: "1rem 1.5rem" }}>
          <Box sx={{ display: "flex", flexDirection: "column" }}>
            <ControlledAutoComplete
              name="status"
              label="Status"
              options={statusOptions}
              getOptionLabel={(option) => option?.name || ""}
              isOptionEqualToValue={(option, value) => option?.id === value?.id}
              isRequired={true}
              disabled={isReadonlyMode}
            />

            <Box sx={{ display: "flex", gap: 2 }}>
              <ControlledDateField
                name="date_to_crown_counsel"
                label="Date to Crown Counsel"
                disabled={isReadonlyMode}
              />
              <ControlledTextField
                name="court_file_number"
                label="Court File #"
                fullWidth
                disabled={isReadonlyMode}
              />
            </Box>

            <Box sx={{ display: "flex", gap: 2 }}>
              <ControlledAutoComplete
                name="charge_decision"
                label="Charge Decision"
                options={decisionOptions}
                getOptionLabel={(option) => option?.name || ""}
                isOptionEqualToValue={(option, value) =>
                  option?.id === value?.id
                }
                fullWidth
                disabled={isReadonlyMode}
              />
              <ControlledDateField
                name="charge_decision_date"
                label="Charge Decision Date"
                disabled={isReadonlyMode}
              />
            </Box>

            <ControlledTextField
              name="court_appearances"
              label="Court Appearances"
              multiline
              rows={1}
              fullWidth
              disabled={isReadonlyMode}
            />

            <Box sx={{ display: "flex", gap: 2 }}>
              <ControlledAutoComplete
                name="judgment"
                label="Judgment"
                options={judgmentOptions}
                getOptionLabel={(option) => option?.name || ""}
                isOptionEqualToValue={(option, value) =>
                  option?.id === value?.id
                }
                fullWidth
                disabled={isReadonlyMode}
              />
              <ControlledDateField
                name="judgment_date"
                label="Judgment Date"
                sx={{ flex: 1 }}
                disabled={isReadonlyMode}
              />
            </Box>
            <ControlledDateField name="sentence_date" label="Sentence Date" disabled={isReadonlyMode} />
            <ControlledTextField
              name="sentence_type"
              label="Sentence Type"
              fullWidth
              disabled={isReadonlyMode}
            />
          </Box>
        </DialogContent>
        {!isReadonlyMode && (
          <ModalActions
            onSecondaryAction={setModalClose}
            onPrimaryAction={methods.handleSubmit(handleSubmit)}
            isLoading={isUpdating}
            primaryActionButtonText="Save"
            secondaryActionButtonText="Cancel"
            onDeleteAction={handleDelete}
            isDeleteActionLoading={isDeleting}
          />
        )}
      </form>
    </FormProvider>
  );
};

export default ChargeRecommendationUpdateModal;
