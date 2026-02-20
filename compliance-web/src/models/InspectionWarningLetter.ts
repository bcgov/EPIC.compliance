import { InspectionRequirementSource } from "./InspectionRequirementSource";
import { StaffUser } from "./Staff";
import { WarningLetterApproval } from "./WarningLetterApproval";

export interface WarningLetterStatus {
  id: string;
  name: string;
}

export interface WarningLetterProgress {
  id: string;
  name: string;
}

export interface InspectionWarningLetter {
  issuing_officer?: StaffUser;
  id?: number;
  content?: string;
  warning_letter_number?: string;
  date_issued?: string;
  intended_issuance_date?: string;
  inspection_id?: number;
  issuing_officer_id?: number;
  warning_letter_requirement_maps?: WarningLetterRequirementMap[];
  is_active?: boolean;
  progress?: WarningLetterProgress;
  status?: WarningLetterStatus;
  warning_letter_approvals?: WarningLetterApproval[];
}

interface WarningLetterRequirementMap {
  id: number;
  inspection_requirement_id: number;
  inspection_requirement: {
    id: number;
    summary: string;
    requirement_source_details: InspectionRequirementSource[];
  };
}

export interface InspectionWarningLetterAPIData {
  inspection_id: number;
  issuing_officer_id?: number;
  intended_issuance_date?: string;
  content?: string;
  inspection_requirement_ids: number[];
  warning_letter_number?: string;
}
