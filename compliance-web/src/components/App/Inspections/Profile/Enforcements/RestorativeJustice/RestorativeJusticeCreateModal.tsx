import { FC, useCallback, useEffect, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import EnforcementModal from "@/components/App/Inspections/Profile/Enforcements/EnforcementModal";
import {
  BaseEnforcementFormType,
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
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { useQueryClient } from "@tanstack/react-query";
import { notify } from "@/store/snackbarStore";

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
  const defaultValues = useMemo(() => {
    return getDefaultFormValues(requirement);
  }, [requirement]);

  const methods = useForm<BaseEnforcementFormType>({
    resolver: yupResolver(baseEnforcementSchema),
    mode: "onBlur",
    defaultValues,
  });

  const { reset } = methods;

  useEffect(() => {
    reset(defaultValues);
  }, [reset, defaultValues]);

  const onSuccess = (data: RestorativeJustice) => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-restorative-justice", inspectionData.id],
    });
    notifyAndSubmit(data);
  };

  const notifyAndSubmit = (data: RestorativeJustice) => {
    notify.success(
      ENFORCEMENT_MESSAGES.RESTORATIVE_JUSTICE_CREATED(
        data.restorative_justice_number || ""
      )
    );
    onSubmit(data);
  };

  const {
    mutate: createRestorativeJustice,
    isPending: isPendingRestorativeJustice,
  } = useCreateRestorativeJustice(onSuccess);

  const handleBaseSubmit = useCallback(
    (data: BaseEnforcementFormType) => {
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

  return (
    <FormProvider {...methods}>
      <EnforcementModal
        requirementsList={requirementsList}
        requirement={requirement}
        title="Create Restorative Justice"
        onSubmit={handleBaseSubmit}
        isLoading={isPendingRestorativeJustice}
      />
    </FormProvider>
  );
};

export default RestorativeJusticeCreateModal;
