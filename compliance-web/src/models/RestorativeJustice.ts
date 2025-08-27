export interface RestorativeJusticeRequirementMap {
  id: number;
  restorative_justice_id: number;
  inspection_requirement_id: number;
  inspection_requirement: {
    id: number;
    summary: string;
  };
}

export interface RestorativeJustice {
  id: number;
  inspection_id: number;
  restorative_justice_number: string;
  restitution_details?: string;
  date_restitution_complete?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  status:RJStatus;
  restorative_justice_requirement_maps?: RestorativeJusticeRequirementMap[];
}

export interface RestorativeJusticeAPIData {
  inspection_id: number;
  restorative_justice_number?: string;
  restitution_details?: string;
  date_restitution_complete?: string;
  status?: string;
  inspection_requirement_ids: number[];
}

export interface RestorativeJusticeUpdateAPIData {
  restorative_justice_number?: string;
  restitution_details?: string;
  date_restitution_complete?: string;
  status?: string;
  inspection_requirement_ids?: number[];
}

export interface RJStatus {
  id: string;
  name: string;
}
