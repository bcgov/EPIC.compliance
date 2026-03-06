import { Dayjs } from "dayjs";
import { StaffUser } from "./Staff";

export interface ContinuationReport {
  id: number;
  case_file_id: number;
  text: string;
  rich_text: string;
  created_by_user?: StaffUser;
  context_type: string;
  context_id: number;
  system_generated: boolean;
  date_created: string;
  is_active: boolean;
  keys: CRKeys[];
}

export interface CRKeys {
  key_context: string;
  id: number;
  key: string;
  is_active: boolean;
}

export interface ContinuationReportPaginated {
  items: ContinuationReport[];
  total: number
}

export interface ContinuationReportFormData {
  dateOfEntry?: Dayjs;
  entry?: {
    html: string;
    text: string;
  };
}

export interface ContinuationReportAPIData {
  case_file_id?: number;
  text: string;
  rich_text: string;
  date_created: string;
  context_type?: string;
  context_id?: number;
}

export interface ContinuationReportExportAPIData {
  case_file_number: string;
}
