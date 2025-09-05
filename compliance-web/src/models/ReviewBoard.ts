import { ApprovalStatus } from "./ApprovalStatus";
import { IRType } from "./IRType";
import { StaffUser } from "./Staff";

export interface ReviewBoardCardType {
  name: string;
  sub_type?: string;
}

export interface ReviewBoardItem {
  id: number;
  number: string;
  name: string;
  card_date: string;
  types: IRType[];
  primary_officer: StaffUser;
  card_type: ReviewBoardCardType;
  approval_status?: ApprovalStatus;
  approved_by?: StaffUser;
  review_date?: string;
}

export interface ReviewBoardSection {
  id: number;
  section: string;
  items: ReviewBoardItem[];
}


