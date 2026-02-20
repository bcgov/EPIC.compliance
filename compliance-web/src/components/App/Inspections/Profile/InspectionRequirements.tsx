import RequirementDrawer from "@/components/App/Inspections/Profile/Requirements/RequirementDrawer";
import {
  useInspectionRequirementImages,
  useInspectionRequirementsData,
  useUpdateInspectionRequirementBatch,
} from "@/hooks/useInspectionRequirements";
import { Inspection } from "@/models/Inspection";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { useDrawer } from "@/store/drawerStore";
import { notify } from "@/store/snackbarStore";
import { AddRounded } from "@mui/icons-material";
import { Box, Button, Typography } from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { Reorder } from "framer-motion";
import React, { useCallback, useEffect, useMemo } from "react";
import RequirementCard from "./Requirements/RequirementCard";
import {
  convertRequirementImagesArrToMap,
  formatRequirementBatchAPIData,
  formatRequirementImagesInFindings,
  REGULATORY_CONSIDERATION_TYPE_ID,
  REQUIREMENT_TYPE_ID,
  updateImagesWithContinuousSortOrder,
} from "./Requirements/RequirementUtils";
import { DRAWER_WIDTHS } from "@/utils/constants";
import { useRequirementStore } from "./Requirements/requirementStore";
import RequirementLoading from "./Requirements/RequirementLoading";
import DynamicHeightBox from "@/components/Shared/DynamicHeightBox";
import useResponsiveDrawerWidth from "@/hooks/useResponsiveDrawerWidth";
import { useReportStore } from "./Reports/reportStore";

interface InspectionRequirementsProps {
  inspectionData: Inspection;
}

