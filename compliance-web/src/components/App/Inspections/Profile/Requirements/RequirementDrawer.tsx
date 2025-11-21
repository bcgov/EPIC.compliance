import DrawerActionBarBottom from "@/components/Shared/Drawer/DrawerActionBarBottom";
import DrawerActionBarTop from "@/components/Shared/Drawer/DrawerActionBarTop";
import DrawerTitleBar from "@/components/Shared/Drawer/DrawerTitleBar";
import {
  useCreateInspectionRequirement,
  useDeleteInspectionRequirement,
  useInspectionRequirementTypesData,
  useUpdateInspectionRequirement,
} from "@/hooks/useInspectionRequirements";
import { Inspection } from "@/models/Inspection";
import {
  InspectionRequirement,
  InspectionRequirementFormData,
} from "@/models/InspectionRequirement";
import { RequirementSourceFormData } from "@/models/InspectionRequirementSource";
import { useMenuStore } from "@/store/menuStore";
import { yupResolver } from "@hookform/resolvers/yup";
import { Box } from "@mui/material";
import { useCallback, useEffect, useMemo, useState } from "react";
import { FormProvider, useForm } from "react-hook-form";
import RequirementFormLeft from "./RequirementFormLeft";
import RequirementFormRight from "./RequirementFormRight";
import {
  formatRequirementAPIData,
  formatRequirementBatchAPIData,
  formatRequirementFormData,
  formatRequirementImagesInFindings,
  REGULATORY_CONSIDERATION_TYPE_ID,
  REQUIREMENT_TYPE_ID,
  RequirementFormSchema,
  updateImagesWithContinuousSortOrder,
} from "./RequirementUtils";
import * as yup from "yup";
import { useRequirementStore } from "./requirementStore";
import { useQueryClient } from "@tanstack/react-query";
import { MQ } from "@/styles/responsive";

type RequirementDrawerProps = {
  inspectionData: Inspection;
  onSubmit: (submitMsg: string, isClose: boolean) => void;
  requirement?: InspectionRequirement;
  index?: number;
  isRegulatoryConsideration?: boolean;
};

const initFormData: InspectionRequirementFormData = {
  requirementType: undefined,
  requirementSummary: "",
  topic: undefined,
  complianceFinding: undefined,
  enforcementAction: undefined,
  findings: undefined,
};

