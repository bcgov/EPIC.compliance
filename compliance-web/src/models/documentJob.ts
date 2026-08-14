export enum DocumentJobStatus {
    IN_PROGRESS = "In Progress",
    COMPLETED = "Completed",
    FAILED = "Failed",
    CANCELLED = "Cancelled",
}


export interface DocumentJob {
  id: string;
  user_id: number;
  inspection_report_id?: number;
  status: DocumentJobStatus;
  output_format: "pdf" | "docx";
  download_name?: string;
  relative_url?: string;
  started_at: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}