import { InspectionRequirement } from "@/models/InspectionRequirement";
import { InspectionOrder } from "@/models/InspectionOrder";
import { InspectionWarningLetter } from "@/models/InspectionWarningLetter";
import {
  defaultRequirementDeleteWarning,
  EnforcementActionEnum,
  hasLinkedEnforcementDeleteWarning,
} from "@/utils/constants";
import * as yup from "yup";
import dateUtils from "@/utils/dateUtils";
import { AdministrativePenalty } from "@/models/AdministrativePenalty";
import { ChargeRecommendation } from "@/models/ChargeRecommendation";
import { ViolationTicket } from "@/models/ViolationTicket";
import { RestorativeJustice } from "@/models/RestorativeJustice";

// Base schema for all enforcement types
export const baseEnforcementSchema = yup.object().shape({
  requirements: yup
    .array()
    .of(yup.object<InspectionRequirement>())
    .nullable()
    .min(1, "At least one Requirement is required")
    .required("Requirement is required"),
});

export type BaseEnforcementFormType = yup.InferType<typeof baseEnforcementSchema>;

export const initBaseFormData: BaseEnforcementFormType = {
  requirements: [],
};

// Extended schema for orders with historical record support
export const orderSchema = baseEnforcementSchema.shape({
  isHistoricalRecord: yup.boolean().nullable(),
  manualOrderNumber: yup
    .string()
    .nullable()
    .when("isHistoricalRecord", {
      is: (value: boolean) => value === true,
      then: (schema) => schema.required("Manual Order # is required"),
      otherwise: (schema) => schema.notRequired(),
    }),
  linkedOrderNumber: yup
    .string()
    .nullable(),
});

export type OrderFormType = yup.InferType<typeof orderSchema>;

// Requirement data processing functions
export const prepNonProceededRequirements = (
  {
    requirements,
    reqIds,
    enforcementActionType
  } : {
    requirements: InspectionRequirement[],
    reqIds: (number[] | undefined)[] | undefined,
    enforcementActionType: EnforcementActionEnum
  }
) => {
  const flattenedReqIds = reqIds?.flat() || [];
  const nonProceededRequirements = requirements.filter(
    (requirement) =>
      !flattenedReqIds.includes(requirement.id) &&
      requirement.enforcement_action_data?.some(
        (enforcement) => enforcement.id === enforcementActionType
      )
  );

  return nonProceededRequirements.map(requirement => ({
    ...requirement,
    enforcement_action_data: requirement.enforcement_action_data?.filter(
      (enforcement) => enforcement.id === enforcementActionType
    ) || []
  }));
};

// Determine whether a requirement has an enforcement action record created
export const hasCreatedEnforcementAction = (
  requirement: InspectionRequirement | undefined,
  enforcementsByType: {
    enforcementActionType: EnforcementActionEnum;
    reqIds: (number[] | undefined)[] | undefined;
  }[]
): boolean => {
  if (!requirement) return false;
  return enforcementsByType.some(({ enforcementActionType, reqIds }) => {
    const isMarkedForType = requirement.enforcement_action_data?.some(
      (enforcement) => enforcement.id === enforcementActionType
    );
    if (!isMarkedForType) return false;
    const nonProceeded = prepNonProceededRequirements({
      requirements: [requirement],
      reqIds,
      enforcementActionType,
    });
    return nonProceeded.length === 0;
  });
};

// Determine which warning message to display to user
export const getRequirementDeleteWarning = (
  requirement: InspectionRequirement | undefined,
  enforcementsByType: {
    enforcementActionType: EnforcementActionEnum;
    reqIds: (number[] | undefined)[] | undefined;
  }[]
): string =>
  hasCreatedEnforcementAction(requirement, enforcementsByType)
    ? hasLinkedEnforcementDeleteWarning
    : defaultRequirementDeleteWarning;

