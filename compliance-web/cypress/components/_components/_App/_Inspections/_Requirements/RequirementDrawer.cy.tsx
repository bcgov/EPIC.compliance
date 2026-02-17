import RequirementDrawer from "@/components/App/Inspections/Profile/Requirements/RequirementDrawer";
import { baseRequirement, mockInspection } from "./mockData";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { useReportStore } from "@/components/App/Inspections/Profile/Reports/reportStore";
import { Inspection } from "@/models/Inspection";
import { InspectionStatusEnum } from "@/utils/constants";

describe("RequirementDrawer Component", () => {
  const queryClient = new QueryClient();

  const mountComponent = (requirement?: InspectionRequirement, inspection?: Inspection) => {
    const mockOnSubmit = cy.stub().as("onSubmitHandler");
    return cy.mount(
      <QueryClientProvider client={queryClient}>
        <RequirementDrawer
          inspectionData={inspection ?? mockInspection}
          requirement={requirement}
          index={0}
          onSubmit={mockOnSubmit}
        />
      </QueryClientProvider>
    );
  };

  beforeEach(() => {
    // Stub API calls
    cy.stub(window, "fetch").resolves({
      ok: true,
      json: () =>
        Promise.resolve([
          { id: "REQ", name: "Test Source" },
          { id: "REG", name: "Regulatory Consideration" },
        ]),
    });
    // Set Zustand store state for useReportStore
    useReportStore.setState({
      inspectionReportsData: { date_issued: new Date().toISOString() },
    });
  });
  it("does not show action buttons when inspection is closed", () => {
    useReportStore.setState({
      inspectionReportsData: { date_issued: new Date().toISOString() },
    });
    mockInspection.inspection_status = InspectionStatusEnum.CLOSED;
    mountComponent(baseRequirement, mockInspection);
    cy.contains("Delete").should("not.exist");
    cy.contains("Edit Requirement #1").should("not.exist");
  });

  it("renders create requirement drawer correctly", () => {
    mockInspection.inspection_status = InspectionStatusEnum.OPEN;
    mountComponent(baseRequirement, mockInspection);

    cy.contains("Edit Requirement #1").should("be.visible");
    cy.get("form").should("exist");
  });

  it("renders edit requirement drawer correctly", () => {
    mockInspection.inspection_status = InspectionStatusEnum.OPEN;
    mountComponent(baseRequirement, mockInspection);

    cy.contains("Edit Requirement #1").should("be.visible");
  });

  it("handles requirement deletion", () => {
    mockInspection.inspection_status = InspectionStatusEnum.OPEN;
    useReportStore.setState({
      inspectionReportsData: { date_issued: null },
    });
    mountComponent(baseRequirement, mockInspection);

    // Click delete button
    cy.contains("Delete").click();

    // Confirm deletion
    cy.contains("button", "Delete").click();

  });

});
