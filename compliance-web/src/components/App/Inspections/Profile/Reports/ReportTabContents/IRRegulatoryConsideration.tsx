import { Typography } from "@mui/material";
import { useReportStore } from "@/components/App/Inspections/Profile/Reports/reportStore";
import IRBoxContainer from "./IRBoxContainer";
import { DRAWER_WIDTHS } from "@/utils/constants";
import { useCallback, useEffect, useState } from "react";
import RequirementDrawer from "@/components/App/Inspections/Profile/Requirements/RequirementDrawer";
import { useDrawer } from "@/store/drawerStore";
import { Inspection } from "@/models/Inspection";
import { notify } from "@/store/snackbarStore";
import { useQueryClient } from "@tanstack/react-query";
import { useRequirementStore } from "@/components/App/Inspections/Profile/Requirements/requirementStore";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { REGULATORY_CONSIDERATION_TYPE_ID } from "@/components/App/Inspections/Profile/Requirements/RequirementUtils";
import { RequirementImage } from "@/models/Image";
import IRImageSection from "./IRImageSection";
import useResponsiveDrawerWidth from "@/hooks/useResponsiveDrawerWidth";

const IRRegulatoryConsideration = () => {
  const { inspectionData, isReportsReadOnly } = useReportStore();
  const { requirementsList, requirementPhotos, requirementFigures } =
    useRequirementStore();
  const { setOpen, setClose } = useDrawer();
  const queryClient = useQueryClient();
  const [
    inspectionRegulatoryConsideration,
    setInspectionRegulatoryConsideration,
  ] = useState<InspectionRequirement | undefined>(undefined);
  const [photos, setPhotos] = useState<RequirementImage[]>([]);
  const [figures, setFigures] = useState<RequirementImage[]>([]);

  useEffect(() => {
    setPhotos(
      requirementPhotos.get(inspectionRegulatoryConsideration?.id ?? 0) ?? []
    );
    setFigures(
      requirementFigures.get(inspectionRegulatoryConsideration?.id ?? 0) ?? []
    );
  }, [
    requirementPhotos,
    requirementFigures,
    inspectionRegulatoryConsideration,
  ]);

  useEffect(() => {
    setInspectionRegulatoryConsideration(
      requirementsList.find(
        (requirement) =>
          requirement.req_type.id === REGULATORY_CONSIDERATION_TYPE_ID
      )
    );
  }, [requirementsList]);

  const handleOnSubmit = useCallback(
    (submitMsg: string) => {
      queryClient.invalidateQueries({
        queryKey: ["inspection-requirements", inspectionData?.id],
      });
      notify.success(submitMsg);
      setClose();
    },
    [setClose, inspectionData, queryClient]
  );

  const drawerWidth = useResponsiveDrawerWidth(
    DRAWER_WIDTHS.REQUIREMENT_DRAWER,
    { mdToLgMax: "750px" }
  );

  const handleOpenEditRequirementModal = useCallback(() => {
    setOpen({
      content: (
        <RequirementDrawer
          onSubmit={handleOnSubmit}
          inspectionData={inspectionData as Inspection}
          requirement={inspectionRegulatoryConsideration}
          isRegulatoryConsideration={true}
        />
      ),
      width: drawerWidth,
    });
  }, [
    setOpen,
    handleOnSubmit,
    inspectionData,
    inspectionRegulatoryConsideration,
    drawerWidth,
  ]);

  return (
    <IRBoxContainer
      title="Regulatory Consideration"
      onEdit={!isReportsReadOnly ? handleOpenEditRequirementModal : undefined}
    >
      {inspectionRegulatoryConsideration ? (
        <>
          <Typography
            variant="body1"
            component={"div"}
            className="editor-content"
            mb={1.5}
            dangerouslySetInnerHTML={{
              __html: inspectionRegulatoryConsideration?.findings || "",
            }}
          />

          {photos.map((photo) => (
            <IRImageSection key={photo.id} image={photo} />
          ))}

          {figures.map((figure) => (
            <IRImageSection key={figure.id} image={figure} />
          ))}
        </>
      ) : (
        <Typography variant="body1">None at this time.</Typography>
      )}
    </IRBoxContainer>
  );
};

export default IRRegulatoryConsideration;
