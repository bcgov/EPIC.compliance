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
}


interface AdministrativePenaltyRequirementMap {
  id: number;
  inspection_requirement_id: number;
  inspection_requirement: {
    id: number;
    summary: string;
  };
}

export interface AdministrativePenaltyAPIData {
  inspection_id: number;
  referral_status: string;
  date_referred?: string;
  decision_date?: string;
  decision?: string;
  penalty_amount?: number;
  inspection_requirement_ids: number[];
  administrative_penalty_number?: string;
}
