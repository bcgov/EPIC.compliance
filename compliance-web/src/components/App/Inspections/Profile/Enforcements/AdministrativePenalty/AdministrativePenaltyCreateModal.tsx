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
import { useCreateAdministrativePenalty, useLinkAdministrativePenalty } from "@/hooks/useAdministrativePenalties";
import {
  AdministrativePenalty,
  AdministrativePenaltyAPIData,
} from "@/models/AdministrativePenalty";
import { Inspection } from "@/models/Inspection";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { notify } from "@/store/snackbarStore";
import { useModal } from "@/store/modalStore";
import AdministrativePenaltyUpdateModal from "./AdministrativePenaltyUpdateModal";
import AdministrativePenaltyCreationOptions from "./AdministrativePenaltyCreationOptions";
import {
  APReferralStatus,
  EnforcementActionEnum,
  MODAL_WIDTHS,
} from "@/utils/constants";

const administrativePenaltySchema = baseEnforcementSchema.shape({
  apCreationMethod: yup.string().required("Please select a creation method"),
  manualAPNumber: yup.string().when("apCreationMethod", {
    is: "manual_entry",
    then: (schema) => schema.required("Historical AP number is required"),
    otherwise: (schema) => schema.notRequired(),
  }),
  existingAPId: yup.number().when("apCreationMethod", {
    is: "link_existing",
    then: (schema) => schema.required("Please select an existing AP"),
    otherwise: (schema) => schema.notRequired(),
  }),
});

type AdministrativePenaltyFormType = yup.InferType<
  typeof administrativePenaltySchema
>;

type AdministrativePenaltyCreateModalProps = {
  inspectionData: Inspection;
  requirementsList: InspectionRequirement[];
  requirement?: InspectionRequirement;
  nonProceededRequirements?: InspectionRequirement[];
  enforcementAction: EnforcementActionEnum;
  isPrimaryOfficerOrSuperUser: boolean;
  onSubmit: (data: AdministrativePenalty) => void;
};

const AdministrativePenaltyCreateModal: FC<
  AdministrativePenaltyCreateModalProps
> = ({ inspectionData, requirementsList, requirement, nonProceededRequirements, enforcementAction, isPrimaryOfficerOrSuperUser, onSubmit }) => {
  const queryClient = useQueryClient();
  const { setOpen: setModalOpen, setClose: setModalClose } = useModal();

  const defaultValues = useMemo(() => {
    return {
      ...getDefaultFormValues(requirement, false, undefined),
      apCreationMethod: inspectionData.is_history ? "manual_entry" : "create_new",
      manualAPNumber: "",
      existingAPId: undefined,
    };
  }, [requirement, inspectionData.is_history]);

  const methods = useForm<AdministrativePenaltyFormType>({
    resolver: yupResolver(administrativePenaltySchema),
    mode: "onChange",
    defaultValues,
  });

  const { reset } = methods;


  useEffect(() => {
    reset(defaultValues);
  }, [reset, defaultValues]);

  const onSuccess = (data: AdministrativePenalty) => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-administrative-penalties"],
    });
    queryClient.invalidateQueries({
      queryKey: ["administrative-penalty-links"]
    });
    notify.success(
      ENFORCEMENT_MESSAGES.ADMINISTRATIVE_PENALTY_CREATED(
        data.administrative_penalty_number || ""
      )
    );

    setModalClose();

    setTimeout(() => {
      setModalOpen({
        content: (
          <AdministrativePenaltyUpdateModal
            administrativePenalty={data}
            inspectionData={inspectionData}
            isPrimaryOfficerOrSuperUser={isPrimaryOfficerOrSuperUser}
            onSuccess={(updatedData) => {
              onSubmit(updatedData);
            }}
          />
        ),
        width: MODAL_WIDTHS.ADMINISTRATIVE_PENALTY,
      });
    }, 100);
  };

  const {
    mutate: createAdministrativePenalty,
    isPending: isPendingAdministrativePenalty,
  } = useCreateAdministrativePenalty(onSuccess);

  const {
    mutate: linkAdministrativePenalty,
    isPending: isPendingLink,
  } = useLinkAdministrativePenalty(onSuccess);

  const handleBaseSubmit = useCallback(
    async (data: BaseEnforcementFormType) => {
      const formData = methods.getValues();
      const requirementIds = (data.requirements as InspectionRequirement[]).map((requirement) => requirement.id);

      if (!formData.apCreationMethod) {
        methods.setError("apCreationMethod", {
          type: "required",
          message: "Please select a creation method"
        });
        notify.error("Please select a creation method");
        return;
      }
      if (formData.apCreationMethod === "manual_entry" && !formData.manualAPNumber) {
        methods.setError("manualAPNumber", {
          type: "required",
          message: "Please enter a historical AP number"
        });
        notify.error("Please enter a historical AP number");
        return;
      }
      if (formData.apCreationMethod === "link_existing" && !formData.existingAPId) {
        methods.setError("existingAPId", {
          type: "required",
          message: "Please select an existing AP to link to"
        });
        notify.error("Please select an existing AP to link to");
        return;
      }

      if (formData.apCreationMethod === "link_existing") {
        const linkData = {
          inspection_id: inspectionData.id,
          inspection_requirement_ids: requirementIds,
        };


        linkAdministrativePenalty({
          administrativePenaltyId: formData.existingAPId!,
          link: linkData,
        });
        return;
      }

      const administrativePenaltyData: AdministrativePenaltyAPIData = {
        inspection_id: inspectionData?.id ?? 0,
        inspection_requirement_ids: requirementIds,
        referral_status: APReferralStatus.PREPARING_REFERRAL_FOR_AEO.id,
      };

      if (formData.apCreationMethod === "manual_entry" && formData.manualAPNumber) {
        administrativePenaltyData.administrative_penalty_number = formData.manualAPNumber;
      }

      createAdministrativePenalty({
        administrativePenalty: administrativePenaltyData,
      });
    },
    [createAdministrativePenalty, linkAdministrativePenalty, inspectionData, methods]
  );

  return (
    <FormProvider {...methods}>
      <EnforcementModal
        requirementsList={requirementsList}
        requirement={requirement}
        nonProceededRequirements={nonProceededRequirements}
        title="Create Administrative Penalty"
        onSubmit={handleBaseSubmit}
        enforcementAction={enforcementAction}
        isLoading={isPendingAdministrativePenalty || isPendingLink}
        additionalFormFields={
          <FormProvider {...methods}>
            <AdministrativePenaltyCreationOptions
              inspectionData={inspectionData}
              isHistorical={inspectionData.is_history || false}
            />
          </FormProvider>
        }
      />
    </FormProvider>
  );
};

export default AdministrativePenaltyCreateModal;