const RequirementDrawer: React.FC<RequirementDrawerProps> = ({
  inspectionData,
  onSubmit,
  requirement,
  index,
  isRegulatoryConsideration = false,
}) => {
  const queryClient = useQueryClient();
  const { appHeaderHeight } = useMenuStore();
  const [inspectionRequirementData, setInspectionRequirementData] = useState<
    InspectionRequirementFormData | undefined
  >(undefined);
  const [requirementSourceList, setRequirementSourceList] = useState<
    RequirementSourceFormData[]
  >([]);

  const {
    requirementsList,
    requirementPhotos,
    requirementFigures,
    isDataChanged,
    isImageChanged,
    setIsDataChanged,
    setIsImageChanged,
    resetRequirementStoreFlags,
    createRequirementStoreSnapshot,
    restoreRequirementStoreFromSnapshot,
  } = useRequirementStore();

  const { data: inspectionRequirementTypesList } =
    useInspectionRequirementTypesData();

  const isRequirementEditable = useMemo(
    () => inspectionData?.inspection_status?.toLowerCase() === "open",
    [inspectionData]
  );

  const GeneratedFormSchema = RequirementFormSchema(isRegulatoryConsideration);

  type RequirementSchemaType = yup.InferType<typeof GeneratedFormSchema>;

  const methods = useForm<RequirementSchemaType>({
    resolver: yupResolver(GeneratedFormSchema),
    mode: "onBlur",
    defaultValues: requirement
      ? formatRequirementFormData(requirement)
      : {
          ...initFormData,
          requirementType: inspectionRequirementTypesList?.[0],
        },
  });

  const { handleSubmit, reset: resetForm } = methods;

  useEffect(() => {
    resetForm(
      inspectionRequirementData ?? {
        ...initFormData,
        requirementType: inspectionRequirementTypesList?.[0],
      }
    );
  }, [inspectionRequirementData, resetForm, inspectionRequirementTypesList]);
  const isInspectionClosed = useMemo(() => inspectionData?.inspection_status?.toLowerCase() === "closed", [inspectionData]);
  const onCreateSuccess = useCallback(() => {
    onSubmit("Requirement created successfully!", true);
    resetForm();
  }, [onSubmit, resetForm]);

  const onUpdateSuccess = useCallback(() => {
    queryClient.invalidateQueries({
      queryKey: [
        "requirement-source-images",
        inspectionData.id,
        requirement?.id ?? 0,
      ],
    });
    queryClient.invalidateQueries({
      queryKey: [
        "requirement-document-images",
        inspectionData.id,
        requirement?.id ?? 0,
      ],
    });
    onSubmit("Changes saved successfully!", false);
    setIsImageChanged(false);
  }, [onSubmit, setIsImageChanged, queryClient, inspectionData, requirement]);

  const onDeleteSuccess = useCallback(() => {
    onSubmit("Requirement deleted successfully!", true);
    resetForm();
  }, [onSubmit, resetForm]);

  const {
    mutate: createInspectionRequirement,
    isPending: isCreateInspectionRequirementPending,
  } = useCreateInspectionRequirement(onCreateSuccess);

  const {
    mutate: updateInspectionRequirement,
    data: inspectionRequirementUpdateData,
    isPending: isUpdateInspectionRequirementPending,
  } = useUpdateInspectionRequirement(onUpdateSuccess);

  const formatAndSetFormData = useCallback(
    (inspectionRequirement: InspectionRequirement) => {
      const inspectionRequirementFormData = formatRequirementFormData(
        inspectionRequirement
      );
      setInspectionRequirementData(inspectionRequirementFormData);
      setRequirementSourceList(
        inspectionRequirementFormData.requirementSourceDetails ?? []
      );
    },
    []
  );

  useEffect(() => {
    if (requirement) {
      formatAndSetFormData(requirement);
    }
    resetRequirementStoreFlags();
    createRequirementStoreSnapshot();
  }, [
    requirement,
    formatAndSetFormData,
    resetRequirementStoreFlags,
    createRequirementStoreSnapshot,
  ]);

  useEffect(() => {
    if (inspectionRequirementUpdateData) {
      formatAndSetFormData(inspectionRequirementUpdateData);
      setIsDataChanged(false);
      createRequirementStoreSnapshot();
    }
  }, [
    inspectionRequirementUpdateData,
    formatAndSetFormData,
    setIsDataChanged,
    createRequirementStoreSnapshot,
  ]);

  const { mutate: deleteInspectionRequirement } =
    useDeleteInspectionRequirement(onDeleteSuccess);

  const onDeleteRequirement = () => {
    if (!requirement) {
      return;
    }
    if (
      (requirementPhotos.get(requirement.id) ?? []).length > 0 ||
      (requirementFigures.get(requirement.id) ?? []).length > 0
    ) {
      // Remove the requirement's photos and figures from the records & update the sort order
      let updatedRequirementPhotos = new Map(requirementPhotos);
      let updatedRequirementFigures = new Map(requirementFigures);

      if (updatedRequirementPhotos.has(requirement.id)) {
        updatedRequirementPhotos.delete(requirement.id);
        updatedRequirementPhotos = updateImagesWithContinuousSortOrder(
          updatedRequirementPhotos,
          requirementsList
        );
      }

      if (updatedRequirementFigures.has(requirement.id)) {
        updatedRequirementFigures.delete(requirement.id);
        updatedRequirementFigures = updateImagesWithContinuousSortOrder(
          updatedRequirementFigures,
          requirementsList
        );
      }

      // update the requirement images sort order in all findings
      const updatedRequirementsList = formatRequirementImagesInFindings(
        requirementsList,
        updatedRequirementPhotos,
        updatedRequirementFigures
      );

      // prepare for batch update
      const requirementBatchAPIData = formatRequirementBatchAPIData(
        updatedRequirementsList,
        updatedRequirementPhotos,
        updatedRequirementFigures,
        requirement?.id ?? 0
      );

      deleteInspectionRequirement({
        inspectionId: inspectionData.id,
        requirementId: requirement.id,
        requirementBatch: requirementBatchAPIData,
      });
    } else {
      deleteInspectionRequirement({
        inspectionId: inspectionData.id,
        requirementId: requirement.id,
      });
    }
  };

  const onSubmitHandler = useCallback(
    (formData: RequirementSchemaType) => {
      const formLeftData = formData as InspectionRequirementFormData;

      const inspectionRequirementPayload = formatRequirementAPIData(
        formLeftData,
        isRegulatoryConsideration
          ? REGULATORY_CONSIDERATION_TYPE_ID
          : REQUIREMENT_TYPE_ID,
        requirementPhotos.get(requirement?.id ?? NaN),
        requirementFigures.get(requirement?.id ?? NaN),
        requirementSourceList ?? undefined
      );

      if (inspectionRequirementData) {
        const photosWithSortOrder = updateImagesWithContinuousSortOrder(
          requirementPhotos,
          requirementsList
        );
        const figuresWithSortOrder = updateImagesWithContinuousSortOrder(
          requirementFigures,
          requirementsList
        );
        // prepare for batch update
        const requirementBatchAPIData = isImageChanged
          ? formatRequirementBatchAPIData(
              requirementsList,
              photosWithSortOrder,
              figuresWithSortOrder,
              requirement?.id ?? 0
            )
          : undefined;
        updateInspectionRequirement({
          inspectionId: inspectionData.id,
          requirementId: inspectionRequirementData.id ?? 0,
          inspectionRequirement: inspectionRequirementPayload,
          requirementBatch: requirementBatchAPIData,
        });
      } else {
        createInspectionRequirement({
          inspectionId: inspectionData.id,
          inspectionRequirement: inspectionRequirementPayload,
        });
      }
    },
    [
      requirementsList,
      requirementPhotos,
      requirementFigures,
      requirement,
      isRegulatoryConsideration,
      requirementSourceList,
      inspectionRequirementData,
      updateInspectionRequirement,
      inspectionData,
      createInspectionRequirement,
      isImageChanged,
    ]
  );

  const onRequirementSourceListDataChange = (
    data: RequirementSourceFormData[]
  ) => {
    const isDifferent =
      JSON.stringify(data) !== JSON.stringify(requirementSourceList);
    if (isDifferent) {
      setIsDataChanged(true);
      setRequirementSourceList(data);
    }
  };

  const getDrawerTitle = () => {
    if (inspectionRequirementData) {
      return isRegulatoryConsideration
        ? `Edit Regulatory Consideration`
        : `Edit Requirement ${index !== undefined ? `#${index + 1}` : ""}`;
    }
    return isRegulatoryConsideration
      ? "Create Regulatory Consideration"
      : "Create Requirement";
  };

  const handleClearData = useCallback(() => {
    // Only restore if there are unsaved changes; otherwise keep the latest store state
    if (isDataChanged || isImageChanged) {
      restoreRequirementStoreFromSnapshot();
    }
  }, [isDataChanged, isImageChanged, restoreRequirementStoreFromSnapshot]);

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmitHandler)}>
        <DrawerTitleBar
          title={getDrawerTitle()}
          isFormDirtyCheck
          isDirtyManual={isDataChanged}
          customCloseFn={handleClearData}
        />
        <DrawerActionBarTop
          isShowActionBar={!inspectionRequirementData}
          isLoading={isCreateInspectionRequirementPending}
        />
        <Box
          key={JSON.stringify(inspectionRequirementData)}
          height={`calc(100vh - ${appHeaderHeight + 129}px)`} // 64px (DrawerTitleBar height) + 65px (DrawerActionBar height)
          sx={{
            display: "flex",
            flexDirection: "row",
            [MQ.mdToLg]: {
              flexDirection: "column-reverse",
              overflow: "auto",
            }
          }}
        >
          <RequirementFormLeft
            appHeaderHeight={appHeaderHeight}
            isRegulatoryConsideration={isRegulatoryConsideration}
            isEditMode={!!inspectionRequirementData}
            requirementId={requirement?.id ?? 0}
            inspectionData={inspectionData}
            currentEnforcementAction={
              requirement?.enforcement_action_data?.[0] ?? undefined
            }
            isRequirementEditable={isRequirementEditable}
          />
          <RequirementFormRight
            onDataChange={onRequirementSourceListDataChange}
            requirementSourceFormDataList={requirementSourceList}
            inspectionId={inspectionData.id}
            caseFile={inspectionData.case_file}
            isRegulatoryConsideration={isRegulatoryConsideration}
            requirementId={requirement?.id ?? 0}
            isRequirementEditable={isRequirementEditable}
          />
        </Box>
        <DrawerActionBarBottom
          isShowActionBar={!isInspectionClosed}
          onDeleteAction={onDeleteRequirement}
          onDeleteTitle="Delete Requirement"
          onDeleteDescription="You are about to delete this Requirement. Are you sure?"
          isDirtyManual={isDataChanged}
          customCancelFn={handleClearData}
          isLoading={isUpdateInspectionRequirementPending}
        />
      </form>
    </FormProvider>
  );
};

export default RequirementDrawer;
