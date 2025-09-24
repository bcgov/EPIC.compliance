import { Box, Typography, Chip } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import { ReviewBoardSection as ReviewBoardSectionType } from "@/models/ReviewBoard";
import ReviewBoardSectionItem from "@/components/App/ReviewBoard/ReviewBoardSectionItem";
import { ReviewBoardCardTypeEnum } from "@/components/App/ReviewBoard/ReviewBoardUtils";

const ReviewBoardSection = ({
  section,
}: {
  section: ReviewBoardSectionType;
}) => {
  return (
    <Box
      key={section.id}
      sx={{
        display: "flex",
        flexDirection: "column",
        gap: 1,
        backgroundColor: BCDesignTokens.surfaceColorBackgroundLightGray,
        borderRadius: BCDesignTokens.layoutBorderRadiusMedium,
        p: 1,
        flex: 1,
        minWidth: 0,
        height: "calc(100% - 1rem)", // 1rem is the margin bottom of the main page box
      }}
    >
      <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, pb: 1 }}>
        <Typography
          variant="caption"
          color={BCDesignTokens.typographyColorDisabled}
          fontWeight={BCDesignTokens.typographyFontWeightsBold}
        >
          {section.sectionTitle}
        </Typography>
        <Chip
          size="small"
          color="default"
          label={section.items.length}
          sx={{
            backgroundColor: BCDesignTokens.typographyColorSecondaryInvert,
            color: BCDesignTokens.typographyColorPlaceholder,
            fontWeight: BCDesignTokens.typographyFontWeightsBold,
            borderRadius: BCDesignTokens.layoutBorderRadiusMedium,
          }}
        />
      </Box>
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          gap: 1,
          overflow: "auto",
          flex: 1,
        }}
      >
        {section.items.map((item) => (
          <ReviewBoardSectionItem
            key={item.id}
            item={item}
            sectionId={section.id as ReviewBoardCardTypeEnum}
          />
        ))}
      </Box>
    </Box>
  );
};

export default ReviewBoardSection;