export const formatRequirementSummary = (
  order?: InspectionOrder,
  warningLetter?: InspectionWarningLetter,
  administrativePenalty?: AdministrativePenalty,
  chargeRecommendation?: ChargeRecommendation,
  violationTicket?: ViolationTicket,
  restorativeJustice?: RestorativeJustice
): string => {
  if (order?.order_requirement_maps) {
    return order.order_requirement_maps
      .map((map) => map.inspection_requirement.summary)
      .join(", ");
  }
  if (warningLetter?.warning_letter_requirement_maps) {
    return warningLetter.warning_letter_requirement_maps
      .map((map) => map.inspection_requirement.summary)
      .join(", ");
  }
  if(administrativePenalty?.administrative_penalty_requirement_maps) {
    return administrativePenalty.administrative_penalty_requirement_maps
      .map((map) => map.inspection_requirement.summary)
      .join(", ");
  }
  if(chargeRecommendation?.charge_recommendation_requirement_maps) {
    return chargeRecommendation.charge_recommendation_requirement_maps
      .map((map) => map.inspection_requirement.summary)
      .join(", ");
  }
  if(violationTicket?.violation_ticket_requirement_maps) {
    return violationTicket.violation_ticket_requirement_maps
      .map((map) => map.inspection_requirement.summary)
      .join(", ");
  }
  if(restorativeJustice?.restorative_justice_requirement_maps) {
    return restorativeJustice.restorative_justice_requirement_maps
      .map((map) => map.inspection_requirement.summary)
      .join(", ");
  }
  return "No requirement summary available";
};

export const formatRequirementSources = (
  requirementEnforcements: InspectionRequirement[],
  order?: InspectionOrder,
  warningLetter?: InspectionWarningLetter,
  administrativePenalty?: AdministrativePenalty,
  chargeRecommendation?: ChargeRecommendation,
  violationTicket?: ViolationTicket,
  restorativeJustice?: RestorativeJustice
): string[] => {
  // Collect all requirement maps from all enforcement types
  const allRequirementMaps = [
    ...(order?.order_requirement_maps || []).map(map => map.inspection_requirement),
    ...(warningLetter?.warning_letter_requirement_maps || []).map(map => map.inspection_requirement),
    ...(administrativePenalty?.administrative_penalty_requirement_maps || []).map(map => map.inspection_requirement),
    ...(chargeRecommendation?.charge_recommendation_requirement_maps || []).map(map => map.inspection_requirement),
    ...(violationTicket?.violation_ticket_requirement_maps || []).map(map => map.inspection_requirement),
    ...(restorativeJustice?.restorative_justice_requirement_maps || []).map(map => map.inspection_requirement),
  ];

  // Check if any requirement has source details from API
  const hasSourceDetailsFromAPI = allRequirementMaps.some(
    req => req.requirement_source_details && req.requirement_source_details.length > 0
  );

  const result: string[] = [];

  if (hasSourceDetailsFromAPI) {
    allRequirementMaps.forEach((requirement) => {
      const sourceMap = new Map<number, { name: string; numbers: string[] }>();

      requirement.requirement_source_details?.forEach((source) => {
        const sourceId = source.requirement_source_id;
        const sourceName = source.requirement_source?.name || "";
        const number = source.condition_number ?? source.section_number ?? "";

        if (!sourceMap.has(sourceId)) {
          sourceMap.set(sourceId, { name: sourceName, numbers: [] });
        }

        if (number) {
          sourceMap.get(sourceId)?.numbers.push(`#${number.trim()}`);
        }
      });

      sourceMap.forEach((value) => {
        if (value.numbers.length > 0) {
          result.push(`${value.name}, ${value.numbers.join(", ")}`);
        } else {
          result.push(value.name);
        }
      });
    });
  } else {
    // Fallback to the old way if no source details are available from API for data safety
    const requirementIds = allRequirementMaps.map(req => req.id);
    const requirements = requirementEnforcements.filter((requirement) =>
      requirementIds?.includes(requirement.id)
    );

    requirements.forEach((requirement) => {
      const sourceMap = new Map<number, { name: string; numbers: string[] }>();

      requirement.requirement_source_details?.forEach((source) => {
        const sourceId = source.requirement_source_id;
        const sourceName = source.requirement_source?.name || "";
        const number = source.condition_number ?? source.section_number ?? "";

        if (!sourceMap.has(sourceId)) {
          sourceMap.set(sourceId, { name: sourceName, numbers: [] });
        }

        if (number) {
          sourceMap.get(sourceId)?.numbers.push(`#${number.trim()}`);
        }
      });

      sourceMap.forEach((value) => {
        if (value.numbers.length > 0) {
          result.push(`${value.name}, ${value.numbers.join(", ")}`);
        } else {
          result.push(value.name);
        }
      });
    });
  }

  return result;
};

