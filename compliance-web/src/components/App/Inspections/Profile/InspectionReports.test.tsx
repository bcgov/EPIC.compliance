// @vitest-environment jsdom
import { act, useEffect } from "react";
import { createRoot, Root } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { Inspection } from "@/models/Inspection";
import { InspectionRecord } from "@/models/InspectionRecord";
import { useReportStore } from "./Reports/reportStore";
import InspectionReports from "./InspectionReports";

const previousInspection = { id: 1 } as Inspection;
const currentInspection = { id: 2, inspection_status: "Open" } as Inspection;
const previousReport = { id: 700, inspection_id: 1 } as InspectionRecord;
const currentReport = { id: 708, inspection_id: 2 } as InspectionRecord;

// Stable references, as react-query hands back for cached data
const noApprovals: never[] = [];
const noStatuses: never[] = [];

vi.mock("@/hooks/useInspectionReports", () => ({
  useInspectionReportsData: () => ({ data: currentReport, isLoading: false }),
  useFetchIRApprovals: () => ({ data: noApprovals }),
  useCreateInspectionRecord: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/hooks/useInspections", () => ({
  useIRStatusesData: () => ({ data: noStatuses }),
}));

vi.mock("@/components/Shared/DynamicHeightBox", () => ({
  default: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Stands in for ReportTabs when its inspection, case file and image queries are all
// served from cache: it stores the inspection once, in the same commit its parent mounts,
// and nothing makes it store it again.
vi.mock("./Reports/ReportTabs", () => ({
  default: function ReportTabsStub() {
    const setInspectionData = useReportStore((state) => state.setInspectionData);
    useEffect(() => {
      setInspectionData(currentInspection);
    }, [setInspectionData]);
    return null;
  },
}));

describe("InspectionReports", () => {
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
    container = document.createElement("div");
    document.body.appendChild(container);
    root = createRoot(container);
  });

  afterEach(() => {
    act(() => root.unmount());
    container.remove();
    useReportStore.getState().reset();
  });

  it("keeps the inspection its report tabs stored when replacing a previous inspection's report", () => {
    useReportStore.setState({
      inspectionData: previousInspection,
      inspectionReportsData: previousReport,
    });

    act(() => {
      root.render(
        <QueryClientProvider client={new QueryClient()}>
          <InspectionReports inspectionData={currentInspection} />
        </QueryClientProvider>
      );
    });

    const state = useReportStore.getState();
    expect(state.inspectionData?.id).toBe(currentInspection.id);
    expect(state.inspectionReportsData?.id).toBe(currentReport.id);
  });

  it("still clears what was left over from the previous inspection", () => {
    useReportStore.setState({
      inspectionData: previousInspection,
      inspectionReportsData: previousReport,
      inspectionScope: "<p>previous inspection's scope</p>",
    });

    act(() => {
      root.render(
        <QueryClientProvider client={new QueryClient()}>
          <InspectionReports inspectionData={currentInspection} />
        </QueryClientProvider>
      );
    });

    expect(useReportStore.getState().inspectionScope).toBeUndefined();
  });
});
