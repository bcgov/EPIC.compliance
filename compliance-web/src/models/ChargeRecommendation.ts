import { InspectionRequirementSource } from "./InspectionRequirementSource";
import { Option } from "./common";

export interface ChargeRecommendation {
  charge_recommendation_requirement_maps: ChargeRecommendationRequirementMap[];
  sentence_type_mappings: SentenceTypeMapping[];
  id: number;
  inspection_id: number;
  charge_recommendation_number: string;
  status: Option;
  date_to_crown_counsel?: string;
  charge_decision?: Option;
  charge_decision_date?: string;
  court_file_number?: string;
  court_decision?: Option;
  court_decision_date?: string;
  sentence_date?: string;
  sentence_description?: string;
  is_active: boolean;
  is_closed: boolean;
}

interface ChargeRecommendationRequirementMap {
  id: number;
  inspection_requirement_id: number;
  inspection_requirement: {
    id: number;
    summary: string;
    requirement_source_details: InspectionRequirementSource[];
  };
}

interface SentenceTypeMapping {
  id: number;
  sentence_type_option_id: number;
  sentence_type_option: {
    id: number;
    name: string;
  };
}

export interface ChargeRecommendationAPIData {
  inspection_id: number;
  status?: string;
  date_to_crown_counsel?: string;
  charge_decision?: string;
  charge_decision_date?: string;
  court_file_number?: string;
  court_decision?: string;
  court_decision_date?: string;
  sentence_date?: string;
  sentence_description?: string;
  sentence_type_option_ids?: number[];
  inspection_requirement_ids: number[];
}

export interface SentenceTypeOption {
  id: number;
  name: string;
  sort_order?: number;
}
