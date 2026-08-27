/// <reference types="cypress" />
import { mount } from "cypress/react";
import InspectionFileActions from "@/components/App/Inspections/Profile/InspectionFileActions";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Inspection } from "@/models/Inspection";
import ModalProvider from "@/components/Shared/Modals/ModalProvider";

describe("InspectionFileActions Component", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
        mutations: {
          retry: false,
        },
      },
    });

    // Mock inspection data for the query client
    const mockInspection: Inspection = {
      id: 1,
      case_file_id: 1,
      ir_number: "INSP-2023-001",
      project_id: 0,
      location_description: "Test Location",
      utm: "1234567890",
      initiation_id: 0,
      ir_status_id: 0,
      primary_officer_id: 0,
      start_date: "2023-01-01",
      end_date: "2023-01-02",
      types: [],
      types_text: "",
      inspection_status: "",
      is_active: false,
      initiation: undefined,
      project: undefined,
      primary_officer: undefined,
      ir_status: undefined,
      case_file: undefined,
      project_statuses: [],
      debrief_date: "2023-01-03",
    };

    // Set the mock inspection data in the query client
    queryClient.setQueryData(["inspection", "INSP-2023-001"], mockInspection);
  });

  const mountComponent = (status = "open") => {
    mount(
      <QueryClientProvider client={queryClient}>
        <ModalProvider />
        <InspectionFileActions status={status} fileNumber="INSP-2023-001" />
      </QueryClientProvider>
    );
  };

  it("renders menu action dropdown", () => {
    mountComponent();
    cy.contains("button", "Actions").should("exist");
  });

  it("shows all actions for open inspection", () => {
    mountComponent("open");
    cy.contains("button", "Actions").click();

    cy.contains("Cancel Inspection").should("exist");
    cy.contains("Close as Note to File").should("exist");
    cy.contains("Close").should("exist");
    cy.contains("Delete Inspection").should("exist");
  });

  it("shows appropriate actions for canceled inspection", () => {
    mountComponent("canceled");
    cy.contains("button", "Actions").click();

    cy.contains("Cancel Inspection").should("not.exist");
    cy.contains("Close as Note to File").should("not.exist");
    cy.contains("Close").should("not.exist");
    cy.contains("Delete Inspection").should("exist");
  });

  it("shows appropriate actions for closed inspection", () => {
    mountComponent("closed");
    cy.contains("button", "Actions").click();

    cy.contains("Cancel Inspection").should("not.exist");
    cy.contains("Close as Note to File").should("not.exist");
    cy.contains("Close").should("not.exist");
    cy.contains("Delete Inspection").should("exist");
  });

  it("handles Cancel Inspection click", () => {
    mountComponent("open");
    cy.contains("button", "Actions").click();
    cy.contains("Cancel Inspection").click();

    // Verify the confirmation dialog opens
    cy.contains("Cancel Inspection?").should("exist");
    cy.contains("Are you sure you want to cancel this inspection?").should(
      "exist"
    );
    cy.contains("button", "Cancel Inspection").should("exist").click();
    cy.contains("button", "Cancel").should("exist").click();
  });

  it("handles Close as Note to File click", () => {
    mountComponent("open");
    cy.contains("button", "Actions").click();
    cy.get("li[id='Close as Note to File']").click();

    // Verify the confirmation dialog opens
    cy.contains("Close Inspection as Note to File?").should("exist");
    cy.contains(
      "Are you sure you want to close inspection as note to file?"
    ).should("exist");
    cy.contains("button", "Close Inspection").should("exist").click();
    cy.contains("button", "Cancel").should("exist").click();
  });

  // it("handles Closed click with no pending items", () => {
  //   // Mock window.fetch to intercept the API call
  //   cy.window().then((win) => {
  //     cy.stub(win, 'fetch').callsFake((url) => {
  //       if (url.includes('pending-items')) {
  //         return Promise.resolve({
  //           ok: true,
  //           status: 200,
  //           json: () => Promise.resolve([]), // Empty array = no pending items
  //         });
  //       }
  //       // For other requests, use the original fetch
  //       return win.fetch(url);
  //     });
  //   });

  //   mountComponent("open");
  //   cy.contains("button", "Actions").click();
  //   cy.get("li[id='Close']").last().click();

  //   // Wait for the "Checking Pending Items..." modal to appear
  //   cy.contains("Checking Pending Items...").should("exist");

  //   // Wait for the fetch to complete
  //   cy.wait(1000);

  //   // Verify the confirmation dialog opens after the check completes
  //   cy.contains("Close Inspection?").should("exist");
  //   cy.contains("Are you sure you want to close inspection?").should("exist");
  //   cy.contains("button", "Close Inspection").should("exist");

  //   // Close the modal to clean up
  //   cy.contains("button", "Cancel").should("exist").click();
  //   cy.contains("Close Inspection?").should("not.exist");
  // });


  // it("handles Closed click with pending items", () => {
  //   // Mock window.fetch to return pending items
  //   const pendingItems = [
  //     {
  //       requirement: {
  //         id: 1,
  //         summary: "Test requirement",
  //       },
  //       item: {
  //         id: 5,
  //         name: "Order",
  //       },
  //       is_created: false,
  //       item_number: null,
  //     },
  //   ];

  //   cy.window().then((win) => {
  //     cy.stub(win, 'fetch').callsFake((url) => {
  //       if (url.includes('pending-items')) {
  //         return Promise.resolve({
  //           ok: true,
  //           status: 200,
  //           json: () => Promise.resolve(pendingItems), // Return pending items
  //         });
  //       }
  //       // For other requests, use the original fetch
  //       return win.fetch(url);
  //     });
  //   });

  //   mountComponent("open");
  //   cy.contains("button", "Actions").click();
  //   cy.get("li[id='Close']").last().click();

  //   // Wait for the "Checking Pending Items..." modal to appear
  //   cy.contains("Checking Pending Items...").should("exist");

  //   // Wait for the fetch to complete
  //   cy.wait(1000);

  //   // Verify the blocking modal appears
  //   cy.contains("Cannot Close Inspection").should("exist");
  //   cy.contains("button", "Return to Inspection").should("exist").click();

  //   // Verify modal is closed
  //   cy.contains("Cannot Close Inspection").should("not.exist");
  // });

  it("handles Delete Inspection click", () => {
    mountComponent("open");

    // Wait a bit to ensure any previous modals are fully closed
    cy.wait(200);

    cy.contains("button", "Actions").click();
    cy.contains("Delete Inspection").click();

    // Verify the confirmation dialog opens
    cy.contains("Delete Inspection?").should("exist");
    cy.contains(
      "You are about to delete this inspection. Are you sure?"
    ).should("exist");
    cy.contains("button", "Delete").should("exist");

    // Close the modal to clean up
    cy.contains("button", "Cancel").should("exist").click();
    cy.contains("Delete Inspection?").should("not.exist");
  });
});
