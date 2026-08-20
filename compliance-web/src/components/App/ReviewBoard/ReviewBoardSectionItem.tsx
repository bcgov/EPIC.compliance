import { ReviewBoardItem } from "@/models/ReviewBoard";
import { ReviewBoardCardTypeEnum } from "@/components/App/ReviewBoard/ReviewBoardUtils";
import {
  AdministrativePenaltyStatus,
  APPROVAL_STATUS,
} from "@/utils/constants";
import dateUtils from "@/utils/dateUtils";
import { CalendarMonthRounded } from "@mui/icons-material";
import { Box, Chip, Divider, Typography } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import { useRouter } from "@tanstack/react-router";

const reviewBoardDateFormat = "DD MMM. YYYY";

const ReviewBoardSectionItem = ({
  item,
  sectionId,
}: {
  item: ReviewBoardItem;
  sectionId: ReviewBoardCardTypeEnum;
}) => {
  const router = useRouter();

  const approvalCardColor = (approvalStatus: string) => {
    if (approvalStatus === APPROVAL_STATUS.APPROVED) {
      return "success";
    } else if (approvalStatus === APPROVAL_STATUS.APPROVAL_PENDING) {
      return "warning";
    } else if (approvalStatus === APPROVAL_STATUS.NOT_APPROVED) {
      return "error";
    } else if (
      approvalStatus === AdministrativePenaltyStatus.DEPUTY_REVIEW_COMPLETE
    ) {
      return "success";
    }
    return "default";
  };

  const getFormattedDate = (date: string | undefined) => {
    return date ? dateUtils.formatDate(date, reviewBoardDateFormat) : "N/A";
  };

  const formatInspectionTypes = (inspectionTypes: string) => {
    return inspectionTypes.replace("Administrative", "Admin");
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
        minWidth: 200,
        maxWidth: 280,
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
        (sectionId === ReviewBoardCardTypeEnum.DEPUTY_REVIEW ||
          sectionId === ReviewBoardCardTypeEnum.REVIEW_STATUS) ? (
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
          {getFormattedDate(item.card_date)}
        </Typography>
        <Typography
          variant="caption"
          sx={{
            backgroundColor: BCDesignTokens.surfaceColorBackgroundLightGray,
            padding: 0.5,
            marginLeft: 0.5,
            borderRadius: BCDesignTokens.layoutBorderRadiusMedium,
          }}
        >
          {formatInspectionTypes(item.inspection_types)}
        </Typography>
      </Box>
      <Typography
        variant="caption"
        sx={{
          width: "fit-content",
          backgroundColor: BCDesignTokens.surfaceColorBackgroundLightBlue,
          padding: 0.5,
          my: 0.5,
          borderRadius: BCDesignTokens.layoutBorderRadiusMedium,
        }}
      >
        {item.primary_officer?.last_name}
      </Typography>
      {sectionId !== ReviewBoardCardTypeEnum.DRAFTING && (
        <>
          <Divider />
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              mt: 1,
            }}
          >
            {sectionId === ReviewBoardCardTypeEnum.REVIEW_STATUS && (
              <Typography
                variant="caption"
                color={BCDesignTokens.typographyColorPlaceholder}
              >
                Review Date:
                <Typography
                  variant="caption"
                  ml={0.25}
                  fontWeight={BCDesignTokens.typographyFontWeightsBold}
                >
                  {getFormattedDate(item.review_date)}
                </Typography>
              </Typography>
            )}
            {(sectionId === ReviewBoardCardTypeEnum.DEPUTY_REVIEW ||
              sectionId === ReviewBoardCardTypeEnum.REVIEW_STATUS) && (
              <>
                <Typography
                  variant="caption"
                  color={BCDesignTokens.typographyColorPlaceholder}
                >
                  Sent for Review:
                  <Typography
                    variant="caption"
                    ml={0.25}
                    fontWeight={
                      sectionId === ReviewBoardCardTypeEnum.REVIEW_STATUS
                        ? BCDesignTokens.typographyFontWeightsRegular
                        : BCDesignTokens.typographyFontWeightsBold
                    }
                  >
                    {getFormattedDate(item.send_for_review_date)}
                  </Typography>
                </Typography>
                {item.deputy_director && (
                  <Typography
                    variant="caption"
                    color={BCDesignTokens.typographyColorPlaceholder}
                  >
                    Deputy Director:
                    <Typography variant="caption" ml={0.25}>
                      {item.deputy_director.last_name}
                    </Typography>
                  </Typography>
                )}
              </>
            )}
            {sectionId === ReviewBoardCardTypeEnum.HOLDER_REVIEW && (
              <>
                <Typography
                  variant="caption"
                  color={BCDesignTokens.typographyColorPlaceholder}
                >
                  Due Date:
                  <Typography
                    variant="caption"
                    ml={0.25}
                    fontWeight={BCDesignTokens.typographyFontWeightsBold}
                  >
                    {getFormattedDate(item.expected_return_date)}
                  </Typography>
                </Typography>
                <Typography
                  variant="caption"
                  color={BCDesignTokens.typographyColorPlaceholder}
                >
                  Report Sent:
                  <Typography variant="caption" ml={0.25}>
                    {getFormattedDate(item.date_report_sent)}
                  </Typography>
                </Typography>
              </>
            )}
            {sectionId === ReviewBoardCardTypeEnum.FINALIZING_RECORD && (
              <Typography
                variant="caption"
                color={BCDesignTokens.typographyColorPlaceholder}
              >
                Response Date:
                <Typography variant="caption" ml={0.25}>
                  {getFormattedDate(item.date_response)}
                </Typography>
              </Typography>
            )}
            {sectionId === ReviewBoardCardTypeEnum.PENDING_ISSUANCE && (
              <>
                <Typography
                  variant="caption"
                  color={BCDesignTokens.typographyColorPlaceholder}
                >
                  Issuance Date:
                  <Typography variant="caption" ml={0.25}>
                    {getFormattedDate(item.intended_issuance_date)}
                  </Typography>
                </Typography>
                {item.issuing_officer && (
                  <Typography
                    variant="caption"
                    color={BCDesignTokens.typographyColorPlaceholder}
                  >
                    Issuing Officer:
                    <Typography variant="caption" ml={0.25}>
                      {item.issuing_officer?.last_name}
                    </Typography>
                  </Typography>
                )}
              </>
            )}
          </Box>
        </>
      )}
    </Box>
  );
};

export default ReviewBoardSectionItem;