// Approval data extraction functions
export const getSentForReviewDate = (
  order?: InspectionOrder,
  warningLetter?: InspectionWarningLetter
): string => {
  let sentForReviewDate: string = "";
  if (order?.order_approvals) {
    sentForReviewDate = order.order_approvals?.[0]?.created_date ?? "";
  }
  if (warningLetter?.warning_letter_approvals) {
    sentForReviewDate =
      warningLetter.warning_letter_approvals?.[0]?.created_date ?? "";
  }
  return sentForReviewDate ? dateUtils.formatDate(sentForReviewDate) : "";
};

export const getApprovedByDate = (
  order?: InspectionOrder,
  warningLetter?: InspectionWarningLetter
): string => {
  let approvedByDate: string = "";
  if (order?.order_approvals) {
    approvedByDate = order.order_approvals?.[0]?.approved_date ?? "";
  }
  if (warningLetter?.warning_letter_approvals) {
    approvedByDate =
      warningLetter.warning_letter_approvals?.[0]?.approved_date ?? "";
  }
  return approvedByDate ? dateUtils.formatDate(approvedByDate) : "";
};

export const getApproverName = (
  order?: InspectionOrder,
  warningLetter?: InspectionWarningLetter
): string => {
  let approverName: string = "";
  if (order?.order_approvals) {
    approverName = order.order_approvals?.[0]?.approved_by?.name ?? "";
  }
  if (warningLetter?.warning_letter_approvals) {
    approverName =
      warningLetter.warning_letter_approvals?.[0]?.approved_by?.name ?? "";
  }
  return approverName;
};

// Utility functions for form handling
export const getDefaultFormValues = (
  requirement?: InspectionRequirement,
  isHistoricalRecord: boolean = false,
  manualOrderNumber?: string
) => {
  if (requirement) {
    return {
      requirements: [requirement],
      isHistoricalRecord,
      manualOrderNumber,
    };
  }
  return {
    requirements: [],
    isHistoricalRecord: false,
    manualOrderNumber: undefined,
  };
};


// Partitions enforcements into two groups: those linked to the current inspection and those linked to other inspections.
// The enforcements linked to the current inspection are returned first, followed by the linked enforcements.
// If there are no linked enforcements, only the created enforcements are returned.
export const partitionEnforcementsByOrigin = <T extends { inspection_id: number }>(enforcements: T[], inspection_id: number): T[] => {
  const linkedEnforcements = enforcements.filter(e => e.inspection_id !== inspection_id);
  const createdEnforcements = enforcements.filter(e => e.inspection_id === inspection_id);
  
  // If there is are linked enforcement, we return them second
  if (linkedEnforcements.length > 0) {
    return [...createdEnforcements, ...linkedEnforcements];
  }
  return createdEnforcements;
}

// Enforcement type constants
export const ENFORCEMENT_TYPES = {
  ORDER: EnforcementActionEnum.ORDER,
  WARNING_LETTER: EnforcementActionEnum.WARNING_LETTER,
} as const;

// Common notification messages
export const ENFORCEMENT_MESSAGES = {
  ORDER_CREATED: (orderNumber: string) => `Order ${orderNumber} created`,
  WARNING_LETTER_CREATED: (warningLetterNumber: string) => `Warning Letter ${warningLetterNumber} created`,
  ADMINISTRATIVE_PENALTY_CREATED: (administrativePenaltyNumber: string) => `Administrative Penalty ${administrativePenaltyNumber} created`,
  CHARGE_RECOMMENDATION_CREATED: (chargeRecommendationNumber: string) => `Charge Recommendation ${chargeRecommendationNumber} created`,
  VIOLATION_TICKET_CREATED: (violationTicketNumber: string) => `Violation Ticket ${violationTicketNumber} created`,
  RESTORATIVE_JUSTICE_CREATED: (restorativeJusticeNumber: string) => `Restorative Justice ${restorativeJusticeNumber} created`,
  ORDER_ISSUED: "Order issued",
  WARNING_LETTER_ISSUED: "Warning letter issued",
} as const;
