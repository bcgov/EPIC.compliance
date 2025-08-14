import { Dayjs } from "dayjs";
import { Initiation } from "./Initiation";
import { Project } from "./Project";
import { StaffUser } from "./Staff";
import { BaseTableQueryParams } from "./BaseTableQueryParams";

export interface CaseFile {
  id: number;
  project_id: number;
  date_created: string;
  primary_officer_id: number;
  case_file_number: string;
  case_file_status: string;
  initiation: Initiation;
  is_active: boolean;
  project: Project;
  primary_officer: StaffUser;
  officers?: StaffUser[];
  authorization?: string;
  regulated_party?: string;
  type?: string;
  sub_type?: string;
  project_description?: string;
  caseFileLinks?: CaseFile[];
}

export interface CaseFileGridQueryParams extends BaseTableQueryParams {
  case_file_number?: string;
  project_ids?: string;
  initiation_ids?: string;
  statuses?: string;
  primary_officer_ids?: string;
  date_created?: string;
}

export interface CaseFileGridItems {
  items: CaseFile[];
  total: number;
}

export interface CaseFileFormData {
  project?: Project;
  authorization?: string;
  regulatedParty?: string;
  projectDescription?: string;
  projectType?: string;
  projectSubType?: string;
  dateCreated?: Dayjs;
  primaryOfficer?: StaffUser;
  officers?: StaffUser[];
  initiation?: Initiation;
  caseFileNumber?: string;
}

export interface CaseFileAPIData {
  project_id?: number;
  initiation_id: string;
  primary_officer_id: number;
  officer_ids?: number[];
  date_created?: string;
  case_file_number?: string;
  project_description?: string;
  unapproved_project_authorization?: string;
  unapproved_project_regulated_party?: string;
  unapproved_project_type?: string;
  unapproved_project_sub_type?: string;
}

export interface CaseFileStatusAPIData {
  status: string;
}

export interface CaseFileOption {
  id: number;
  name: string;
}

