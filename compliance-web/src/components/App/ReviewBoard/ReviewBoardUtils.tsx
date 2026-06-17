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

export enum ReviewBoardCardTypeEnum {
  DRAFTING = 1,
  DEPUTY_REVIEW = 2,
  REVIEW_STATUS = 3,
  HOLDER_REVIEW = 4,
  FINALIZING_RECORD = 5,
  PENDING_ISSUANCE = 6,
}

const formatInspectionRecordsToReviewBoardItems = (
  inspectionRecords: IRReviewBoardItem[]
): ReviewBoardItem[] => {
  return inspectionRecords.map((record, index) => ({
    id: index + 1000, // Use unique IDs to avoid conflicts
    number: record.ir_number,
    project_name: record.project_title,
    card_date: record.inspection_start_date,
    inspection_types: record.inspection_types,
    primary_officer: record.primary_officer,
    card_type: {
      name: "IR",
      sub_type: record.ir_status?.name,
    },
    approval_status: record.approval_status,
    approved_by: undefined, // Not available in IRReviewBoardItem
    review_date: record.approved_date,
    ir_progress: record.ir_progress,
    ir_number: record.ir_number,
    intended_issuance_date: record.intended_issuance_date,
    deputy_director: record.deputy_director,
    send_for_review_date: record.send_for_review_date,
    date_report_sent: record.date_report_sent,
    expected_return_date: record.expected_return_date,
    date_response: record.date_response,
  }));
};

const formatOrderRecordsToReviewBoardItems = (
  orderRecords: OrderReviewBoardItem[]
): ReviewBoardItem[] => {
  return orderRecords.map((record, index) => ({
    id: index + 2000, // Use unique IDs to avoid conflicts
    number: record.order_number,
    project_name: record.project_title,
    card_date: record.inspection_start_date,
    inspection_types: record.inspection_types,
    primary_officer: record.primary_officer,
    card_type: {
      name: "Order",
    },
    approval_status: record.approval_status,
    approved_by: undefined, // Not available in OrderReviewBoardItem
    review_date: record.approved_date,
    ir_number: record.ir_number,
    intended_issuance_date: record.intended_issuance_date,
    deputy_director: record.deputy_director,
    send_for_review_date: record.send_for_review_date,
    issuing_officer: record.issuing_officer,
  }));
};

const formatWarningLettersToReviewBoardItems = (
  warningLetters: WarningLetterReviewBoardItem[]
): ReviewBoardItem[] => {
  return warningLetters.map((record, index) => ({
    id: index + 3000, // Use unique IDs to avoid conflicts
    number: record.warning_letter_number,
    project_name: record.project_title,
    card_date: record.inspection_start_date,
    inspection_types: record.inspection_types,
    primary_officer: record.primary_officer,
    card_type: {
      name: "Warning Letter",
    },
    approval_status: record.approval_status,
    approved_by: record.approved_by,
    review_date: record.approved_date,
    ir_number: record.ir_number,
    intended_issuance_date: record.intended_issuance_date,
    deputy_director: record.deputy_director,
    send_for_review_date: record.review_requested_date,
    issuing_officer: record.issuing_officer,
  }));
};

