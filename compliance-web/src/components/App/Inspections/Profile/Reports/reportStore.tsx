import { create } from "zustand";
import { Inspection } from "@/models/Inspection";
import { DEFAULT_REPORT_TAB_CONTENT, InspectionStatusEnum } from "@/utils/constants";
import { CaseFile } from "@/models/CaseFile";
import { InspectionRecord } from "@/models/InspectionRecord";
import { QueryClient } from "@tanstack/react-query";
import { IRApproval } from "@/models/IRApproval";

// Define the store state and actions
interface ReportStore {
  queryClient: QueryClient;
  inspectionReportsData: InspectionRecord | undefined;
  irApprovalsData: IRApproval[] | undefined;
  inspectionData: Inspection | undefined;
  caseFileData: CaseFile | undefined;
  proponentLabel?: string;
  inspectionScope?: string;
  preliminaryReviewDetails?: string;
  findingsStatement?: string;
  actionsRequired?: string;
  enforcementSummary?: string;
  isReportsReadOnly?: boolean;
  isHistorical?: boolean;

  setQueryClient: (queryClient: QueryClient) => void;
  setInspectionReportsData: (inspectionReportsData: InspectionRecord) => void;
  setIRApprovalsData: (irApprovalsData: IRApproval[]) => void;
  setInspectionData: (inspectionData: Inspection) => void;
  setCaseFileData: (caseFileData: CaseFile) => void;
  setInspectionScope: (inspectionScope: string) => void;
  setPreliminaryReviewDetails: (preliminaryReviewDetails: string) => void;
  setFindingsStatement: (findingsStatement: string) => void;
  setActionsRequired: (actionsRequired: string) => void;
  setEnforcementSummary: (enforcementSummary: string) => void;
  reset: () => void;
}

// Create the Zustand store
export const useReportStore = create<ReportStore>((set) => ({
  queryClient: new QueryClient(),
  inspectionReportsData: undefined,
  irApprovalsData: undefined,
  inspectionData: undefined,
  caseFileData: undefined,
  proponentLabel: undefined,
  inspectionScope: undefined,
  preliminaryReviewDetails: undefined,
  findingsStatement: undefined,
  actionsRequired: undefined,
  enforcementSummary: DEFAULT_REPORT_TAB_CONTENT,
  isReportsReadOnly: false,
  isHistorical: false,

  setQueryClient: (queryClient: QueryClient) => set({ queryClient }),
  setInspectionReportsData: (inspectionReportsData: InspectionRecord) => {
    const queryClient = useReportStore.getState().queryClient;
    const inspectionData = useReportStore.getState().inspectionData;
    set({ inspectionReportsData });
    queryClient.setQueryData(
      ["inspection-reports", inspectionData?.id],
      inspectionReportsData
    );
  },
  setIRApprovalsData: (irApprovalsData: IRApproval[]) => {
    const queryClient = useReportStore.getState().queryClient;
    const inspectionData = useReportStore.getState().inspectionData;
    const inspectionReportsData =
      useReportStore.getState().inspectionReportsData;
    set({ irApprovalsData });
    queryClient.setQueryData(
      ["ir-approvals", inspectionData?.id, inspectionReportsData?.id],
      irApprovalsData
    );
  },
  setInspectionData: (inspectionData: Inspection) => {
    set({
      inspectionData,
      isReportsReadOnly:
        inspectionData?.inspection_status === InspectionStatusEnum.CLOSED,
      isHistorical: inspectionData?.is_history ?? false,
    });
  },
  setCaseFileData: (caseFileData: CaseFile) => {
    set({ caseFileData });
    set({
      proponentLabel:
        caseFileData?.authorization &&
        /^E\d{1,3}-\d{1,3}$/.test(caseFileData.authorization)
          ? "Certificate Holder"
          : "Regulated Party",
    });
  },
  setInspectionScope: (inspectionScope: string) => set({ inspectionScope }),
  setPreliminaryReviewDetails: (preliminaryReviewDetails: string) =>
    set({ preliminaryReviewDetails }),
  setFindingsStatement: (findingsStatement: string) =>
    set({ findingsStatement }),
  setActionsRequired: (actionsRequired: string) => set({ actionsRequired }),
  setEnforcementSummary: (enforcementSummary: string) =>
    set({ enforcementSummary }),
  reset: () =>
    set({
      inspectionReportsData: undefined,
      inspectionData: undefined,
      caseFileData: undefined,
      inspectionScope: undefined,
      findingsStatement: undefined,
      actionsRequired: undefined,
      enforcementSummary: DEFAULT_REPORT_TAB_CONTENT,
      isReportsReadOnly: false,
    }),
}));
