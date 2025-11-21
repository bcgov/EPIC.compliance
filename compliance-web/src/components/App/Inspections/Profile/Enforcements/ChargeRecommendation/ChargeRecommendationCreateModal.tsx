import { FC, useCallback, useEffect, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup";
import { useQueryClient } from "@tanstack/react-query";
import EnforcementModal from "@/components/App/Inspections/Profile/Enforcements/EnforcementModal";
import {
  baseEnforcementSchema,
  BaseEnforcementFormType,
  getDefaultFormValues,
  ENFORCEMENT_MESSAGES,
} from "@/components/App/Inspections/Profile/Enforcements/EnforcementUtils";
import { useCreateChargeRecommendation } from "@/hooks/useChargeRecommendations";
import {
  ChargeRecommendation,
  ChargeRecommendationAPIData,
} from "@/models/ChargeRecommendation";
import { Inspection } from "@/models/Inspection";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { notify } from "@/store/snackbarStore";
import { useModal } from "@/store/modalStore";
import ChargeRecommendationUpdateModal from "./ChargeRecommendationUpdateModal";
import { EnforcementActionEnum, MODAL_WIDTHS } from "@/utils/constants";

const chargeRecommendationSchema = baseEnforcementSchema;

type ChargeRecommendationFormType = yup.InferType<
  typeof chargeRecommendationSchema
>;

type ChargeRecommendationCreateModalProps = {
  inspectionData: Inspection;
  requirementsList: InspectionRequirement[];
  nonProceededRequirements: InspectionRequirement[];
  enforcementAction: EnforcementActionEnum;
  isPrimaryOfficerOrSuperUser: boolean;
  requirement?: InspectionRequirement;
  onSubmit: (data: ChargeRecommendation) => void;
};

const ChargeRecommendationCreateModal: FC<
  ChargeRecommendationCreateModalProps
> = ({
  inspectionData,
  requirementsList,
  nonProceededRequirements,
  enforcementAction,
  isPrimaryOfficerOrSuperUser,
  requirement,
  onSubmit,
}) => {
  const queryClient = useQueryClient();
  const { setOpen: setModalOpen, setClose: setModalClose } = useModal();

  const defaultValues = useMemo(() => {
    return getDefaultFormValues(requirement, false, undefined);
  }, [requirement]);

  const methods = useForm<ChargeRecommendationFormType>({
    resolver: yupResolver(chargeRecommendationSchema),
    mode: "onBlur",
    defaultValues,
  });

  const onSuccess = (data: ChargeRecommendation) => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-charge-recommendations", inspectionData.id],
    });
    notify.success(
      ENFORCEMENT_MESSAGES.CHARGE_RECOMMENDATION_CREATED(
        data.charge_recommendation_number || ""
      )
    );

    setModalClose();

    setTimeout(() => {
      setModalOpen({
        content: (
          <ChargeRecommendationUpdateModal
            inspectionData={inspectionData}
            chargeRecommendationData={data}
            isPrimaryOfficerOrSuperUser={isPrimaryOfficerOrSuperUser}
            onSubmit={(updatedData) => {
              onSubmit(updatedData);
            }}
          />
        ),
        width: MODAL_WIDTHS.CHARGE_RECOMMENDATION,
      });
    }, 100);
  };

  const { mutate: createChargeRecommendation, isPending } =
    useCreateChargeRecommendation(onSuccess);

  const handleBaseSubmit = useCallback(
    (data: BaseEnforcementFormType) => {
      const chargeRecommendationData: ChargeRecommendationAPIData = {
        inspection_id: inspectionData?.id ?? 0,
        inspection_requirement_ids: (
          data.requirements as InspectionRequirement[]
        ).map((requirement) => requirement.id),
        status: "DRAFTING",
      };

      createChargeRecommendation({
        chargeRecommendation: chargeRecommendationData,
      });
    },
    [createChargeRecommendation, inspectionData]
  );

  useEffect(() => {
    methods.reset(defaultValues);
  }, [defaultValues, methods]);

  return (
    <FormProvider {...methods}>
      <EnforcementModal
        requirementsList={requirementsList}
        requirement={requirement}
        nonProceededRequirements={nonProceededRequirements}
        enforcementAction={enforcementAction}
        title="Create Charge Recommendation"
        onSubmit={handleBaseSubmit}
        isLoading={isPending}
      />
    </FormProvider>
  );
};

export default ChargeRecommendationCreateModal;
