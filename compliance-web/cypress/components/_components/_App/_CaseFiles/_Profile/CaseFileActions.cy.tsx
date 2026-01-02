import { mount } from "cypress/react";
import CaseFileActions from "@/components/App/CaseFiles/Profile/CaseFileActions";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ModalProvider from "@/components/Shared/Modals/ModalProvider";

describe("CaseFileActions", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient();
  });

  const mountComponent = (status: string) => {
    mount(
      <QueryClientProvider client={queryClient}>
        <ModalProvider />
        <CaseFileActions status={status} fileNumber="CF-123" />
      </QueryClientProvider>
    );
  };

  it("renders menu action dropdown", () => {
    mountComponent("open");
    cy.contains("button", "Actions").should("exist");
  });

  it("shows all actions for open case file", () => {
    mountComponent("open");
    cy.contains("button", "Actions").click();

    cy.contains("Link to Case File").should("exist");
    cy.contains("Unlink from Case File").should("exist");
    cy.contains("Close Case File").should("exist");
    cy.contains("Delete Case File").should("exist");
    cy.contains("Reopen Case File").should("not.exist");
  });

  it("shows appropriate actions for closed case file", () => {
    mountComponent("closed");
    cy.contains("button", "Actions").click();

    cy.contains("Link to Case File").should("not.exist");
    cy.contains("Unlink from Case File").should("not.exist");
    cy.contains("Close Case File").should("not.exist");
    cy.contains("Reopen Case File").should("exist");
    cy.contains("Delete Case File").should("exist");
  });

  it("handles Link to Case File click", () => {
    mountComponent("open");
    cy.contains("button", "Actions").click();
    cy.contains("Link to Case File").click();

    // Verify the dialog opens
    cy.get('div[role="presentation"]').should("exist");
    cy.contains("Link to Case File").should("exist");
    cy.get('input[name="caseFile"]').should("exist");
    cy.get('button[aria-label="close"]').should("exist").click();
  });

  it("handles Unlink from Case File click", () => {
    mountComponent("open");
    cy.contains("button", "Actions").click();
    cy.contains("Unlink from Case File").click();

    // Verify the dialog opens
    cy.get('div[role="presentation"]').should("exist");
    cy.contains("Unlink from Case File").should("exist");
    cy.get('input[name="caseFile"]').should("exist");
    cy.get('button[aria-label="close"]').should("exist").click();
  });

  it("handles Close Case File click", () => {
    mountComponent("open");
    cy.contains("button", "Actions").click();
    cy.contains("Close Case File").click();

    // Verify the confirmation dialog opens
    cy.contains("Close Case File").should("exist");
    cy.contains("Are you sure you want to close this case file?").should(
      "exist"
    );
    cy.contains("button", "Close Case File").should("exist").click();
    cy.contains("button", "Cancel").should("exist").click();
  });

  it("handles Delete Case File click", () => {
    mountComponent("open");
    cy.contains("button", "Actions").click();
    cy.contains("Delete Case File").click();

    // Verify the confirmation dialog opens
    cy.contains("Delete Case File").should("exist");
    cy.contains("You are about to delete this case file. Are you sure?").should(
      "exist"
    );
    cy.contains("button", "Delete").should("exist").click();
    cy.contains("button", "Cancel").should("exist").click();
  });

  it("handles Reopen Case File click", () => {
    mountComponent("closed");
    cy.contains("button", "Actions").click();
    cy.contains("Reopen Case File").click();

    // Verify the confirmation dialog opens
    cy.contains("Reopen Case File").should("exist");
    cy.contains("You are about to reopen this case file. Are you sure?").should(
      "exist"
    );
    cy.contains("button", "Reopen Case File").should("exist").click();
    cy.contains("button", "Cancel").should("exist").click();
  });
});
