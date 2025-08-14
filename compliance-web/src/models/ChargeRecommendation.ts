import { Option } from "./common";

export interface ChargeRecommendation {
  charge_recommendation_requirement_maps: ChargeRecommendationRequirementMap[];
  id: number;
  inspection_id: number;
  charge_recommendation_number: string;
  status: Option;
  date_to_crown_counsel?: string;
  charge_decision?: Option;
  charge_decision_date?: string;
  court_file_number?: string;
  court_appearances?: string;
  judgment?: Option;
  judgment_date?: string;
  sentence_date?: string;
  sentence_type?: string;
  is_active: boolean;
}

interface ChargeRecommendationRequirementMap {
  id: number;
  inspection_requirement_id: number;
  inspection_requirement: {
    id: number;
    summary: string;
  };
}

export interface ChargeRecommendationAPIData {
  inspection_id: number;
  status?: string;
  date_to_crown_counsel?: string;
  charge_decision?: string;
  charge_decision_date?: string;
  court_file_number?: string;
  court_appearances?: string;
  judgment?: string;
  judgment_date?: string;
  sentence_date?: string;
  sentence_type?: string;
  inspection_requirement_ids: number[];
}


