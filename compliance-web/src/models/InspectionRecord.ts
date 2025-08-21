import { Inspection } from "./Inspection";
import { IRProgress } from "./IRProgress";
import { IRStatus } from "./IRStatus";
import { StaffUser } from "./Staff";
import { Position } from "./Position";

export interface InspectionRecord {
  id?: number;
  inspection_id?: number;
  inspection?: Inspection;
  action_required_by_rp?: string;
  date_issued?: string;
  enforcement_summary?: string;
  finding_statement?: string;
  inspection_scope?: string;
  intended_issuance_date?: string;
  ir_progress?: IRProgress;
  ir_status_id?: number;
  ir_status?: IRStatus;
  is_active?: boolean;
  mailing_address?: string;
  preliminary_review_details?: string;
  record_prepared_by_id?: number;
  record_prepared_by_position_id?: number;
  record_prepared_by?: StaffUser;
  record_prepared_by_position?: Position;
  field_change_info?: {
    inspection_scope_changed?: boolean;
    finding_statement_changed?: boolean;
    preliminary_review_details_changed?: boolean;
  };
}
