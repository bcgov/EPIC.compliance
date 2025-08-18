import GridLabelValuePair from "@/components/Shared/GridLabelValuePair";
import { InspectionOrder } from "@/models/InspectionOrder";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { InspectionWarningLetter } from "@/models/InspectionWarningLetter";
import dateUtils from "@/utils/dateUtils";
import { Box, Grid, Stack, Typography } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import EnforcementStatusFlag from "@/components/App/Inspections/Profile/Enforcements/EnforcementStatusFlag";
import {
  formatRequirementSummary,
  formatRequirementSources,
  getSentForReviewDate,
  getApprovedByDate,
  getApproverName,
} from "@/components/App/Inspections/Profile/Enforcements/EnforcementUtils";
import { AdministrativePenalty } from "@/models/AdministrativePenalty";
import { ChargeRecommendation } from "@/models/ChargeRecommendation";
import { ViolationTicket } from "@/models/ViolationTicket";

const EnforcementCard = ({
  order,
  warningLetter,
  requirementEnforcements,
  administrativePenalty,
  chargeRecommendation,
  violationTicket,
}: {
  order?: InspectionOrder;
  warningLetter?: InspectionWarningLetter;
  requirementEnforcements: InspectionRequirement[];
  administrativePenalty?: AdministrativePenalty;
  chargeRecommendation?: ChargeRecommendation;
  violationTicket?: ViolationTicket;
}) => {
  // console.log(chargeRecommendation)
  const requirementSummaryFormatted = formatRequirementSummary(
    order,
    warningLetter,
    administrativePenalty,
    chargeRecommendation,
    violationTicket
  );
  const requirementSourcesFormatted = formatRequirementSources(
    requirementEnforcements,
    order,
    warningLetter,
    administrativePenalty,
    chargeRecommendation,
    violationTicket
  );
  const sentForReviewDate = getSentForReviewDate(order, warningLetter);
  const approvedByDate = getApprovedByDate(order, warningLetter);
  const approverName = getApproverName(order, warningLetter);

  return (
    <Box
      sx={{
        backgroundColor: BCDesignTokens.surfaceColorBackgroundWhite,
        mb: 2,
        border: `1px solid ${BCDesignTokens.surfaceColorBorderDefault}`,
        borderRadius: BCDesignTokens.layoutBorderRadiusMedium,
        "&:hover": {
          cursor: "pointer",
          boxShadow: `0px 4px 6px 0px ${BCDesignTokens.surfaceColorBorderDefault}`,
        },
      }}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          p: "0.75rem 1.5rem",
          backgroundColor: BCDesignTokens.surfaceColorBackgroundLightGray,
        }}
      >
        <Stack direction="row" alignItems="center" gap={1}>
          <Typography
            variant="body1"
            color={BCDesignTokens.typographyColorLink}
          >
            {order?.order_number ??
              warningLetter?.warning_letter_number ??
              administrativePenalty?.administrative_penalty_number ??
              chargeRecommendation?.charge_recommendation_number ??
              violationTicket?.vt_number}
          </Typography>
          <EnforcementStatusFlag
            order={order}
            warningLetter={warningLetter}
            administrativePenalty={administrativePenalty}
            chargeRecommendation={chargeRecommendation}
            violationTicket={violationTicket}
          />
        </Stack>
        <Stack>
          {requirementSourcesFormatted?.map((source) => {
            return (
              <Typography key={source} variant="caption" component={"div"}>
                {source}
              </Typography>
            );
          })}
        </Stack>
      </Box>
      <Box
        sx={{
          p: "0.5rem 1.5rem 1rem",
        }}
      >
        <Grid container spacing={0.5}>
          <GridLabelValuePair
            label="Requirement Summary"
            value={requirementSummaryFormatted}
            multiline
          />
          {(order || warningLetter) && (
            <>
              <GridLabelValuePair
                label="Deputy Director, Compliance & Enforcement Operations"
                value={approverName}
              />
              <GridLabelValuePair
                label="Sent for Review"
                value={sentForReviewDate}
                gridProps={{ xs: 3 }}
              />
              <GridLabelValuePair
                label="Approved by Deputy"
                value={approvedByDate}
                gridProps={{ xs: 3 }}
              />
              <GridLabelValuePair
                label="Date Issued"
                value={
                  (order || warningLetter)?.date_issued
                    ? dateUtils.formatDate(
                        (order || warningLetter)?.date_issued ?? ""
                      )
                    : ""
                }
                gridProps={{ xs: 6 }}
              />
            </>
          )}
          {administrativePenalty && (
            <>
              <GridLabelValuePair
                label="Date Referred to Decision Maker"
                value={
                  administrativePenalty.date_referred
                    ? dateUtils.formatDate(administrativePenalty.date_referred)
                    : ""
                }
                gridProps={{ xs: 6 }}
              />
              <GridLabelValuePair
                label="Decision Date"
                value={
                  administrativePenalty.decision_date
                    ? dateUtils.formatDate(administrativePenalty.decision_date)
                    : ""
                }
                gridProps={{ xs: 6 }}
              />
              <GridLabelValuePair
                label="Decision"
                value={administrativePenalty.decision?.name || ""}
                gridProps={{ xs: 6 }}
              />
              {administrativePenalty.penalty_amount && (
                <GridLabelValuePair
                  label="Penalty Amount"
                  value={`$${administrativePenalty.penalty_amount}`}
                  gridProps={{ xs: 6 }}
                />
              )}
            </>
          )}
          {chargeRecommendation && (
            <>
              <GridLabelValuePair
                label="Date to Crown Counsel"
                value={
                  chargeRecommendation.date_to_crown_counsel
                    ? dateUtils.formatDate(chargeRecommendation.date_to_crown_counsel)
                    : ""
                }
                gridProps={{ xs: 6 }}
              />
              <GridLabelValuePair
                label="Court File #"
                value={chargeRecommendation.court_file_number || ""}
                gridProps={{ xs: 6 }}
              />
              <GridLabelValuePair
                label="Charge Decision"
                value={chargeRecommendation.charge_decision?.name || ""}
                gridProps={{ xs: 6 }}
              />
              <GridLabelValuePair
                label="Charge Decision Date"
                value={
                  chargeRecommendation.charge_decision_date
                    ? dateUtils.formatDate(chargeRecommendation.charge_decision_date)
                    : ""
                }
                gridProps={{ xs: 6 }}
              />
              <GridLabelValuePair
                label="Court Appearances"
                value={chargeRecommendation.court_appearances || ""}
                multiline
              />
              <GridLabelValuePair
                label="Judgement"
                value={chargeRecommendation.judgment?.name || ""}
                gridProps={{ xs: 6 }}
              />
              <GridLabelValuePair
                label="Judgement Date"
                value={
                  chargeRecommendation.judgment_date
                    ? dateUtils.formatDate(chargeRecommendation.judgment_date)
                    : ""
                }
                gridProps={{ xs: 6 }}
              />
              <GridLabelValuePair
                label="Sentence Date"
                value={
                  chargeRecommendation.sentence_date
                    ? dateUtils.formatDate(chargeRecommendation.sentence_date)
                    : ""
                }
                gridProps={{ xs: 6 }}
              />
              <GridLabelValuePair
                label="Sentence Type"
                value={chargeRecommendation.sentence_type || ""}
                gridProps={{ xs: 6 }}
              />
            </>
          )}
          {violationTicket && (
            <>
              <GridLabelValuePair
                label="Ticket #"
                value={violationTicket.ticket_number || ""}
                gridProps={{ xs: 6 }}
              />
              <GridLabelValuePair
                label="Date Issued"
                value={
                  violationTicket.date_issued
                    ? dateUtils.formatDate(violationTicket.date_issued)
                    : ""
                }
                gridProps={{ xs: 6 }}
              />
             
              <GridLabelValuePair
                label="Fine Amount"
                value={`$${violationTicket.fine_amount || 0}`}
                gridProps={{ xs: 6 }}
              />
               <GridLabelValuePair
                label="Status Date"
                value={ violationTicket.status_date
                    ? dateUtils.formatDate(violationTicket.status_date)
                    : ""}
                gridProps={{ xs: 6 }}
              />
            </>
          )}
        </Grid>
      </Box>
    </Box>
  );
};

export default EnforcementCard;
