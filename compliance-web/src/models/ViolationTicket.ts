export interface ViolationTicket {
  violation_ticket_requirement_maps: ViolationTicketRequirementMap[];
  id: number;
  inspection_id: number;
  vt_number: string;
  date_issued: string;
  ticket_number: string;
  fine_amount: string;
  status: VTStatus;
  status_date: string;
  created_date: string;
  updated_date: string;
  is_closed: boolean;
}

interface ViolationTicketRequirementMap {
  id: number;
  inspection_requirement_id: number;
  inspection_requirement: {
    id: number;
    summary: string;
  };
}

export interface ViolationTicketAPIData {
  inspection_id: number;
  date_issued?: string;
  ticket_number: string;
  fine_amount?: string;
  status?: string;
  status_date?: string;
  inspection_requirement_ids: number[];
}

export interface VTStatus {
  id: string;
  name: string;
}


