import { ComplianceFinding } from "./ComplianceFinding";
import { EnforcementAction } from "./EnforcementAction";
import { ApprovalStatus } from "./ApprovalStatus";
import { RequirementSource } from "./RequirementSource";
import { Topic } from "./Topic";
import { StaffUser } from "./Staff";
import { BaseTableQueryParams } from "./BaseTableQueryParams";

export interface InspectionRequirementGrid {
  id: number;
  topic: Topic;
  summary: string;
  compliance_finding: ComplianceFinding;
  enforcement_action: EnforcementAction;
  approval_status: ApprovalStatus;
  sort_order: number;
  date_issued: string;
  ir_number: string;
  requirement_number: string;
  requirement_source: RequirementSource;
  approved_by: StaffUser;
  approved_by_id: number;
}

export interface InspectionRequirementGridQueryParams extends BaseTableQueryParams {
  tpc_ids?: string;
  summary?: string;
  cmd_fnd_ids?: string;
  enf_actn_ids?: string;
  apprv_sts?: string;
  approver_ids?: string;
  req_src_ids?: string;
  req_src_num?: string;
  ir_no?: string;
  date_issued?: string;
  prm_offc_ids?: string;
  insp_sts?: string;
  project_ids?: string;
}

export interface InspectionRequirementGridItems {
  items: InspectionRequirementGrid[];
  total: number;
}
