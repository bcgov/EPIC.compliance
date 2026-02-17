
import { OrderApproval } from "./OrderApproval";
import { StaffUser } from "./Staff";
export interface InspectionOrder {
  issuing_officer?: StaffUser;
  section?: {
    id: number;
    name: string;
  };
  id?: number;
  where_as?: string;
  now_therefore?: string;
  order_number?: string;
  section_id?: number;
  date_issued?: string;
  intended_issuance_date?: string;
  inspection_id?: number;
  issuing_officer_id?: number;
  order_requirement_maps?: OrderRequirementMap[];
  order_progress?: OrderProgress;
  order_status?: OrderStatus;
  order_approvals?: OrderApproval[];
  is_active?: boolean;
  type?: string;
}

export interface OrderStatus {
  id: string;
  name: string;
}

export interface OrderProgress {
  id: string;
  name: string;
}

interface OrderRequirementMap {
  id: number;
  inspection_requirement_id: number;
  inspection_requirement: {
    id: number;
    summary: string;
  };
}

export interface InspectionOrderAPIData {
  inspection_id: number;
  section_id?: number;
  issuing_officer_id?: number;
  intended_issuance_date?: string;
  where_as?: string;
  now_therefore?: string;
  inspection_requirement_ids: number[];
  order_number?: string;
}
