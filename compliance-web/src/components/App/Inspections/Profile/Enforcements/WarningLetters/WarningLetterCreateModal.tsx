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
import { useCreateWarningLetter } from "@/hooks/useInspectionWarningLetters";
import {
  InspectionWarningLetter,
  InspectionWarningLetterAPIData,
} from "@/models/InspectionWarningLetter";
import { Inspection } from "@/models/Inspection";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { useQueryClient } from "@tanstack/react-query";
import { notify } from "@/store/snackbarStore";

type WarningLetterCreateModalProps = {
  inspectionData: Inspection;
  requirementsList: InspectionRequirement[];
  requirement?: InspectionRequirement;
  onSubmit: (data: InspectionWarningLetter) => void;
};

const WarningLetterCreateModal: FC<WarningLetterCreateModalProps> = ({
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

  const onSuccess = (data: InspectionWarningLetter) => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-warning-letters", inspectionData.id],
    });
    notifyAndSubmit(data);
  };

  const notifyAndSubmit = (data: InspectionWarningLetter) => {
    notify.success(
      ENFORCEMENT_MESSAGES.WARNING_LETTER_CREATED(
        data.warning_letter_number || ""
      )
    );
    onSubmit(data);
  };

  const {
    mutate: createInspectionWarningLetter,
    isPending: isPendingWarningLetter,
  } = useCreateWarningLetter(onSuccess);

  const handleBaseSubmit = useCallback(
    (data: BaseEnforcementFormType) => {
      const warningLetterData: InspectionWarningLetterAPIData = {
        inspection_id: inspectionData?.id ?? 0,
        inspection_requirement_ids: (
          data.requirements as InspectionRequirement[]
        ).map((requirement) => requirement.id),
      };
      createInspectionWarningLetter({
        inspectionWarningLetter: warningLetterData,
      });
    },
    [createInspectionWarningLetter, inspectionData]
  );

  return (
    <FormProvider {...methods}>
      <EnforcementModal
        requirementsList={requirementsList}
        requirement={requirement}
        title="Create Warning Letter"
        onSubmit={handleBaseSubmit}
        isLoading={isPendingWarningLetter}
      />
    </FormProvider>
  );
};

export default WarningLetterCreateModal;
