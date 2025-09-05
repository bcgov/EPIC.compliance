import { ReviewBoardItem } from "@/models/ReviewBoard";
import { APPROVAL_STATUS } from "@/utils/constants";
import dateUtils from "@/utils/dateUtils";
import { CalendarMonthRounded } from "@mui/icons-material";
import { Box, Chip, Typography } from "@mui/material";
import { BCDesignTokens } from "epic.theme";

const ReviewBoardSectionItem = ({ item }: { item: ReviewBoardItem }) => {
  const approvalCardColor = (approvalStatus: string) => {
    if (approvalStatus === APPROVAL_STATUS.APPROVED) {
      return "success";
    } else if (approvalStatus === APPROVAL_STATUS.APPROVAL_PENDING) {
      return "warning";
    } else if (approvalStatus === APPROVAL_STATUS.NOT_APPROVED) {
      return "error";
    }
    return "default";
  };

  return (
    <Box
      key={item.id}
      sx={{
        display: "flex",
        flexDirection: "column",
        p: 1,
        backgroundColor: BCDesignTokens.surfaceColorBackgroundWhite,
        borderRadius: BCDesignTokens.layoutBorderRadiusMedium,
        border: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
        // height: 400,
        flexShrink: 0,
      }}
    >
      <Box
        sx={{
          display: "flex",
          flexWrap: "wrap",
          gap: 0.5,
          mb: 1,
        }}
      >
        <Chip
          variant="outlined"
          size="small"
          color={item.card_type.name === "IR" ? "default" : "warning"}
          label={`${item.card_type.name}${item.card_type.sub_type ? `: ${item.card_type.sub_type}` : ""}`}
          sx={{
            width: "fit-content",
            fontSize: "0.75rem",
          }}
        />
        {item.approval_status ? (
          <Chip
            variant="outlined"
            size="small"
            color={approvalCardColor(item.approval_status.id)}
            label={item.approval_status.name}
            sx={{
              width: "fit-content",
              fontSize: "0.75rem",
            }}
          />
        ) : null}
      </Box>
      <Typography
        variant="body2"
        fontWeight={BCDesignTokens.typographyFontWeightsBold}
        color={BCDesignTokens.typographyColorLink}
        sx={{
          wordWrap: "break-word",
          overflowWrap: "break-word",
          whiteSpace: "normal",
          width: "100%",
        }}
      >
        {item.number}
      </Typography>
      <Typography
        variant="caption"
        color={BCDesignTokens.typographyColorPlaceholder}
      >
        {item.name}
      </Typography>
      <Box sx={{ display: "flex", alignItems: "center", mt: 1 }}>
        <CalendarMonthRounded
          sx={{
            fontSize: "1rem",
            marginRight: 0.25,
            color: BCDesignTokens.typographyColorDisabled,
          }}
        />
        <Typography variant="caption">
          {dateUtils.formatDate(item.card_date)}
        </Typography>
        {item.types ? (
          <Typography
            variant="caption"
            sx={{
              backgroundColor: BCDesignTokens.surfaceColorBackgroundLightGray,
              padding: 0.5,
              marginLeft: 0.5,
              borderRadius: BCDesignTokens.layoutBorderRadiusMedium,
            }}
          >
            {item.types.map((type) => type.name).join(", ")}
          </Typography>
        ) : null}
      </Box>
      <Typography
        variant="caption"
        sx={{
          width: "fit-content",
          backgroundColor: BCDesignTokens.surfaceColorBackgroundLightBlue,
          padding: 0.5,
          borderRadius: BCDesignTokens.layoutBorderRadiusMedium,
        }}
      >
        {item.primary_officer.last_name}
      </Typography>
    </Box>
  );
};

export default ReviewBoardSectionItem;