const formatAdministrativePenaltiesToReviewBoardItems = (
  administrativePenalties: APReviewBoardItem[]
): ReviewBoardItem[] => {
  return administrativePenalties.map((record, index) => ({
    id: index + 4000, // Use unique IDs to avoid conflicts
    number: record.administrative_penalty_number,
    project_name: record.project_title,
    card_date: record.inspection_start_date,
    inspection_types: record.inspection_types,
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

const createInitialSections = (): ReviewBoardSection[] => {
  return [
    {
      id: ReviewBoardCardTypeEnum.DRAFTING,
      sectionTitle: "Drafting",
      items: [],
    },
    {
      id: ReviewBoardCardTypeEnum.DEPUTY_REVIEW,
      sectionTitle: "Deputy Review",
      items: [],
    },
    {
      id: ReviewBoardCardTypeEnum.REVIEW_STATUS,
      sectionTitle: "Review Status",
      items: [],
    },
    {
      id: ReviewBoardCardTypeEnum.HOLDER_REVIEW,
      sectionTitle: "Holder Review",
      items: [],
    },
    {
      id: ReviewBoardCardTypeEnum.FINALIZING_RECORD,
      sectionTitle: "Finalizing Record",
      items: [],
    },
    {
      id: ReviewBoardCardTypeEnum.PENDING_ISSUANCE,
      sectionTitle: "Pending Issuance",
      items: [],
    },
  ];
};

const determineItemSection = (
  item: ReviewBoardItem
): ReviewBoardCardTypeEnum => {
  let sectionIndex = ReviewBoardCardTypeEnum.DRAFTING;

  if (item.card_type.name === "AP") {
    switch (item.approval_status?.id) {
      case AdministrativePenaltyStatus.DRAFTING:
      case AdministrativePenaltyStatus.REFERRED_TO_AMP_UNIT:
        sectionIndex = ReviewBoardCardTypeEnum.DRAFTING;
        break;
      case AdministrativePenaltyStatus.DEPUTY_REVIEW:
        sectionIndex = ReviewBoardCardTypeEnum.DEPUTY_REVIEW;
        break;
      case AdministrativePenaltyStatus.CEB_NOT_PROCEEDING:
        sectionIndex = ReviewBoardCardTypeEnum.REVIEW_STATUS;
        break;
      case AdministrativePenaltyStatus.REFERRED_TO_DM:
        sectionIndex = ReviewBoardCardTypeEnum.PENDING_ISSUANCE;
        break;
    }
  } else if (
    item.card_type.name !== "AP" &&
    item.approval_status?.id === APPROVAL_STATUS.APPROVED &&
    item.intended_issuance_date
  ) {
    // If the issuance date is set, move it to pending issuance section
    sectionIndex = ReviewBoardCardTypeEnum.PENDING_ISSUANCE;
  } else if (
    item.card_type.name === "IR" &&
    item.ir_progress?.id === IRProgressEnum.HOLDER_PRELIMINARY_REVIEW
  ) {
    // If the IR is in holder preliminary review, move it to holder review section
    sectionIndex = ReviewBoardCardTypeEnum.HOLDER_REVIEW;
  } else if (
    item.card_type.name === "IR" &&
    item.ir_progress?.id === IRProgressEnum.FINAL_APPROVED
  ) {
    // If the IR is final approved, move it to review status section
    sectionIndex = ReviewBoardCardTypeEnum.REVIEW_STATUS;
  } else if (
    item.card_type.name === "IR" &&
    item.ir_progress?.id === IRProgressEnum.FINALIZING_RECORD
  ) {
    // If the IR is in final record, move it to finalizing record section
    sectionIndex = ReviewBoardCardTypeEnum.FINALIZING_RECORD;
    if (item.approval_status == null) {
      sectionIndex = ReviewBoardCardTypeEnum.DRAFTING;
    } else if (item.approval_status?.id === APPROVAL_STATUS.NOT_APPROVED) {
      sectionIndex = ReviewBoardCardTypeEnum.REVIEW_STATUS;
    }
  } else if (item.approval_status) {
    // Determine section based on approval status and card type
    switch (item.approval_status.id) {
      case APPROVAL_STATUS.APPROVED:
      case APPROVAL_STATUS.NOT_APPROVED:
        sectionIndex = ReviewBoardCardTypeEnum.REVIEW_STATUS;
        break;
      case APPROVAL_STATUS.APPROVAL_PENDING:
        sectionIndex = ReviewBoardCardTypeEnum.DEPUTY_REVIEW;
        break;
      default:
        sectionIndex = ReviewBoardCardTypeEnum.DRAFTING;
    }
  } else {
    sectionIndex = ReviewBoardCardTypeEnum.DRAFTING;
  }

  return sectionIndex;
};

const sortUsingDate = (items: ReviewBoardItem[], field: string): void => {
  items.sort((a, b) => {
    const aValue = a[field as keyof ReviewBoardItem];
    const bValue = b[field as keyof ReviewBoardItem];
    if (!aValue && !bValue) return 0;
    if (!aValue) return 1;
    if (!bValue) return -1;
    return (
      new Date(aValue as string).getTime() -
      new Date(bValue as string).getTime()
    );
  });
};

const sortSections = (sections: ReviewBoardSection[]): void => {
  sections.forEach((section) => {
    switch (section.id) {
      case ReviewBoardCardTypeEnum.DRAFTING:
        sortUsingDate(section.items, "card_date");
        break;
      case ReviewBoardCardTypeEnum.DEPUTY_REVIEW:
        sortUsingDate(section.items, "send_for_review_date");
        break;
      case ReviewBoardCardTypeEnum.REVIEW_STATUS:
        sortUsingDate(section.items, "review_date");
        break;
      case ReviewBoardCardTypeEnum.HOLDER_REVIEW:
        sortUsingDate(section.items, "expected_return_date");
        break;
      case ReviewBoardCardTypeEnum.FINALIZING_RECORD:
        sortUsingDate(section.items, "date_response");
        break;
      case ReviewBoardCardTypeEnum.PENDING_ISSUANCE:
        sortUsingDate(section.items, "intended_issuance_date");
        break;
    }
  });
};

export const generateDynamicSections = (
  inspectionRecords?: IRReviewBoardItem[],
  orderRecords?: OrderReviewBoardItem[],
  warningLetters?: WarningLetterReviewBoardItem[],
  administrativePenalties?: APReviewBoardItem[],
  externalFilters?: Record<string, string[] | string>
): ReviewBoardSection[] => {
  // Extract primary officer filter from external filters
  const primaryOfficerFilter = externalFilters?.primary_officer_id as
    | string[]
    | undefined;
  const deputyDirectorFilter = externalFilters?.deputy_director_id as
    | string[]
    | undefined;

  // Initialize the 6 sections with empty items
  const sections = createInitialSections();

  // Collect all formatted items from different data sources
  let allItems = [
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
  if (primaryOfficerFilter && primaryOfficerFilter.length > 0) {
    allItems = allItems.filter(
      (item) =>
        item.primary_officer &&
        primaryOfficerFilter.includes(item.primary_officer.id.toString())
    );
  }
  if (deputyDirectorFilter && deputyDirectorFilter.length > 0) {
    allItems = allItems.filter(
      (item) =>
        (item.approval_status?.id === APPROVAL_STATUS.APPROVAL_PENDING ||
          item.approval_status?.id ===
            AdministrativePenaltyStatus.DEPUTY_REVIEW) &&
        item.deputy_director &&
        deputyDirectorFilter.includes(item.deputy_director.id.toString())
    );
  }

  // Distribute items across sections based on their status/progress and approval status
  allItems.forEach((item) => {
    const sectionIndex = determineItemSection(item);
    sections[sectionIndex - 1].items.push(item);
  });

  sortSections(sections);

  return sections;
};
