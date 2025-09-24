import {
  ReviewBoardItem,
  IRReviewBoardItem,
  OrderReviewBoardItem,
  WarningLetterReviewBoardItem,
  APReviewBoardItem,
  ReviewBoardSection,
} from "@/models/ReviewBoard";
import {
  AdministrativePenaltyStatus,
  APPROVAL_STATUS,
  IRProgressEnum,
} from "@/utils/constants";

export enum ReviewBoardCardType {
  DRAFTING = 1,
  DEPUTY_REVIEW = 2,
  REVIEW_STATUS = 3,
  HOLDER_REVIEW = 4,
  FINALIZING_RECORD = 5,
  PENDING_ISSUANCE = 6,
}

export const formatInspectionRecordsToReviewBoardItems = (
  inspectionRecords: IRReviewBoardItem[]
): ReviewBoardItem[] => {
  return inspectionRecords.map((record, index) => ({
    id: index + 1000, // Use unique IDs to avoid conflicts
    number: record.ir_number,
    project_name: record.project_title,
    card_date: record.inspection_start_date,
    types: [], // IR records don't have types in the current structure
    primary_officer: record.primary_officer,
    card_type: {
      name: "IR",
      sub_type: record.ir_status?.name,
    },
    approval_status: record.approval_status,
    approved_by: undefined, // Not available in IRReviewBoardItem
    review_date: record.send_for_review_date,
    ir_progress: record.ir_progress,
    ir_number: record.ir_number,
    intended_issuance_date: record.intended_issuance_date,
  }));
};

export const formatOrderRecordsToReviewBoardItems = (
  orderRecords: OrderReviewBoardItem[]
): ReviewBoardItem[] => {
  return orderRecords.map((record, index) => ({
    id: index + 2000, // Use unique IDs to avoid conflicts
    number: record.order_number,
    project_name: record.project_title,
    card_date: record.inspection_start_date,
    types: [], // Order records don't have types in the current structure
    primary_officer: record.primary_officer,
    card_type: {
      name: "Order",
    },
    approval_status: record.approval_status,
    approved_by: undefined, // Not available in OrderReviewBoardItem
    review_date: record.send_for_review_date,
    ir_number: record.ir_number,
    intended_issuance_date: record.intended_issuance_date,
  }));
};

export const formatWarningLettersToReviewBoardItems = (
  warningLetters: WarningLetterReviewBoardItem[]
): ReviewBoardItem[] => {
  return warningLetters.map((record, index) => ({
    id: index + 3000, // Use unique IDs to avoid conflicts
    number: record.warning_letter_number,
    project_name: record.project_title,
    card_date: record.inspection_start_date,
    types: [], // Warning letter records don't have types in the current structure
    primary_officer: record.primary_officer,
    card_type: {
      name: "Warning Letter",
    },
    approval_status: record.approval_status,
    approved_by: record.approved_by,
    review_date: record.review_requested_date,
    ir_number: record.ir_number,
    intended_issuance_date: record.intended_issuance_date,
  }));
};

export const formatAdministrativePenaltiesToReviewBoardItems = (
  administrativePenalties: APReviewBoardItem[]
): ReviewBoardItem[] => {
  return administrativePenalties.map((record, index) => ({
    id: index + 4000, // Use unique IDs to avoid conflicts
    number: record.administrative_penalty_number,
    project_name: record.project_title,
    card_date: record.inspection_start_date,
    types: [],
    primary_officer: record.primary_officer,
    card_type: {
      name: "AP",
    },
    approval_status: record.referral_status,
    approved_by: undefined,
    review_date: record.date_referred,
    ir_number: record.ir_number,
  }));
};

export const createInitialSections = (): ReviewBoardSection[] => {
  return [
    { id: ReviewBoardCardType.DRAFTING, sectionTitle: "Drafting", items: [] },
    {
      id: ReviewBoardCardType.DEPUTY_REVIEW,
      sectionTitle: "Deputy Review",
      items: [],
    },
    {
      id: ReviewBoardCardType.REVIEW_STATUS,
      sectionTitle: "Review Status",
      items: [],
    },
    {
      id: ReviewBoardCardType.HOLDER_REVIEW,
      sectionTitle: "Holder Review",
      items: [],
    },
    {
      id: ReviewBoardCardType.FINALIZING_RECORD,
      sectionTitle: "Finalizing Record",
      items: [],
    },
    {
      id: ReviewBoardCardType.PENDING_ISSUANCE,
      sectionTitle: "Pending Issuance",
      items: [],
    },
  ];
};

