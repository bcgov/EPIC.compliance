
export interface RequirementSource {
  id: string;
  name: string;
  source_title: string;
  sort_order?: number;
}

export interface RequirementDetails {
  id: number;
  complaint_id: number;
  created_by?: string;
  order_number?: string;
}
