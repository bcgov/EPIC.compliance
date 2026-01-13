import React from "react";
import { mount } from "cypress/react";
import InspectionFileTabs from "@/components/App/Inspections/Profile/InspectionFileTabs";

describe("InspectionFileTabs Component", () => {
  beforeEach(() => {
    // Mount the component with the TabProvider to provide the tab context
    mount(<InspectionFileTabs />);
  });

  it("renders all tabs correctly", () => {
    // Check if all tabs are rendered
    cy.contains("Details").should("be.visible");
    cy.contains("Requirements").should("be.visible");
    cy.contains("Enforcement").should("be.visible");
    cy.contains("Report").should("be.visible");
  });

  it('has "Details" tab selected by default', () => {
    // The first tab (Details) should be selected by default
    cy.contains("Details").should("have.class", "Mui-selected");
  });

  it("changes the selected tab when clicked", () => {
    // Click on the Requirements tab
    cy.contains("Requirements").click();

    // Verify Requirements tab is now selected
    cy.contains("Requirements").should("have.class", "Mui-selected");
    cy.contains("Details").should("not.have.class", "Mui-selected");

    // Click on the Enforcement tab
    cy.contains("Enforcement").click();

    // Verify Enforcement tab is now selected
    cy.contains("Enforcement").should("have.class", "Mui-selected");
    cy.contains("Requirements").should("not.have.class", "Mui-selected");

    // Click on the Report tab
    cy.contains("Report").click();

    // Verify Report tab is now selected
    cy.contains("Report").should("have.class", "Mui-selected");
    cy.contains("Enforcement").should("not.have.class", "Mui-selected");
  });

  it("updates tab store when tab is changed", () => {
    // Click on the Requirements tab (index 1)
    cy.contains("Requirements").click();

    // We can't directly access the store, but we can verify the UI reflects the change
    cy.contains("Requirements").should("have.class", "Mui-selected");

    // Click on the Enforcement tab (index 2)
    cy.contains("Enforcement").click();
    cy.contains("Enforcement").should("have.class", "Mui-selected");

    // Click on the Report tab (index 3)
    cy.contains("Report").click();
    cy.contains("Report").should("have.class", "Mui-selected");

    // Go back to Details tab (index 0)
    cy.contains("Details").click();
    cy.contains("Details").should("have.class", "Mui-selected");
  });
});
