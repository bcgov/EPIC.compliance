


interface OpenItem {
  id: number;
  inspection_id: number;
  ir_number?: string;
  number: string;
  status: {
    id: string;
    name: string;
  };
}

export interface CaseFileOpenItems {
  has_open_items: boolean;
  inspections: OpenItem[];
  complaints: OpenItem[];
  orders: OpenItem[];
  warning_letters: OpenItem[];
  violation_tickets: OpenItem[];
  administrative_penalties: OpenItem[];
  charge_recommendations: OpenItem[];
  restorative_justice: OpenItem[];
}
