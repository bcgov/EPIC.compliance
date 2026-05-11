import RequirementCard from "@/components/App/Inspections/Profile/Requirements/RequirementCard";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { Reorder } from "framer-motion";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { baseRequirement, regulatoryRequirement } from "./mockData";

describe("RequirementCard Component", () => {
  const queryClient = new QueryClient();

  // Helper function to mount component with necessary providers
  const mountComponent = (requirement: InspectionRequirement, isActive = false) => {
    const mockOnEdit = cy.stub().as("onEditHandler");
    const requirements = [requirement];

    return cy.mount(
      <QueryClientProvider client={queryClient}>
        <Reorder.Group
          axis="y"
          values={requirements}
          onReorder={cy.stub()}
        >
          <RequirementCard
            requirement={requirement}
            index={0}
            onEdit={mockOnEdit}
            isActive={isActive}
          />
        </Reorder.Group>
      </QueryClientProvider>
    );
  };

  it("renders standard requirement correctly", () => {
    mountComponent(baseRequirement);

    // Check basic content
    cy.contains("#1. Test Requirement").should("be.visible");
    cy.contains("Test Topic").should("be.visible");
    cy.contains("Test Source").should("be.visible");
    cy.contains("Condition #").should("be.visible");
    cy.contains("Section #").should("not.exist");
    cy.contains("Compliance Finding").should("be.visible");
    cy.contains("Enforcement Action").should("be.visible");
    cy.contains("No Action Required").should("be.visible");
  });

  it("renders regulatory considerations correctly", () => {
    mountComponent(regulatoryRequirement);

    // Check regulatory considerations specific content
    cy.contains("Regulatory Considerations").should("be.visible");
    cy.contains("Summary").should("be.visible");
    cy.contains("Test Topic").should("be.visible");
    cy.contains("Test Agency").should("be.visible");
  });

  it("shows active state when isActive is true", () => {
    mountComponent(baseRequirement, true);

    // Check for active border color
    cy.get("[class*='MuiBox-root']")
      .first()
      .should("have.css", "border-color", "rgb(46, 93, 215)"); // BCDesignTokens.surfaceColorBorderActive
  });

  it("calls onEdit when clicked", () => {
    mountComponent(baseRequirement);

    cy.get("[class*='MuiBox-root']").first().click();
    cy.get("@onEditHandler").should("have.been.calledOnce");
  });

  it("shows drag indicator for standard requirements but not for regulatory considerations", () => {
    // Mount standard requirement
    mountComponent(baseRequirement);
    cy.get("[data-testid='drag-indicator']").should("be.visible");

    // Mount regulatory considerations
    mountComponent(regulatoryRequirement);
    cy.get("[data-testid='drag-indicator']").should("not.be.visible");
  });

  it("renders condition number instead of section number when source is condition", () => {
    const conditionRequirement: InspectionRequirement = {
      ...baseRequirement,
      requirement_source_details: [
        {
          requirement_source: { id: "1", name: "Test Source" },
          requirement_source_id: 1, // This will trigger condition rendering
          section_number: null,
          condition_number: "C-123",
          amendment_number: "1",
          title: "Test Title",
          description: "Test Description",
          is_active: true,
          id: 1,
          requirement_id: 1,
          appendix_id: undefined,
          appendix: undefined,
          order_id: undefined,
          order: undefined,
          documents: [
            { id: 1, req_detail_id: 1, document_type: { id: "1", name: "Test Document" },
              document_type_id: 1,
              document_title: "Test Document",
              section_number: "1.1",
              section_title: "Test Section",
              description: "Test Description",
              is_active: true,
              appendix_id: undefined,
              appendix: undefined,
            },
          ],
        },
      ],
    };

    mountComponent(conditionRequirement);

    cy.contains("Condition #").should("be.visible");
    cy.contains("C-123").should("be.visible");
  });

  it("hides drag indicator when dragDisabled is true", () => {
    const mockOnEdit = cy.stub().as("onEditHandler");
    const requirements = [baseRequirement];

    cy.mount(
      <QueryClientProvider client={queryClient}>
        <Reorder.Group
          axis="y"
          values={requirements}
          onReorder={cy.stub()}
        >
          <RequirementCard
            requirement={baseRequirement}
            index={0}
            onEdit={mockOnEdit}
            isActive={false}
            dragDisabled={true}
          />
        </Reorder.Group>
      </QueryClientProvider>
    );

    // Drag indicator should be hidden when dragDisabled is true
    cy.get("[data-testid='drag-indicator']").should("not.be.visible");
  });

  it("remains clickable when dragDisabled is true", () => {
    const mockOnEdit = cy.stub().as("onEditHandler");
    const requirements = [baseRequirement];

    cy.mount(
      <QueryClientProvider client={queryClient}>
        <Reorder.Group
          axis="y"
          values={requirements}
          onReorder={cy.stub()}
        >
          <RequirementCard
            requirement={baseRequirement}
            index={0}
            onEdit={mockOnEdit}
            isActive={false}
            dragDisabled={true}
          />
        </Reorder.Group>
      </QueryClientProvider>
    );

    // Card should still be clickable even when drag is disabled
    cy.get("[class*='MuiBox-root']").first().click();
    cy.get("@onEditHandler").should("have.been.calledOnce");
  });
});
