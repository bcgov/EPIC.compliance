/// <reference types="cypress" />
import { mount } from "cypress/react18";
import ComplaintFileActions from "@/components/App/Complaints/Profile/ComplaintFileActions";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Complaint } from "@/models/Complaint";
import ModalProvider from "@/components/Shared/Modals/ModalProvider";

describe("ComplaintFileActions Component", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    // Mock complaint data for the query client
    const mockComplaint: Complaint = {
      id: 1,
      complaint_number: "COMP-2023-001",
      case_file_id: 1,
      case_file: {
        id: 1,
        case_file_number: "CF-2023-001",
        case_file_status: "OPEN",
        project_id: 1,
        project: {
          id: 1,
          name: "Project 1",
        },
        date_created: "2023-01-01",
        primary_officer_id: 1,
        primary_officer: {
          id: 1,
          name: "Officer 1",
          is_active: true,
        },
        initiation: undefined,
        is_active: true,
      },
      status: "OPEN",
      project_id: 1,
      project_description: "Project 1",
      concern_description: "Concern 1",
      location_description: "Location 1",
      date_received: "2023-01-01",
      primary_officer_id: 0,
      requirement_source_id: 0,
      source_type_id: 0,
      source_agency_id: 0,
      source_first_nation_id: 0,
      is_active: false,
      primary_officer: undefined,
      project: undefined,
      source_type: undefined,
      requirement_source: undefined,
      source_contact: undefined,
      requirement_detail: undefined,
      topic: {
        id: 1,
        name: "Topic 1",
      },
    };

    // Set the mock complaint data in the query client
    queryClient.setQueryData(["complaint", "COMP-2023-001"], mockComplaint);
  });

  const setup = (status = "OPEN") => {
    mount(
      <QueryClientProvider client={queryClient}>
        <ModalProvider />
        <ComplaintFileActions status={status} fileNumber="COMP-2023-001" />
      </QueryClientProvider>
    );
  };

  it("renders the actions dropdown button", () => {
    setup();
    cy.contains("button", "Actions").should("exist");
  });

  it("shows 'Close Complaint' option when status is OPEN", () => {
    setup("OPEN");
    cy.contains("button", "Actions").click();
    cy.contains("Close Complaint").should("exist");
    cy.contains("Reopen Complaint").should("not.exist");
  });

  it("shows 'Reopen Complaint' option when status is CLOSED", () => {
    setup("CLOSED");
    cy.contains("button", "Actions").click();
    cy.contains("Reopen Complaint").should("exist");
    cy.contains("Close Complaint").should("not.exist");
  });

  it("shows 'Delete Complaint' option regardless of status", () => {
    setup("OPEN");
    cy.contains("button", "Actions").click();
    cy.contains("Delete Complaint").should("exist");

    // Close the menu and test with CLOSED status
    cy.get("body").click();
    setup("CLOSED");
    cy.contains("button", "Actions").click();
    cy.contains("Delete Complaint").should("exist");
  });

  it("opens confirmation modal when clicking 'Close Complaint'", () => {
    setup("OPEN");
    cy.contains("button", "Actions").click();
    cy.contains("Close Complaint").click();

    // Check if confirmation modal appears
    cy.contains("Close Complaint?").should("exist");
    cy.contains("You are about to close complaint").should("exist");
    cy.contains("COMP-2023-001").should("exist");
    
    // Test the close button
    cy.get("button[aria-label='close']").should("exist").click();
    cy.contains("Close Complaint?").should("not.exist");
  });

  it("opens confirmation modal when clicking 'Reopen Complaint'", () => {
    setup("CLOSED");
    cy.contains("button", "Actions").click();
    cy.contains("Reopen Complaint").click();

    // Check if confirmation modal appears
    cy.contains("Reopen Complaint?").should("exist");
    cy.contains("Are you sure you want to reopen this complaint?").should("exist");
    
    // Test the close button
    cy.get("button[aria-label='close']").should("exist").click();
    cy.contains("Reopen Complaint?").should("not.exist");
  });

  it("opens confirmation modal when clicking 'Delete Complaint'", () => {
    setup("OPEN");
    cy.contains("button", "Actions").click();
    cy.contains("Delete Complaint").click();

    // Check if confirmation modal appears
    cy.contains("Delete Complaint?").should("exist");
    cy.contains("You are about to delete this complaint. Are you sure?").should("exist");
    
    // Test the close button
    cy.get("button[aria-label='close']").should("exist").click();
    cy.contains("Delete Complaint?").should("not.exist");
  });
});
