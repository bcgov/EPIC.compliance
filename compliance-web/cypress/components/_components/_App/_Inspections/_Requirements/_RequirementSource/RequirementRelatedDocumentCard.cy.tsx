import RequirementRelatedDocumentCard from "@/components/App/Inspections/Profile/Requirements/RequirementSource/RequirementRelatedDocumentCard";
import { RequirementRelatedDocumentData } from "@/models/InspectionRequirementSource";

describe("RequirementRelatedDocumentCard", () => {
  const mockRelatedDocument: RequirementRelatedDocumentData = {
    documentTitle: "Test Document",
    sections: [
      {
        sectionNumber: "1.1",
        sectionTitle: "Test Section",
        description: {
          html: "<p>Test description</p>",
          text: "Test description",
        },
      },
      {
        sectionNumber: "1.2",
        sectionTitle: "Another Section",
        description: {
          html: "<p>Another description</p>",
          text: "Another description",
        },
      },
    ],
  };

  let mockProps;

  beforeEach(() => {
    mockProps = {
      relatedDocument: mockRelatedDocument,
      index: 0,
      onAddRelatedDocumentSection: cy.stub().as("onAddRelatedDocumentSection"),
      onDeleteRelatedDocumentSection: cy.stub().as("onDeleteRelatedDocumentSection"),
      onEditRelatedDocumentSection: cy.stub().as("onEditRelatedDocumentSection"),
    };

    cy.mount(<RequirementRelatedDocumentCard {...mockProps} />);
  });

  it("displays the document title", () => {
    cy.contains("Test Document").should("be.visible");
  });

  it("starts expanded by default", () => {
    cy.get("[id^=requirement-related-document-panel]").should("have.attr", "aria-expanded", "true");
    cy.contains("Test Section").should("be.visible");
  });

  it("collapses and expands when clicking the header", () => {
    // Collapse
    cy.get("[id^=requirement-related-document-panel]").click();
    cy.get("[id^=requirement-related-document-panel]").should("have.attr", "aria-expanded", "false");
    cy.contains("Test Section").should("not.be.visible");

    // Expand
    cy.get("[id^=requirement-related-document-panel]").click();
    cy.get("[id^=requirement-related-document-panel]").should("have.attr", "aria-expanded", "true");
    cy.contains("Test Section").should("be.visible");
  });

  it("calls onAddRelatedDocumentSection when clicking Add Section button", () => {
    cy.contains("button", "Section").click();
    cy.get("@onAddRelatedDocumentSection").should("have.been.calledOnce");
  });

  it("displays sections in order by section number", () => {
    cy.get("[id^=requirement-related-document-panel]")
      .parent()
      .within(() => {
        cy.contains("1.1").should("be.visible");
        cy.contains("1.2").should("be.visible");
      });
  });

  it("calls onEditRelatedDocumentSection when clicking edit button", () => {
    cy.get("[data-testid='requirement-related-document-edit-0-0']").first().click();
    cy.get("@onEditRelatedDocumentSection").should("have.been.calledWith", 
      mockRelatedDocument.sections[0]
    );
  });

  it("calls onDeleteRelatedDocumentSection when clicking delete button", () => {
    cy.get("[data-testid='requirement-related-document-delete-0-0']").first().click();
    cy.get("@onDeleteRelatedDocumentSection").should("have.been.calledWith",
      mockRelatedDocument.sections[0]
    );
  });

  it("renders section details correctly", () => {
    cy.contains("Section #:").should("be.visible");
    cy.contains("1.1").should("be.visible");
    cy.contains("Section Title:").should("be.visible");
    cy.contains("Test Section").should("be.visible");
    cy.contains("Description:").should("be.visible");
    cy.get("div").contains("Test description").should("be.visible");
  });

  it("Add Section button is only visible when expanded", () => {
    // Visible when expanded
    cy.contains("button", "Section").should("be.visible");
    
    // Collapse
    cy.get("[id^=requirement-related-document-panel]").click();
    cy.wait(0);
    // Not visible when collapsed
    cy.contains("button", "Section").should("not.exist");
  });
});
