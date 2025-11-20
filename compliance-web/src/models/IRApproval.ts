import { ApprovalStatus } from "./ApprovalStatus";
import { Position } from "./Position";
import { StaffUser } from "./Staff";

export interface IRApproval {
  approved_by: StaffUser;
  approval_status: ApprovalStatus;
  approved_by_position: Position;
  id: number;
  inspection_record_id: number;
  date_report_sent: string;
  date_expected_return: string;
  date_response: string;
  approved_by_id: number;
  ir_status_id: number;
  is_active: boolean;
}

export interface InspectionRecordApprovalPayload {
  field_name: string;
  value: string | null;
}
