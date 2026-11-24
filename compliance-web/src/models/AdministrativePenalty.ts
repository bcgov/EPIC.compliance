import { Inspection } from './Inspection';
import { InspectionRequirement } from './InspectionRequirement';
import { InspectionRequirementSource } from './InspectionRequirementSource';
import { Option } from './common';

export interface AdministrativePenalty {
  administrative_penalty_requirement_maps: AdministrativePenaltyRequirementMap[];
  id: number;
  inspection_id: number;
  administrative_penalty_number: string;
  date_referred: string;
  decision_date: string;
  is_active: boolean;
  referral_status: Option;
  decision?: Option;
  penalty_amount?: string;
  jr_decision_date?: string;
  jr_decision?: Option;
  jr_new_penalty_amount?: string;
  is_closed: boolean;
  is_jr_complete?: boolean;
  jr_ap_fields_edited?: boolean;
}


interface AdministrativePenaltyRequirementMap {
  id: number;
  inspection_requirement_id: number;
  inspection_requirement: {
    id: number;
    summary: string;
    inspection_id: number;
    requirement_source_details: InspectionRequirementSource[];
  };
}

export interface AdministrativePenaltyAPIData {
  inspection_id: number;
  referral_status: string;
  date_referred?: string;
  decision_date?: string;
  decision?: string;
  penalty_amount?: number;
  jr_decision_date?: string;
  jr_decision?: string;
  jr_new_penalty_amount?: number;
  jr_ap_fields_edited?: boolean;
  inspection_requirement_ids: number[];
  administrative_penalty_number?: string;
}

export interface AdministrativePenaltyLink {
  inspection: Inspection;
  requirements: InspectionRequirement[];
}

