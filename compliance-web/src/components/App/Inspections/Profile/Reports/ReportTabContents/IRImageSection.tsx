import { RequirementImage } from "@/models/Image";
import { Typography } from "@mui/material";
import { Box } from "@mui/material";
import imageNotFound from "@/assets/images/image-not-found.svg";

const IRImageSection = ({ image }: { image: RequirementImage }) => {
  return (
    <Box key={image.id} sx={{ marginBottom: 2 }}>
      <Box
        sx={{
          height: 150,
          width: 200,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          overflow: "hidden",
          borderRadius: 2,
        }}
      >
        <img
          src={image.url ?? ""}
          alt={image.caption}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
          onError={(e) => {
            e.currentTarget.src = imageNotFound;
            e.currentTarget.style.opacity = "0.5";
            e.currentTarget.style.width = "45%";
            e.currentTarget.style.height = "150px";
            e.currentTarget.style.objectFit = "contain";
          }}
        />
      </Box>
      <Typography variant="caption">
        {image.image_type ? `${image.image_type} ${image.sort_order}. ` : ""}
        {image.caption}
      </Typography>
    </Box>
  );
};

export default IRImageSection;
