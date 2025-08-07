// App Constants should go here

export const APP_SIDE_NAV_WIDTH = 260;
export const APP_SIDE_NAV_WIDTH_COLLAPSED = 68;

export const DATE_FORMAT = "YYYY-MM-DD";
export const DATE_TIME_FORMAT = "YYYY-MM-DD HH:mm";

export const UNAPPROVED_PROJECT_ID = 99999;
export const UNAPPROVED_PROJECT_ABBREVIATION = "UNPRVD";

export const STAFF_USER_POSITION = {
  DEPUTY_DIRECTOR: 3,
  DIRECTOR: 4,
}

export const INITIATION = {
  INSPECTION_ID: "1",
  COMPLAINTS_ID: "2",
  OTHER_ID: "3",
};

export const IR_STATUS = {
  PRELIMINARY: 1,
  FINAL: 2,
};

export const CORS_ERROR_MSG = "Network error or CORS issue";

export const REGEX_EMAIL = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
export const REGEX_PHONE_NUMBER = /^\(\d{3}\) \d{3}-\d{4}$/;

export enum RequirementSourceEnum {
  SCHEDULE_B = "1",
  ORDER = "2",
  EAC = "3",
  CPD = "4",
  ACT2018 = "5",
  COMPLAINCE_AGREEMENT = "6",
  ACT2022 = "7",
  OTHER = "8",
  EACA = "10",
  REGULATION = "11",
  EXEMPTION_ORDER = "12",
}

export enum RequirementDocumentTypeEnum {
  MANAGEMENT_PLAN = "1",
  OTHER_DOCUMENT = "2",
}

export const CR_CONTEXT_TYPE = {
  INSPECTION: "Inspection",
  COMPLAINT: "Complaint",
  CASEFILE: "Casefile",
}

export const CR_CONTEXT_LINK: Record<string, string> = {
  "Inspection": "/ce-database/inspections",
  "Complaint": "/ce-database/complaints",
  "Casefile": "/ce-database/case-files",
}

export const FILE_PROFILE_CONTEXT = CR_CONTEXT_TYPE;

export const DEFAULT_REPORT_TAB_CONTENT = `<p class="editor-paragraph">None at this time.</p>`;

export const DRAWER_WIDTHS = {
  INSPECTION_DRAWER: "1118px",
  COMPLAINT_DRAWER: "1118px",
  CASEFILE_DRAWER: "718px",
  REQUIREMENT_DRAWER: "1228px",
  ENFORCEMENT_DRAWER: "1228px",
};

export enum APPROVAL_STATUS {
  APPROVAL_PENDING = "APPROVAL_PENDING",
  APPROVED = "APPROVED",
  NOT_APPROVED = "NOT_APPROVED",
}

export enum APPROVAL_STATUS_TEXT {
  APPROVAL_PENDING = "Approval Pending",
  APPROVED = "Approved",
  NOT_APPROVED = "Not Approved",
}

export enum IRProgressEnum {
  PRELIMINARY_DRAFTING = "PRELIMINARY_DRAFTING",
  PRELIMINARY_DEPUTY_REVIEW = "PRELIMINARY_DEPUTY_REVIEW",
  PRELIMINARY_APPROVED = "PRELIMINARY_APPROVED",
  HOLDER_PRELIMINARY_REVIEW = "HOLDER_PRELIMINARY_REVIEW",
  FINALIZING_RECORD = "FINALIZING_RECORD",
  FINAL_DEPUTY_REVIEW = "FINAL_DEPUTY_REVIEW",
  FINAL_APPROVED = "FINAL_APPROVED",
  ISSUED = "ISSUED",
}

export enum IRProgressEnumText {
  PRELIMINARY_DRAFTING = "Preliminary Drafting",
  PRELIMINARY_DEPUTY_REVIEW = "Preliminary Deputy Review",
  PRELIMINARY_APPROVED = "Preliminary Approved",
  HOLDER_PRELIMINARY_REVIEW = "Holder Preliminary Review",
  FINALIZING_RECORD = "Finalizing Record",
  FINAL_DEPUTY_REVIEW = "Final Deputy Review",
  FINAL_APPROVED = "Final Approved",
  ISSUED = "Issued",
}

export enum InspectionStatusEnum {
  OPEN = "Open",
  CLOSED = "Closed",
  CANCELED = "Canceled",
}

export enum OrderStatusEnum {
  CREATED = "CREATED",
  OPEN = "OPEN",
  CLOSED = "CLOSED",
  RESCINDED = "RESCINDED",
}

export enum OrderProgressEnum {
  DRAFTING = "DRAFTING",
  DEPUTY_REVIEW = "DEPUTY_REVIEW",
  APPROVED = "APPROVED",
  ISSUED = "ISSUED",
}

export enum WarningLetterStatusEnum {
  CREATED = "CREATED",
  ISSUED = "ISSUED",
}

export enum WarningLetterProgressEnum {
  DRAFTING = "DRAFTING",
  DEPUTY_REVIEW = "DEPUTY_REVIEW",
  APPROVED = "APPROVED",
  ISSUED = "ISSUED",
}

export enum AttendanceEnum {
  AGENCIES = "1",
  FIRST_NATIONS = "2",
  MUNICIPAL = "3",
  INDIVIDUAL_ENV_MONITOR = "4",
  CH_RP_REPRESENTATIVE = "5",
  OTHER = "7",
  OFFICERS = "8",
}

export enum EnforcementActionEnum {
  NOT_APPLICABLE = "2",
  WARNING_LETTER = "4",
  ORDER = "5",
  AP_RECOMMENDATION = "6",
  REFER_TO_ANOTHER_AGENCY = "7",
  VIOLATION_TICKET = "8",
  CHARGE_RECOMMENDATION = "9",
  ADVISORY = "10",
  WARNING = "11",
}

export type VARIANT_COLORS = "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning";
