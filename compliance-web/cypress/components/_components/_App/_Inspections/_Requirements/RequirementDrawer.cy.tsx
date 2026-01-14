import RequirementDrawer from "@/components/App/Inspections/Profile/Requirements/RequirementDrawer";
import { baseRequirement, mockInspection } from "./mockData";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { useReportStore } from "@/components/App/Inspections/Profile/Reports/reportStore";

describe("RequirementDrawer Component", () => {
  const queryClient = new QueryClient();

  const mountComponent = (requirement?: InspectionRequirement) => {
    const mockOnSubmit = cy.stub().as("onSubmitHandler");

    return cy.mount(
      <QueryClientProvider client={queryClient}>
        <RequirementDrawer
          inspectionData={mockInspection}
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
      inspectionReportsData: { is_open_for_editing: true },
    });
  });
  it("does not show action buttons when is_open_for_editing is false", () => {
    useReportStore.setState({
      inspectionReportsData: { is_open_for_editing: false },
    });
    mountComponent(baseRequirement);
    cy.contains("Delete").should("not.exist");
    cy.contains("Edit Requirement #1").should("not.exist");
    // If there are other action buttons, add similar checks here
  });

  it("renders create requirement drawer correctly", () => {
    mountComponent(baseRequirement);

    cy.contains("Edit Requirement #1").should("be.visible");
    cy.get("form").should("exist");
  });

  it("renders edit requirement drawer correctly", () => {
    mountComponent(baseRequirement);

    cy.contains("Edit Requirement #1").should("be.visible");
  });

  it("handles requirement deletion", () => {
    mountComponent(baseRequirement);

    // Click delete button
    cy.contains("Delete").click();

    // Confirm deletion
    cy.contains("button", "Delete").click();

  });

});
