import { AdministrativePenalty } from "@/models/AdministrativePenalty";
import { ChargeRecommendation } from "@/models/ChargeRecommendation";
import { InspectionOrder } from "@/models/InspectionOrder";
import { InspectionWarningLetter } from "@/models/InspectionWarningLetter";
import { ViolationTicket } from "@/models/ViolationTicket";
import { RestorativeJustice } from "@/models/RestorativeJustice";
import {
  OrderProgressEnum,
  OrderStatusEnum,
  VARIANT_COLORS,
  WarningLetterProgressEnum,
  APReferralStatus,
  CRStatus,
  ViolationTicketStatus,
  RestorativeJusticeStatus,
  EnforcementActionEnum,
} from "@/utils/constants";
import { Chip } from "@mui/material";
import { useMemo } from "react";
import { InspectionMoreDetailsEnforcementAction } from "@/models/Inspection";
import { FC } from "react";

interface EnforcementStatusFlagProps {
  enforcementActionType: EnforcementActionEnum;
  enforcementActionDetails?: InspectionMoreDetailsEnforcementAction;
  order?: InspectionOrder;
  warningLetter?: InspectionWarningLetter;
  administrativePenalty?: AdministrativePenalty;
  chargeRecommendation?: ChargeRecommendation;
  violationTicket?: ViolationTicket;
  restorativeJustice?: RestorativeJustice;
}

const EnforcementStatusFlag: FC<EnforcementStatusFlagProps> = ({
  enforcementActionType,
  enforcementActionDetails,
  order,
  warningLetter,
  administrativePenalty,
  chargeRecommendation,
  violationTicket,
  restorativeJustice,
}) => {
  const flagStatus = useMemo(() => {
    let status: {
      name: string;
      color?: VARIANT_COLORS;
    } = {
      name: "",
      color: "default",
    };
    if (enforcementActionType === EnforcementActionEnum.ORDER) {
      const orderProgress =
        enforcementActionDetails?.progress || order?.order_progress;
      const orderStatus =
        enforcementActionDetails?.status || order?.order_status;
      status = {
        name: orderProgress?.name || "",
      };
      if (orderProgress?.id === OrderProgressEnum.APPROVED) {
        status.color = "success";
      } else if (orderProgress?.id === OrderProgressEnum.DEPUTY_REVIEW) {
        status.color = "warning";
      } else if (orderProgress?.id === OrderProgressEnum.ISSUED) {
        status.name = "Open";
        status.color = "success";
        if (
          orderStatus?.id === OrderStatusEnum.CLOSED ||
          orderStatus?.id === OrderStatusEnum.RESCINDED
        ) {
          status.name = orderStatus?.name || "";
          status.color = "error";
        }
      }
    } else if (enforcementActionType === EnforcementActionEnum.WARNING_LETTER) {
      const warningLetterProgress =
        enforcementActionDetails?.progress || warningLetter?.progress;
      status = {
        name: warningLetterProgress?.name || "",
      };
      if (warningLetterProgress?.id === WarningLetterProgressEnum.APPROVED) {
        status.color = "success";
      } else if (
        warningLetterProgress?.id === WarningLetterProgressEnum.DEPUTY_REVIEW
      ) {
        status.color = "warning";
      } else if (
        warningLetterProgress?.id === WarningLetterProgressEnum.ISSUED
      ) {
        status.color = "success";
      }
    } else if (
      enforcementActionType === EnforcementActionEnum.AP_RECOMMENDATION
    ) {
      const administrativePenaltyStatus =
        enforcementActionDetails?.status ||
        administrativePenalty?.referral_status;
      status = {
        name: administrativePenaltyStatus?.name || "",
      };
      if (administrativePenaltyStatus?.id === APReferralStatus.DEPUTY_REVIEW.id) {
        status.color = "warning";
      } else if (
        administrativePenaltyStatus?.id ===
        APReferralStatus.DEPUTY_REVIEW_COMPLETE.id
      ) {
        status.color = "success";
      } else if (
        administrativePenaltyStatus?.id === APReferralStatus.AP_NOT_PROCEEDING.id
      ) {
        status.color = "error";
      } else if (
        administrativePenaltyStatus?.id === APReferralStatus.REFERRED_TO_DM.id
      ) {
        status.color = "success";
      }
    } else if (
      enforcementActionType === EnforcementActionEnum.CHARGE_RECOMMENDATION
    ) {
      const chargeRecommendationStatus =
        enforcementActionDetails?.status || chargeRecommendation?.status;
      status = {
        name: chargeRecommendationStatus?.name || CRStatus.DRAFTING.name,
      };
      if (
        chargeRecommendationStatus?.id ===
        CRStatus.SUBMITTED_TO_CROWN_COUNSEL.id
      ) {
        status.color = "success";
      } else if (chargeRecommendationStatus?.id === CRStatus.DEPUTY_REVIEW.id) {
        status.color = "warning";
      } else if (
        chargeRecommendationStatus?.id === CRStatus.CEB_NOT_PROCEEDING.id
      ) {
        status.color = "error";
      }
    } else if (
      enforcementActionType === EnforcementActionEnum.VIOLATION_TICKET
    ) {
      const violationTicketStatus =
        enforcementActionDetails?.status || violationTicket?.status;
      status = {
        name: violationTicketStatus?.name || "",
      };
      if (violationTicketStatus?.id === ViolationTicketStatus.ISSUED) {
        status.color = "success";
      } else if (violationTicketStatus?.id === ViolationTicketStatus.PAID) {
        status.color = "success";
      } else if (violationTicketStatus?.id === ViolationTicketStatus.DISPUTED) {
        status.color = "error";
      }
      else if (violationTicketStatus?.id === ViolationTicketStatus.DEEMED_GUILTY) {
        status.color = "error";
      }
    } else if (
      enforcementActionType === EnforcementActionEnum.RESTORATIVE_JUSTICE
    ) {
      const restorativeJusticeStatus =
        enforcementActionDetails?.status || restorativeJustice?.status;
      status = {
        name: restorativeJusticeStatus?.name || "",
      };
      if (restorativeJusticeStatus?.id === RestorativeJusticeStatus.OPEN) {
        status.color = "success";
      } else if (
        restorativeJusticeStatus?.id === RestorativeJusticeStatus.CLOSED
      ) {
        status.color = "error";
      }
    }

    return status;
  }, [
    enforcementActionType,
    enforcementActionDetails,
    order,
    warningLetter,
    administrativePenalty,
    chargeRecommendation,
    violationTicket,
    restorativeJustice,
  ]);
  
  return flagStatus.name ? (
    <Chip
      label={flagStatus.name}
      color={flagStatus.color}
      size="small"
      variant="outlined"
    />
  ) : null;
};

export default EnforcementStatusFlag;
