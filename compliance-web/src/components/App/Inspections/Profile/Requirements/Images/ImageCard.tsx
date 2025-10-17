import { Link, Tooltip, IconButton } from "@mui/material";
import { Box } from "@mui/material";
import { RequirementImage } from "@/models/Image";
import { arraySwap, useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import imageNotFound from "@/assets/images/image-not-found.svg";
import { BCDesignTokens } from "epic.theme";
import { DragIndicatorRounded } from "@mui/icons-material";

type ImageCardProps = {
  image: RequirementImage;
  handleImageClick: () => void;
  isPhoto: boolean;
  isRequirementEditable?: boolean;
};

export default function ImageCard({
  image,
  handleImageClick,
  isPhoto,
  isRequirementEditable = true,
}: ImageCardProps) {
  const { attributes, listeners, setNodeRef, transition, transform } =
    useSortable({
      id: image.id ?? 0,
      getNewIndex: ({ id, items, activeIndex, overIndex }) =>
        arraySwap(items, activeIndex, overIndex).indexOf(id),
    });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <Box
      id={image.id?.toString()}
      sx={{
        display: "flex",
        flexDirection: "column",
        width: "calc(50% - 4px)",
        borderRadius: "4px",
        padding: "8px 6px",
        pb: "12px",
        boxSizing: "border-box",
        backgroundColor: BCDesignTokens.surfaceColorBackgroundLightGray,
        cursor: isRequirementEditable ? "pointer" : "default",
        "&:hover": {
          backgroundColor: isRequirementEditable
            ? BCDesignTokens.surfaceColorBackgroundLightBlue
            : "transparent",
        },
      }}
      ref={setNodeRef}
      style={style}
      data-testid={`image-card-${image.id}`}
    >
      <Box sx={{ display: "flex", alignItems: "flex-start" }}>
        {/* Drag Handle */}
        {isRequirementEditable && (
          <IconButton
            sx={{
              height: 140,
              padding: 0,
              marginRight: 0.5,
              borderRadius: 1,
              alignItems: "flex-start",
              cursor: "grab",
              "&:active": {
                cursor: "grabbing",
              },
              "&:hover": {
                backgroundColor: "rgba(0, 0, 0, 0.04)",
              },
            }}
            {...attributes}
            {...listeners}
            onClick={(e) => e.stopPropagation()}
            disableRipple={true}
          >
            <DragIndicatorRounded />
          </IconButton>
        )}
        <Box
          sx={{
            height: 140,
            marginBottom: 0.5,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            overflow: "hidden",
            backgroundColor: "#EDEDED",
          }}
          onClick={isRequirementEditable ? handleImageClick : undefined}
        >
          <img
            src={image.url ?? ""}
            alt={image.caption}
            width={"100%"}
            style={{ pointerEvents: "none" }}
            onError={(e) => {
              e.currentTarget.src = imageNotFound;
              e.currentTarget.style.opacity = "0.5";
              e.currentTarget.style.width = "45%";
              e.currentTarget.style.height = "150px";
            }}
          />
        </Box>
      </Box>
      <Tooltip title={image.caption}>
        <Link
          sx={{
            display: "-webkit-box",
            WebkitBoxOrient: "vertical",
            WebkitLineClamp: 2,
            overflow: "hidden",
            textOverflow: "ellipsis",
            fontSize: "0.75rem",
            textAlign: "center",
            cursor: isRequirementEditable ? "pointer" : "default",
            "&:hover": {
              textDecoration: isRequirementEditable ? "underline" : "none",
            },
          }}
          underline="none"
          onClick={isRequirementEditable ? handleImageClick : undefined}
        >
          <strong>
            {isPhoto ? "Photo" : "Figure"} {image.sort_order}:
          </strong>{" "}
          {image.caption}
        </Link>
      </Tooltip>
    </Box>
  );
}
