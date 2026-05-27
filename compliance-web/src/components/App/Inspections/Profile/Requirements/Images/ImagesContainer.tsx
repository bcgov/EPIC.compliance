import { FC, memo, useCallback, useMemo, useState } from "react";
import {
  Box,
  Typography,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from "@mui/material";
import {
  AddRounded,
  ExpandLessRounded,
  ExpandMoreRounded,
} from "@mui/icons-material";
import { BCDesignTokens } from "epic.theme";
import {
  formatRequirementImagesInFindings,
  ImageTypeEnum,
  REGULATORY_CONSIDERATION_TYPE_ID,
  updateImagesWithContinuousSortOrder,
} from "@/components/App/Inspections/Profile/Requirements/RequirementUtils";
import { useModal } from "@/store/modalStore";
import ImageModal from "./ImageModal";
import { RequirementImage } from "@/models/Image";
import ImageCard from "./ImageCard";
import {
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
  TouchSensor,
  MouseSensor,
} from "@dnd-kit/core";
import {
  SortableContext,
  arraySwap,
  rectSwappingStrategy,
} from "@dnd-kit/sortable";
import { useRequirementStore } from "@/components/App/Inspections/Profile/Requirements/requirementStore";
import { useInspectionById } from "@/hooks/useInspections";

type ImagesContainerProps = {
  imageType: ImageTypeEnum;
  inspectionId: number;
  requirementId: number;
  isRegulatoryConsideration: boolean;
  isRequirementEditable?: boolean;
};

const ImagesContainer: FC<ImagesContainerProps> = memo(
  ({
    imageType,
    inspectionId,
    requirementId,
    isRegulatoryConsideration,
    isRequirementEditable,
  }) => {
    const isPhoto = imageType === ImageTypeEnum.PHOTO;
    const { data: inspectionData } = useInspectionById(inspectionId);
    const { setOpen, setClose } = useModal();
    const [isExpanded, setIsExpanded] = useState(true);
    const {
      requirementsList,
      requirementPhotos,
      requirementFigures,
      setRequirementsList,
      setRequirementPhotos,
      setRequirementFigures,
      setIsDataChanged,
      setIsImageChanged,
    } = useRequirementStore();

    const currentRequirementId = !requirementId ? NaN : requirementId;
    const currentRequirementImages = isPhoto ? requirementPhotos : requirementFigures;
    const images = useMemo(
      () => currentRequirementImages.get(currentRequirementId) ?? [],
      [currentRequirementImages, currentRequirementId]
    );

    const activationConstraint = {
      delay: 100,
      tolerance: 0,
    };

    const sensors = useSensors(
      useSensor(PointerSensor, { activationConstraint }),
      useSensor(TouchSensor, { activationConstraint }),
      useSensor(MouseSensor, { activationConstraint })
    );

    function handleDragEnd(event: DragEndEvent) {
      const { active, over } = event;
      if (active.id !== over?.id) {
        const oldIndex = images
          .map((item) => item.id)
          .indexOf(active.id as number);
        const newIndex = images
          .map((item) => item.id)
          .indexOf(over?.id as number);
        const reorderedImages = arraySwap(images, oldIndex, newIndex);
        setImageLists(reorderedImages);
      }
    }

    const getImageIndex = useCallback(() => {
      if (!requirementId) {
        let reqImagesList = Array.from(
          isPhoto ? requirementPhotos.values() : requirementFigures.values()
        ).flat();
        if (!isRegulatoryConsideration) {
          const regConsId = requirementsList.find(
            (req) => req.req_type.id === REGULATORY_CONSIDERATION_TYPE_ID
          )?.id;
          if (regConsId) {
            reqImagesList = reqImagesList.filter(
              (img) => img.requirement_id !== regConsId
            );
          }
        }
        return (reqImagesList.length ?? 0) + 1;
      }
      return images.length > 0
        ? (images[images.length - 1].sort_order || 0) + 1
        : 1;
    }, [
      requirementId,
      requirementPhotos,
      requirementFigures,
      isPhoto,
      isRegulatoryConsideration,
      requirementsList,
      images,
    ]);

    const updateActiveLexicalEditor = useCallback(
      (updatedImages: RequirementImage[], imagesType2: RequirementImage[]) => {
        // Find all active Lexical editor instances on the page
        const editorElements = document.querySelectorAll(".editor-input");

        if (!editorElements.length) return;

        // Flatten all images from all requirements into a single array
        const allImages = [...updatedImages, ...imagesType2];

        // For each editor instance, we need to update the mentions
        editorElements.forEach((editorElement) => {
          // Check if the editor is initialized and is accessible
          if (!editorElement || !(editorElement instanceof HTMLElement)) return;

          // Dispatch a custom event to update mentions in the Lexical editor
          const event = new CustomEvent("lexical-command", {
            bubbles: true,
            cancelable: true,
            detail: {
              type: "update-mentions",
              images: allImages,
            },
          });

          editorElement.dispatchEvent(event);
        });
      },
      []
    );

    const setImageLists = useCallback(
      (imagesList: RequirementImage[]) => {
        const sourceMap = isPhoto ? requirementPhotos : requirementFigures;
        const updatedRequirementImages = new Map<number, RequirementImage[]>(
          Array.from(sourceMap.entries())
        );

        updatedRequirementImages.set(
          currentRequirementId,
          imagesList.map((img) => ({ ...img }))
        );

        const updatedImagesWithSortOrder = updateImagesWithContinuousSortOrder(
          updatedRequirementImages,
          requirementsList
        );

        if (isPhoto) {
          setRequirementPhotos(updatedImagesWithSortOrder);
        } else {
          setRequirementFigures(updatedImagesWithSortOrder);
        }

        /**
         * updatedImagesWithSortOrder is the image map of current type of images (photos or figures)
         * requirementImagesType2 is the image map of other type of images
         * formatRequirementImagesInFindings will merge the two maps and return the updated requirements findings and list
         */
        const requirementImagesType2 = isPhoto
          ? requirementFigures
          : requirementPhotos;
        const updatedRequirementsList = formatRequirementImagesInFindings(
          requirementsList,
          updatedImagesWithSortOrder,
          requirementImagesType2
        );
        setRequirementsList(updatedRequirementsList);

        // Pass all images (all requirements, both types) so cross-requirement mention chips update correctly.
        updateActiveLexicalEditor(
          Array.from(updatedImagesWithSortOrder.values()).flat(),
          Array.from(requirementImagesType2.values()).flat()
        );

        setIsDataChanged(true);
        setIsImageChanged(true);
      },
      [
        isPhoto,
        requirementPhotos,
        requirementFigures,
        currentRequirementId,
        requirementsList,
        setRequirementsList,
        updateActiveLexicalEditor,
        setIsDataChanged,
        setIsImageChanged,
        setRequirementPhotos,
        setRequirementFigures,
      ]
    );

    const selectImage = useCallback(() => {
      const input = document.createElement("input");
      input.type = "file";
      input.accept = "image/*";
      input.onchange = (event) => {
        const file = (event.target as HTMLInputElement).files?.[0];
        if (file) {
          setOpen({
            content: (
              <ImageModal
                onSubmit={(image) => {
                  setClose();
                  const newImages = [...images, image];
                  setImageLists(newImages);
                }}
                file={file}
                inspectionId={inspectionId}
                imageType={imageType}
                imageIndex={getImageIndex()}
                primaryOfficer={inspectionData?.primary_officer}
              />
            ),
            width: "640px",
          });
        }
      };
      input.click();
    }, [
      setOpen,
      inspectionId,
      imageType,
      getImageIndex,
      setClose,
      images,
      setImageLists,
      inspectionData,
    ]);

    const handleImageClick = useCallback(
      (image: RequirementImage) => {
        setOpen({
          content: (
            <ImageModal
              onSubmit={(updatedImage) => {
                const updatedImages = images.map((img) =>
                  img.id === updatedImage.id ? updatedImage : img
                );
                setImageLists(updatedImages);
                setClose();
              }}
              onDelete={(imageId) => {
                const updatedImages = images.filter(
                  (img) => img.id !== imageId
                );
                setImageLists(updatedImages);
                setClose();
              }}
              requirementImage={image}
              inspectionId={inspectionId}
              imageType={imageType}
              primaryOfficer={inspectionData?.primary_officer}
            />
          ),
          width: "640px",
        });
      },
      [setOpen, inspectionId, imageType, images, setImageLists, setClose, inspectionData]
    );

    return (
      <Accordion
        expanded={isExpanded}
        onChange={(_, expanded) => {
          setIsExpanded(expanded);
        }}
        sx={{
          marginTop: "1rem",
          border: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
          borderRadius: BCDesignTokens.layoutBorderRadiusMedium,
          "&.Mui-expanded:first-of-type": {
            marginTop: "1rem",
          },
        }}
      >
        <AccordionSummary
          aria-controls={`panel-${imageType}-content`}
          id={`panel-${imageType}-header`}
          sx={{
            "&.Mui-expanded": {
              minHeight: "48px",
              padding: "0.875rem 1rem",
              borderBottom: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
              backgroundColor: BCDesignTokens.surfaceColorBackgroundLightGray,
              "& .MuiAccordionSummary-content": {
                margin: "0",
              },
            },
            "& .MuiAccordionSummary-content": {
              display: "flex",
              justifyContent: "space-between",
              gap: "1rem",
            },
          }}
        >
          <Box display={"flex"} alignItems={"flex-start"} gap={0.5}>
            {isExpanded ? <ExpandLessRounded /> : <ExpandMoreRounded />}
            <Typography variant="body2" fontWeight={700}>
              {isPhoto ? "Photos" : "Figures"}
            </Typography>
          </Box>
          {isExpanded && isRequirementEditable && (
            <Button
              variant="text"
              color="secondary"
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                selectImage();
              }}
              startIcon={<AddRounded />}
              sx={{
                backgroundColor: "transparent",
                paddingY: 0,
                height: "auto",
                "& .MuiButton-startIcon": {
                  mr: 0,
                },
              }}
            >
              {isPhoto ? "Photo" : "Figure"}
            </Button>
          )}
        </AccordionSummary>
        <AccordionDetails>
          {images.length === 0 && (
            <Typography
              variant="body2"
              color={BCDesignTokens.typographyColorPlaceholder}
            >
              {isPhoto
                ? "No photos uploaded yet. Add photos to get started"
                : "No figures uploaded yet. Add figures to get started"}
            </Typography>
          )}
          {images.length > 0 && (
            <Box
              sx={{
                display: "flex",
                flexDirection: "row",
                flexWrap: "wrap",
                gap: 1,
              }}
            >
              <DndContext
                sensors={sensors}
                collisionDetection={closestCenter}
                onDragEnd={handleDragEnd}
              >
                <SortableContext
                  items={images.map((image) => image.id ?? 0)}
                  strategy={rectSwappingStrategy}
                  disabled={!isRequirementEditable}
                >
                  {images.map((image, index) => (
                    <ImageCard
                      key={`${image.id}-${index}`}
                      image={image}
                      handleImageClick={() => {
                        handleImageClick(image);
                      }}
                      isPhoto={isPhoto}
                      isRequirementEditable={isRequirementEditable}
                    />
                  ))}
                </SortableContext>
              </DndContext>
            </Box>
          )}
        </AccordionDetails>
      </Accordion>
    );
  }
);

export default ImagesContainer;