const InspectionRequirements: React.FC<InspectionRequirementsProps> = ({
  inspectionData,
}) => {
  const queryClient = useQueryClient();
  const { setOpen, isOpen: isDrawerOpen, setClose } = useDrawer();
  const {
    requirementPhotos,
    requirementFigures,
    setRequirementPhotos,
    setRequirementFigures,
    setRequirementsList,
  } = useRequirementStore();
  const { inspectionReportsData } = useReportStore();
  const [activeRequirementId, setActiveRequirementId] = React.useState<
    number | null
  >(null);
  const [inspectionRequirements, setInspectionRequirements] = React.useState<
    InspectionRequirement[]
  >([]);
  const [regulatoryConsideration, setRegulatoryConsideration] =
    React.useState<InspectionRequirement | null>(null);
  const [isDataLoading, setIsDataLoading] = React.useState<boolean>(true);

  const {
    data: inspectionRequirementsData,
    isLoading: isInspectionRequirementsLoading,
  } = useInspectionRequirementsData(inspectionData.id);

  const {
    data: inspectionRequirementImages,
    isLoading: isInspectionRequirementImagesLoading,
  } = useInspectionRequirementImages(inspectionData.id);

  const { mutate: updateInspectionRequirementBatch } =
    useUpdateInspectionRequirementBatch(() => {});

  const isRequirementsAllowed = useMemo(
    () => inspectionData?.inspection_status?.toLowerCase() === "open",
    [inspectionData]
  );

  useEffect(() => {
    if (inspectionRequirementsData) {
      let requirementsList = inspectionRequirementsData;

      // Update the requirement images with latest image get url in the findings
      if (requirementPhotos.size || requirementFigures.size) {
        requirementsList = formatRequirementImagesInFindings(
          requirementsList,
          requirementPhotos,
          requirementFigures
        );
      }

      setRequirementsList(requirementsList);

      setInspectionRequirements(
        requirementsList.filter(
          (req) => req.req_type?.id === REQUIREMENT_TYPE_ID
        )
      );

      setRegulatoryConsideration(
        requirementsList.find(
          (req) => req.req_type?.id === REGULATORY_CONSIDERATION_TYPE_ID
        ) ?? null
      );
    }
  }, [
    inspectionRequirementsData,
    setRequirementsList,
    requirementPhotos,
    requirementFigures,
  ]);

  useEffect(() => {
    if (inspectionRequirementImages) {
      const photosMap = convertRequirementImagesArrToMap(
        inspectionRequirementImages.photos
      );
      const figuresMap = convertRequirementImagesArrToMap(
        inspectionRequirementImages.figures
      );
      setRequirementPhotos(photosMap);
      setRequirementFigures(figuresMap);
    }
  }, [
    inspectionRequirementImages,
    setRequirementPhotos,
    setRequirementFigures,
  ]);

  const handleOnSubmit = useCallback(
    (submitMsg: string, isClose: boolean = true) => {
      queryClient.invalidateQueries({
        queryKey: ["inspection-requirements", inspectionData.id],
      });
      queryClient.invalidateQueries({
        queryKey: ["inspection-requirement-images", inspectionData.id],
      });
      notify.success(submitMsg);
      if (isClose) {
        setClose();
      }
    },
    [queryClient, inspectionData, setClose]
  );

  const drawerWidth = useResponsiveDrawerWidth(
    DRAWER_WIDTHS.REQUIREMENT_DRAWER,
    { mdToLgMax: "750px" }
  );

  const handleOpenAddRequirementModal = useCallback(() => {
    setOpen({
      content: (
        <RequirementDrawer
          onSubmit={handleOnSubmit}
          inspectionData={inspectionData}
        />
      ),
      width: drawerWidth,
    });
  }, [setOpen, handleOnSubmit, inspectionData, drawerWidth]);

  const handleOpenAddRegulatoryConsiderationModal = useCallback(() => {
    setOpen({
      content: (
        <RequirementDrawer
          onSubmit={handleOnSubmit}
          inspectionData={inspectionData}
          isRegulatoryConsideration={true}
        />
      ),
      width: drawerWidth,
    });
  }, [setOpen, handleOnSubmit, inspectionData, drawerWidth]);

  const handleOpenEditRequirementDrawer = useCallback(
    (
      requirement: InspectionRequirement,
      index?: number,
      isRegulatoryConsideration?: boolean
    ) => {
      setActiveRequirementId(requirement.id);
      setOpen({
        content: (
          <RequirementDrawer
            onSubmit={handleOnSubmit}
            inspectionData={inspectionData}
            requirement={requirement}
            index={index}
            isRegulatoryConsideration={isRegulatoryConsideration}
          />
        ),
        width: drawerWidth,
      });
    },
    [setOpen, handleOnSubmit, inspectionData, drawerWidth]
  );

  // Add a ref to store the timeout ID : to prevent multiple API calls during reordering
  const updateTimeoutRef = React.useRef<NodeJS.Timeout>();

  const handleSortOrderChange = useCallback(
    (newRequirementListOrder: InspectionRequirement[]) => {
      if (isDrawerOpen || !isRequirementsAllowed) {
        return;
      }

      const updateRequirementLists = [...newRequirementListOrder];

      if (regulatoryConsideration?.id) {
        updateRequirementLists.push(regulatoryConsideration);
      }

      // Always read the latest maps from the store to avoid stale closures
      const {
        requirementPhotos: latestRequirementPhotos,
        requirementFigures: latestRequirementFigures,
      } = useRequirementStore.getState();

      const photosWithSortOrder = updateImagesWithContinuousSortOrder(
        latestRequirementPhotos,
        updateRequirementLists
      );
      const figuresWithSortOrder = updateImagesWithContinuousSortOrder(
        latestRequirementFigures,
        updateRequirementLists
      );

      // update the requirement images sort order in all findings
      const updatedRequirementsList = formatRequirementImagesInFindings(
        updateRequirementLists,
        photosWithSortOrder,
        figuresWithSortOrder
      );

      setRequirementPhotos(photosWithSortOrder);
      setRequirementFigures(figuresWithSortOrder);

      // Update query client cache
      queryClient.setQueryData(
        ["inspection-requirements", inspectionData.id],
        updatedRequirementsList
      );

      // Clear any existing timeout
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }

      // Set a new timeout to make the API call 500ms after the last reordering
      updateTimeoutRef.current = setTimeout(() => {
        const requirementBatchAPIData = formatRequirementBatchAPIData(
          updatedRequirementsList,
          photosWithSortOrder,
          figuresWithSortOrder
        );

        updateInspectionRequirementBatch({
          inspectionId: inspectionData.id,
          requirementBatch: requirementBatchAPIData,
        });
      }, 500);
    },
    [
      isDrawerOpen,
      isRequirementsAllowed,
      inspectionData,
      queryClient,
      regulatoryConsideration,
      setRequirementFigures,
      setRequirementPhotos,
      updateInspectionRequirementBatch,
    ]
  );

  // Clean up the timeout when the component unmounts
  useEffect(() => {
    return () => {
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (!isDrawerOpen) {
      setActiveRequirementId(null);
    }
  }, [isDrawerOpen]);

  useEffect(() => {
    if (
      !isInspectionRequirementsLoading &&
      !isInspectionRequirementImagesLoading
    ) {
      setIsDataLoading(false);
    }
  }, [isInspectionRequirementsLoading, isInspectionRequirementImagesLoading]);

  return (
    <DynamicHeightBox
      display={"flex"}
      flexGrow={1}
      flexDirection={"column"}
      overflow={"auto"}
      bottomOffset={20}
    >
      <Box display={"flex"} justifyContent={"space-between"} mt={3} mb={2}>
        <Typography variant="h6">Requirements</Typography>
        {!isDataLoading &&
          isRequirementsAllowed &&
          !inspectionReportsData?.date_issued && (
            <Box display={"flex"} gap={2}>
              <Button
                variant="text"
                color="primary"
                size="small"
                onClick={handleOpenAddRegulatoryConsiderationModal}
                startIcon={<AddRounded />}
                data-cy="new-regulatory-consideration-button"
                disabled={!!regulatoryConsideration}
              >
                Regulatory Consideration
              </Button>
              <Button
                color="secondary"
                size="small"
                onClick={handleOpenAddRequirementModal}
                startIcon={<AddRounded />}
                data-cy="new-requirement-button"
              >
                New Requirement
              </Button>
            </Box>
          )}
      </Box>
      {isDataLoading ? (
        <RequirementLoading />
      ) : (
        <>
          <Reorder.Group
            axis="y"
            onReorder={handleSortOrderChange}
            values={inspectionRequirements}
            className="reorder-list"
          >
            {inspectionRequirements?.map((requirement, index) => (
              <RequirementCard
                key={requirement.id}
                requirement={requirement}
                index={index}
                onEdit={() =>
                  handleOpenEditRequirementDrawer(requirement, index)
                }
                isActive={requirement.id === activeRequirementId}
                disabled={isDrawerOpen}
                dragDisabled={!isRequirementsAllowed}
              />
            ))}
          </Reorder.Group>
          {regulatoryConsideration && (
            <RequirementCard
              key={regulatoryConsideration.id}
              requirement={regulatoryConsideration}
              index={inspectionRequirements.length}
              onEdit={() =>
                handleOpenEditRequirementDrawer(
                  regulatoryConsideration,
                  undefined,
                  true
                )
              }
              isActive={regulatoryConsideration.id === activeRequirementId}
              disabled={isDrawerOpen}
              dragDisabled={!isRequirementsAllowed}
            />
          )}
        </>
      )}
    </DynamicHeightBox>
  );
};

export default InspectionRequirements;
