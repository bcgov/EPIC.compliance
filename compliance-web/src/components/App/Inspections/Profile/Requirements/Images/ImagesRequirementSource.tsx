import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  Box,
  Button,
  IconButton,
  Stack,
  Typography,
  Popover,
  CircularProgress,
} from "@mui/material";
import {
  CloseRounded,
  ImageOutlined,
  UploadRounded,
} from "@mui/icons-material";
import { BCDesignTokens } from "epic.theme";
import { useImageUpload } from "@/hooks/useImageUpload";
import { RequirementImage, UploadedImageFile } from "@/models/Image";

type ImagesRequirementSourceProps = {
  uploadedImages: RequirementImage[];
  setUploadedImages: React.Dispatch<React.SetStateAction<RequirementImage[]>>;
  inspectionId: number;
};

const ImagesRequirementSource: React.FC<ImagesRequirementSourceProps> = ({
  uploadedImages,
  setUploadedImages,
  inspectionId,
}) => {
  const [previewAnchorEl, setPreviewAnchorEl] = useState<HTMLElement | null>(
    null
  );
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const previousPreviewUrlRef = useRef<string | null>(null);

  const handlePreviewEnter = (
    event: React.MouseEvent<HTMLElement>,
    file: RequirementImage
  ) => {
    setPreviewAnchorEl(event.currentTarget);
    if (previousPreviewUrlRef.current) {
      URL.revokeObjectURL(previousPreviewUrlRef.current);
      previousPreviewUrlRef.current = null;
    }
    const url = file.url ?? "";
    previousPreviewUrlRef.current = url;
    setPreviewUrl(url);
  };

  const handlePreviewLeave = () => {
    setPreviewAnchorEl(null);
    if (previousPreviewUrlRef.current) {
      URL.revokeObjectURL(previousPreviewUrlRef.current);
      previousPreviewUrlRef.current = null;
    }
    setPreviewUrl(null);
  };

  useEffect(() => {
    return () => {
      if (previousPreviewUrlRef.current) {
        URL.revokeObjectURL(previousPreviewUrlRef.current);
        previousPreviewUrlRef.current = null;
      }
    };
  }, []);

  const onSuccess = useCallback(
    (uploadedFile: UploadedImageFile) => {
      const requirementImage: RequirementImage = {
        relative_url: uploadedFile.relative_url,
        url: uploadedFile.presigned_url,
        original_file_name: uploadedFile.fileName,
      };
      setUploadedImages((prevImages) => [...prevImages, requirementImage]);
    },
    [setUploadedImages]
  );

  const { mutate: uploadImage, isPending } = useImageUpload(onSuccess);

  const handleUploadImage = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";
    input.onchange = (event) => {
      const file = (event.target as HTMLInputElement).files?.[0];
      if (file) {
        uploadImage({
          inspectionId: inspectionId,
          fileName: file.name,
          file: file,
        });
      }
    };
    input.click();
  };

  const handleRemoveImage = (index: number) => {
    setUploadedImages((prevImages) => prevImages.filter((_, i) => i !== index));
  };

  return (
    <>
      <Stack direction={"row"} gap={2} alignItems={"center"} sx={{ my: 2 }}>
        <Button
          color="secondary"
          size="small"
          onClick={handleUploadImage}
          startIcon={<UploadRounded />}
        >
          Upload Image
        </Button>
        <Typography variant="caption">
          Uploaded files display as links here, but will be shown as images in
          the report.
        </Typography>
      </Stack>
      {isPending && <CircularProgress size={20} />}
      {!isPending && (
        <Box
          sx={{
            maxHeight: "136px",
            overflow: "scroll",
          }}
        >
          {uploadedImages.map((item, index) => (
            <Box
              key={index}
              sx={{
                mb: 2,
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 1,
                border: "1px solid",
                borderColor: BCDesignTokens.surfaceColorBorderDefault,
                borderRadius: BCDesignTokens.layoutBorderRadiusMedium,
                px: "0.5rem",
                cursor: "pointer",
              }}
              onMouseEnter={(e) => handlePreviewEnter(e, item)}
              onMouseLeave={handlePreviewLeave}
            >
              <Box
                display="flex"
                alignItems="center"
                gap={1}
                color={BCDesignTokens.typographyColorLink}
              >
                <ImageOutlined />
                {item.original_file_name}
              </Box>
              <IconButton onClick={() => handleRemoveImage(index)}>
                <CloseRounded />
              </IconButton>
            </Box>
          ))}
          <Popover
            open={Boolean(previewAnchorEl)}
            anchorEl={previewAnchorEl}
            onClose={handlePreviewLeave}
            anchorOrigin={{ vertical: "top", horizontal: "center" }}
            transformOrigin={{
              vertical: "bottom",
              horizontal: "center",
            }}
            sx={{ pointerEvents: "none" }}
            hidden={!previewUrl}
          >
            <Box
              component="img"
              src={previewUrl ?? ""}
              alt="Preview"
              sx={{
                maxWidth: 450,
                maxHeight: 450,
                objectFit: "contain",
                display: "block",
                padding: "4px",
              }}
            />
          </Popover>
        </Box>
      )}
    </>
  );
};

export default ImagesRequirementSource;