export const determineItemSection = (
  item: ReviewBoardItem
): ReviewBoardCardType => {
  let sectionIndex = ReviewBoardCardType.DRAFTING;

  if (item.card_type.name === "AP") {
    switch (item.approval_status?.id) {
      case AdministrativePenaltyStatus.DRAFTING:
        sectionIndex = ReviewBoardCardType.DRAFTING;
        break;
      case AdministrativePenaltyStatus.DEPUTY_REVIEW:
        sectionIndex = ReviewBoardCardType.DEPUTY_REVIEW;
        break;
      case AdministrativePenaltyStatus.CEB_NOT_PROCEEDING:
        sectionIndex = ReviewBoardCardType.REVIEW_STATUS;
        break;
      case AdministrativePenaltyStatus.REFERRED_TO_DM:
        sectionIndex = ReviewBoardCardType.PENDING_ISSUANCE;
        break;
    }
  } else if (
    item.card_type.name !== "AP" &&
    item.approval_status?.id === APPROVAL_STATUS.APPROVED &&
    item.intended_issuance_date
  ) {
    // If the issuance date is set, move it to pending issuance section
    sectionIndex = ReviewBoardCardType.PENDING_ISSUANCE;
  } else if (
    item.card_type.name === "IR" &&
    item.ir_progress?.id === IRProgressEnum.HOLDER_PRELIMINARY_REVIEW
  ) {
    // If the IR is in holder preliminary review, move it to holder review section
    sectionIndex = ReviewBoardCardType.HOLDER_REVIEW;
  } else if (
    item.card_type.name === "IR" &&
    item.ir_progress?.id === IRProgressEnum.FINAL_APPROVED
  ) {
    // If the IR is final approved, move it to review status section
    sectionIndex = ReviewBoardCardType.REVIEW_STATUS;
  } else if (
    item.card_type.name === "IR" &&
    item.ir_progress?.id === IRProgressEnum.FINALIZING_RECORD
  ) {
    // If the IR is in final record, move it to finalizing record section
    sectionIndex = ReviewBoardCardType.FINALIZING_RECORD;
    if (item.approval_status == null) {
      sectionIndex = ReviewBoardCardType.DRAFTING;
    } else if (item.approval_status?.id === APPROVAL_STATUS.NOT_APPROVED) {
      sectionIndex = ReviewBoardCardType.REVIEW_STATUS;
    }
  } else if (item.approval_status) {
    // Determine section based on approval status and card type
    switch (item.approval_status.id) {
      case APPROVAL_STATUS.APPROVED:
      case APPROVAL_STATUS.NOT_APPROVED:
        sectionIndex = ReviewBoardCardType.REVIEW_STATUS;
        break;
      case APPROVAL_STATUS.APPROVAL_PENDING:
        sectionIndex = ReviewBoardCardType.DEPUTY_REVIEW;
        break;
      default:
        sectionIndex = ReviewBoardCardType.DRAFTING;
    }
  } else {
    sectionIndex = ReviewBoardCardType.DRAFTING;
  }

  return sectionIndex;
};

export const generateDynamicSections = (
  inspectionRecords?: IRReviewBoardItem[],
  orderRecords?: OrderReviewBoardItem[],
  warningLetters?: WarningLetterReviewBoardItem[],
  administrativePenalties?: APReviewBoardItem[],
  primaryOfficerFilter?: string[]
): ReviewBoardSection[] => {
  // Initialize the 6 sections with empty items
  const sections = createInitialSections();

  // Collect all formatted items from different data sources
  const allItems = [
    ...(inspectionRecords
      ? formatInspectionRecordsToReviewBoardItems(inspectionRecords)
      : []),
    ...(orderRecords ? formatOrderRecordsToReviewBoardItems(orderRecords) : []),
    ...(warningLetters
      ? formatWarningLettersToReviewBoardItems(warningLetters)
      : []),
    ...(administrativePenalties
      ? formatAdministrativePenaltiesToReviewBoardItems(administrativePenalties)
      : []),
  ];

  // Apply primary officer filtering if filter is provided
  const filteredItems =
    primaryOfficerFilter && primaryOfficerFilter.length > 0
      ? allItems.filter(
          (item) =>
            item.primary_officer &&
            primaryOfficerFilter.includes(item.primary_officer.id.toString())
        )
      : allItems;

  // Distribute items across sections based on their status/progress and approval status
  filteredItems.forEach((item) => {
    const sectionIndex = determineItemSection(item);
    sections[sectionIndex - 1].items.push(item);
  });

  return sections;
};
