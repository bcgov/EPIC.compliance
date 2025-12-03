import { Project } from "./Project";
import { RequirementDetails, RequirementSource } from "./RequirementSource";
import { ComplaintSource } from "./ComplaintSource";
import { StaffUser } from "./Staff";
import { CaseFile } from "./CaseFile";
import { Contact } from "./Contact";
import { Dayjs } from "dayjs";
import { Agency } from "./Agency";
import { FirstNation } from "./FirstNation";
import { Topic } from "./Topic";
import { InspectionOrder } from "./InspectionOrder";
import { BaseTableQueryParams } from "./BaseTableQueryParams";
import { ComplaintResolution } from "./ComplaintResolution";

export interface Complaint {
  id: number;
  complaint_number: string;
  case_file_id: number;
  project_id: number;
  project_description: string;
  concern_description: string;
  location_description: string;
  primary_officer_id: number;
  date_received: string;
  topic_id?: number;
  requirement_source_id: number;
  requirement_source_description?: string;
  source_type_id: number;
  source_agency_id: number;
  source_first_nation_id: number;
  is_active: boolean;
  case_file: CaseFile;
  primary_officer: StaffUser;
  project: Project;
  topic: Topic;
  source_type: ComplaintSource;
  requirement_source: RequirementSource;
  source_contact: Contact;
  requirement_detail: RequirementDetails;
  status: string;
  authorization?: string;
  regulated_party?: string;
  type?: string;
  sub_type?: string;
  agency?: Agency;
  first_nation?: FirstNation;
  resolution?: ComplaintResolution;
  resolution_agency?: Agency;
}

export interface ComplaintGridQueryParams extends BaseTableQueryParams {
  complaint_number?: string;
  project_ids?: string;
  topic_ids?: string;
  date_received?: string;
  source_type_ids?: string;
  primary_officer_ids?: string;
  statuses?: string;
  case_file_number?: string;
  case_file_id?: string;  
  resolution_ids?: string;
}

export interface ComplaintGridItems {
  items: Complaint[];
  total: number;
}

export interface ComplaintFormData {
  concernDescription?: string;
  locationDescription?: string;
  topic?: Topic;
  primaryOfficer?: StaffUser;
  dateReceived?: Dayjs;
  complaintSource?: ComplaintSource;
  contactFullName?: string;
  contactTitle?: string;
  contactEmail?: string;
  contactPhoneNumber?: string;
  contactComments?: string;
  agency?: Agency;
  firstNation?: FirstNation;
  otherDescription?: string;
  allianceName?: string;
  requirementSource?: RequirementSource;
  requirementSourceDescription?: string;
  order?: InspectionOrder;
}

export interface ComplaintAPIData {
  project_id?: number;
  concern_description: string;
  location_description?: string;
  primary_officer_id?: number;
  topic_id?: number;
  case_file_id?: number;
  date_received: string;
  source_type_id: string;
  complaint_source_contact?: Contact;
  source_agency_id?: number;
  source_first_nation_id?: number;
  requirement_source_id?: string;
  requirement_source_description?: string;
  requirement_source_details?: {
    order_number?: string;
  };
  project_description?: string;
  unapproved_project_authorization?: string;
  unapproved_project_regulated_party?: string;
  unapproved_project_type?: string;
  unapproved_project_sub_type?: string;
}

export interface ComplaintStatusAPIData {
  status: string;
  resolution_id?: string;
  resolution_agency_id?: string;
}
