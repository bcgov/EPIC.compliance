import { FirstNation } from "./FirstNation";
import { Project } from "./Project";
import { ReportType } from "./ReportType";
import { StaffUser } from "./Staff";

export interface ReportFormValues {
  report_type?: ReportType;
  officers?: StaffUser[];
  project?: Project | null;
  first_nation?: FirstNation | null;
  start_date?: string | null;
  end_date?: string | null;
}
