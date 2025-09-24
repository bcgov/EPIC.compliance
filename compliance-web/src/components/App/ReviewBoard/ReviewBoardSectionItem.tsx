import { ReviewBoardItem } from "@/models/ReviewBoard";
import { ReviewBoardCardType } from "@/components/App/ReviewBoard/ReviewBoardUtils";
import { APPROVAL_STATUS } from "@/utils/constants";
import dateUtils from "@/utils/dateUtils";
import { CalendarMonthRounded } from "@mui/icons-material";
import { Box, Chip, Typography } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import { useRouter } from "@tanstack/react-router";

const ReviewBoardSectionItem = ({
  item,
  sectionId,
}: {
  item: ReviewBoardItem;
  sectionId: ReviewBoardCardType;
}) => {
  const router = useRouter();

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
        flexShrink: 0,
        cursor: "pointer",
      }}
      onClick={() => {
        // All review board items navigate to their related inspection page
        if (item.ir_number) {
          router.navigate({
            to: "/ce-database/inspections/$inspectionNumber",
            params: { inspectionNumber: item.ir_number },
          });
        }
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
        {item.approval_status &&
        (sectionId === ReviewBoardCardType.DEPUTY_REVIEW ||
          sectionId === ReviewBoardCardType.REVIEW_STATUS) ? (
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
        {item.project_name}
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
        {item.primary_officer?.last_name}
      </Typography>
    </Box>
  );
};

export default ReviewBoardSectionItem;
