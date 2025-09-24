import { ApprovalStatus } from "./ApprovalStatus";
import { OrderProgress, OrderStatus } from "./InspectionOrder";
import { WarningLetterProgress, WarningLetterStatus } from "./InspectionWarningLetter";
import { IRProgress } from "./IRProgress";
import { IRStatus } from "./IRStatus";
import { IRType } from "./IRType";
import { StaffUser } from "./Staff";
import { Option } from "./common";

export interface ReviewBoardCardType {
  name: string;
  sub_type?: string;
}

export interface ReviewBoardItem {
  id: number;
  number: string;
  project_name: string;
  card_date: string;
  types: IRType[];
  primary_officer: StaffUser;
  card_type: ReviewBoardCardType;
  approval_status?: ApprovalStatus;
  approved_by?: StaffUser;
  review_date?: string;
  ir_progress?: IRProgress;
  ir_number?: string;
  intended_issuance_date?: string;
  deputy_director_name?: string;
  send_for_review_date?: string;
  date_report_sent?: string;
  expected_return_date?: string;
  date_response?: string;
}

export interface ReviewBoardSection {
  id: number;
  sectionTitle: string;
  items: ReviewBoardItem[];
}

export interface IRReviewBoardItem {
  ir_number: string,
  project_title: string,
  inspection_start_date: string,
  primary_officer: StaffUser,
  send_for_review_date: string,
  deputy_director_name: string,
  approved_date: string,
  date_report_sent: string,
  expected_return_date: string,
  date_response: string,
  intended_issuance_date: string,
  ir_status: IRStatus,
  ir_progress: IRProgress,
  approval_status: ApprovalStatus,
}

export interface OrderReviewBoardItem {
  ir_number: string,
  order_number: string,
  project_title: string,
  inspection_start_date: string,
  primary_officer: StaffUser,
  issuing_officer: StaffUser,
  send_for_review_date: string,
  deputy_director_name: string,
  approved_date: string,
  order_status: OrderStatus,
  order_progress: OrderProgress,
  approval_status: ApprovalStatus,
  intended_issuance_date: string,
}

export interface WarningLetterReviewBoardItem {
  ir_number: string,
  warning_letter_number: string,
  project_title: string,
  inspection_start_date: string,
  primary_officer: StaffUser,
  issuing_officer: StaffUser,
  approved_date: string,
  deputy_director_name: string,
  review_requested_date: string,
  approved_by: StaffUser,
  intended_issuance_date: string,
  warning_letter_status: WarningLetterStatus,
  warning_letter_progress: WarningLetterProgress,
  approval_status: ApprovalStatus,
}

export interface APReviewBoardItem {
  ir_number: string,
  administrative_penalty_number: string,
  project_title: string,
  inspection_start_date: string,
  primary_officer: StaffUser,
  referral_status: Option,
  date_referred: string,
  decision_date: string,
  decision: Option,
  penalty_amount: number,
}
