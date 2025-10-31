import { InspectionRequirement } from "@/models/InspectionRequirement";
import { RequirementImage } from "@/models/Image";
import IRBoxContainer from "./IRBoxContainer";
import { Box, Typography } from "@mui/material";
import { useReportStore } from "@/components/App/Inspections/Profile/Reports/reportStore";
import { DRAWER_WIDTHS } from "@/utils/constants";
import RequirementDrawer from "@/components/App/Inspections/Profile/Requirements/RequirementDrawer";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useDrawer } from "@/store/drawerStore";
import { notify } from "@/store/snackbarStore";
import { Inspection } from "@/models/Inspection";
import { useQueryClient } from "@tanstack/react-query";
import { useRequirementStore } from "@/components/App/Inspections/Profile/Requirements/requirementStore";
import IRImageSection from "./IRImageSection";
import { useRequirementDocumentImages, useRequirementSourceImages } from "@/hooks/useInspectionRequirements";
import useResponsiveDrawerWidth from "@/hooks/useResponsiveDrawerWidth";

const DetailSection = ({
  title,
  subTitle,
  content,
  appendixNo,
  detailSectionImages,
}: {
  title: string;
  subTitle?: string;
  content: string;
  appendixNo?: string;
  detailSectionImages?: RequirementImage[];
}) => (
  <>
    <Typography variant="body1" mb={0.5}>
      <strong>{title}</strong>
      {appendixNo && ` (Appendix ${appendixNo})`}
    </Typography>
    {subTitle && (
      <Typography variant="body1" mb={0.5}>
        <strong>{subTitle}</strong>
      </Typography>
    )}
    <Typography
      variant="body1"
      component={"div"}
      className="editor-content"
      mb={1.5}
      dangerouslySetInnerHTML={{ __html: content || "" }}
    />
    {detailSectionImages && detailSectionImages.length > 0 && (
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
        {detailSectionImages.map((image) => {
          const filenameWithoutExt = image.original_file_name?.includes('.') 
            ? image.original_file_name.substring(0, image.original_file_name.lastIndexOf('.'))
            : image.original_file_name;
          return (
            <IRImageSection key={image.id} image={{...image, caption: filenameWithoutExt}} />
          );
        })}
      </Box>
    )}
  </>
);

const BottomSection = ({
  title,
  content,
}: {
  title: string;
  content: string;
}) => {
  return (
    <Box sx={{ display: "flex", gap: 0.5 }}>
      <Typography variant="body1" fontWeight={"bold"}>
        {title}
      </Typography>
      <Typography variant="body1">{content}</Typography>
    </Box>
  );
};

const IRRequirement = ({
  requirement,
  requirementIndex,
}: {
  requirement: InspectionRequirement;
  requirementIndex: number;
}) => {
  const { inspectionData, isReportsReadOnly } = useReportStore();
  const { requirementPhotos, requirementFigures } = useRequirementStore();
  const { data: requirementSourceImages } = useRequirementSourceImages(inspectionData?.id ?? 0, requirement.id, 540000);
  const { data: requirementDocumentImages } = useRequirementDocumentImages(inspectionData?.id ?? 0, requirement.id, 540000);

  const { setOpen, setClose } = useDrawer();
  const queryClient = useQueryClient();
  const [photos, setPhotos] = useState<RequirementImage[]>([]);
  const [figures, setFigures] = useState<RequirementImage[]>([]);

  useEffect(() => {
    setPhotos(requirementPhotos.get(requirement.id) ?? []);
    setFigures(requirementFigures.get(requirement.id) ?? []);
  }, [requirementPhotos, requirementFigures, requirement]);

  const handleOnSubmit = useCallback(
    (submitMsg: string) => {
      queryClient.invalidateQueries({
        queryKey: ["inspection-requirements", inspectionData?.id],
      });
      queryClient.invalidateQueries({
        queryKey: ["inspection-requirement-images", inspectionData?.id],
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
          requirement={requirement}
          index={requirementIndex}
        />
      ),
      width: drawerWidth,
    });
  }, [setOpen, handleOnSubmit, inspectionData, requirement, requirementIndex]);

  // Group requirement_source_details by requirement_source_id
  const groupedRequirementSources = useMemo(() => {
    return requirement.requirement_source_details.reduce((acc, item) => {
      const sourceId = item.requirement_source?.id;
      if (sourceId === undefined) {
        return acc;
      }
      if (!acc.has(String(sourceId))) {
        acc.set(String(sourceId), []);
      }
      acc.get(String(sourceId))!.push(item);
      return acc;
    }, new Map<string, (typeof requirement.requirement_source_details)[0][]>());
  }, [requirement]);

  return (
    <IRBoxContainer
      title={`#${requirementIndex + 1}. ${requirement.summary}`}
      onEdit={!isReportsReadOnly ? handleOpenEditRequirementModal : undefined}
    >
      {Array.from(groupedRequirementSources.entries()).map(
        ([sourceId, reqSourceDetails], groupIndex) => (
          <Box key={sourceId} sx={{ mb: 3 }}>
            {reqSourceDetails.map((reqSourceDetail) => (
              <Box key={reqSourceDetail.id} sx={{ mb: 2 }}>
                <DetailSection
                  title={`${groupIndex === 0 ? `Requirement ${requirementIndex + 1}:` : ""} 
                  ${reqSourceDetail.condition_number ? `Condition ${reqSourceDetail.condition_number}` : `Section ${reqSourceDetail.section_number}`}
                  of ${reqSourceDetail.source_title || ""}`}
                  subTitle={reqSourceDetail.title || ""}
                  content={reqSourceDetail.description || ""}
                  appendixNo={reqSourceDetail.appendix?.appendix_no}
                  detailSectionImages={requirementSourceImages?.filter(image => image.req_detail_id === reqSourceDetail.id) ?? []}
                />
                {reqSourceDetail.documents.map((document) => (
                  <DetailSection
                    key={document.id}
                    title={`${document.document_title} Section ${document.section_number ?? ""} ${document.section_title ?? ""}`}
                    content={document.description || ""}
                    appendixNo={document.appendix?.appendix_no}
                    detailSectionImages={requirementDocumentImages?.filter(image => image.req_detail_doc_id === document.id) ?? []}
                  />
                ))}
              </Box>
            ))}
          </Box>
        )
      )}

      <DetailSection
        title="Inspection Details:"
        content={requirement.findings || ""}
      />

      {photos.map((photo) => (
        <IRImageSection key={photo.id} image={photo} />
      ))}

      {figures.map((figure) => (
        <IRImageSection key={figure.id} image={figure} />
      ))}

      <BottomSection
        title="Compliance Finding:"
        content={requirement.compliance_finding?.name || ""}
      />
      <BottomSection
        title="Enforcement Action:"
        content={
          requirement.enforcement_action_data
            ?.map((action) => action.name)
            .join(", ") || ""
        }
      />
    </IRBoxContainer>
  );
};

export default IRRequirement;
