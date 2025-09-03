import { Dayjs } from "dayjs";
import { Attendance, InspectionAttendance } from "./Attendance";
import { CaseFile } from "./CaseFile";
import { Initiation } from "./Initiation";
import { IRStatus } from "./IRStatus";
import { IRType } from "./IRType";
import { Project } from "./Project";
import { ProjectStatus } from "./ProjectStatus";
import { StaffUser } from "./Staff";
import { ApprovalStatus } from "./ApprovalStatus";
import { IRProgress } from "./IRProgress";
import { BaseTableQueryParams } from "./BaseTableQueryParams";
import { Agency } from "./Agency";
import { FirstNation } from "./FirstNation";

export interface Inspection {
  id: number;
  ir_number: string;
  case_file_id: number;
  project_id: number;
  location_description: string;
  utm: string;
  initiation_id: number;
  ir_status_id: number;
  project_status_id: number;
  primary_officer_id: number;
  start_date: string;
  end_date: string;
  debrief_date: string;
  types: IRType[];
  types_text: string; // TODO: Remove this once the table filter is updated
  inspection_status: string;
  is_active: boolean;
  initiation: Initiation;
  project: Project;
  primary_officer: StaffUser;
  ir_status: IRStatus;
  case_file: CaseFile;
  officers?: StaffUser[];
  project_status: ProjectStatus;
  authorization?: string;
  regulated_party?: string;
  type?: string;
  sub_type?: string;
  project_description?: string;
  inspectionAttendances?: InspectionAttendance[];
  subtopic?: string;
  source?: string;
  enforcement?: string;
  approval_status?: ApprovalStatus;
  approved_by_id?: number;
  approved_by?: StaffUser;
  ir_progress?: IRProgress;
  is_history?: boolean;
}

export interface InspectionGridQueryParams extends BaseTableQueryParams {
  case_file_id?: string;
  ir_number?: string;
  project_ids?: string;
  start_date?: string;
  initiation_ids?: string;
  ir_progresses?: string;
  approval_statuses?: string;
  primary_officer_ids?: string;
  statuses?: string;
  case_file_number?: string;
  approved_by_ids?: string;
}

export interface InspectionGridItems {
  items: Inspection[];
  total: number;
}

export interface InspectionGridQueryParams extends BaseTableQueryParams {
  case_file_id?: string;
  ir_number?: string;
  project_ids?: string;
  start_date?: string;
  initiation_ids?: string;
  ir_progresses?: string;
  approval_statuses?: string;
  primary_officer_ids?: string;
  statuses?: string;
  case_file_number?: string;
  approved_by_ids?: string;
}

export interface InspectionGridItems {
  items: Inspection[];
  total: number;
}

export interface InspectionMoreDetails extends Inspection {
  requirement_details?: {
    requirement_id: number;
    requirement_summary: string;
    requirement_sort_order: number;
    enforcement_action?: InspectionMoreDetailsEnforcementAction;
    requirement_number: string;
    requirement_source_name: string;
  }[];
}

export interface InspectionMoreDetailsEnforcementAction {
  id: string;
  name: string;
  number?: string;
  approval_status?: ApprovalStatus;
  progress?: {
    id: string;
    name: string;
  } | null;
}

export interface InspectionFormData {
  project?: Project;
  startDate?: Dayjs;
  endDate?: Dayjs;
  debriefDate?: Dayjs;
  primaryOfficer?: StaffUser;
  initiation?: Initiation;
  irTypes?: IRType[];
  irStatus?: IRStatus;
  projectStatus?: ProjectStatus;
  caseFileId?: string;
  isHistory?: boolean;
  isIndependentEnvMonitor?: boolean;
  isCHRepresentatives?: boolean;
  officers?: StaffUser[];
  inAttendance?: Attendance[];
  agencies?: Agency[];
  firstNations?: FirstNation[];
  municipal?: string;
  other?: string;
  projectDescription?: string;
  locationDescription?: string;
  utm?: string;
}

export interface InspectionAPIData {
  project_id?: number;
  location_description?: string;
  utm?: string;
  primary_officer_id: number;
  case_file_id?: number;
  inspection_type_ids: string[];
  start_date: string;
  end_date?: string;
  debrief_date?: string;
  initiation_id: string;
  ir_status_id?: string;
  project_status_id?: string;
  attendance_option_ids?: string[];
  agency_attendance_ids?: number[];
  attendance_municipal?: string;
  attendance_other?: string;
  firstnation_attendance_ids?: number[];
  attending_officer_ids?: number[];
  project_description?: string;
  unapproved_project_authorization?: string;
  unapproved_project_regulated_party?: string;
  unapproved_project_type?: string;
  unapproved_project_sub_type?: string;
  is_history?: boolean;
}

export interface InspectionStatusAPIData {
  status: string;
}
