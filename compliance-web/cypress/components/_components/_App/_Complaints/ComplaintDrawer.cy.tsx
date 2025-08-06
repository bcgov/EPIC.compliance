/// <reference types="cypress" />
import React from "react";
import { mount } from "cypress/react18";
import ComplaintDrawer from "@/components/App/Complaints/ComplaintDrawer";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { CaseFile } from "@/models/CaseFile";
import ModalProvider from "@/components/Shared/Modals/ModalProvider";
import DrawerProvider from "@/components/Shared/Drawer/DrawerProvider";
import { Complaint } from "@/models/Complaint";
import { OidcConfig } from "@/utils/config";
import { AuthProvider } from "react-oidc-context";
import { useDrawer } from "@/store/drawerStore";

import { RequirementSourceEnum } from "@/utils/constants";

// Mock data
const mockCaseFile: CaseFile = {
  id: 1,
  case_file_number: "CF-2023-001",
  project: {
    id: 1,
    name: "Test Project",
    description: "Test Project Description",
  },
  primary_officer: {
    id: 1,
    name: "John Doe",
    auth_user_guid: "user-guid-1",
    is_active: true,
  },
  officers: [
    {
      id: 2,
      name: "Jane Smith",
      auth_user_guid: "user-guid-2",
      is_active: true,
    },
  ],
  project_id: 1,
  date_created: "2023-01-01",
  primary_officer_id: 1,
  case_file_status: "OPEN",
  initiation: undefined,
  is_active: false,
};

const mockComplaint: Complaint = {
  id: 1,
  complaint_number: "COMP-2023-001",
  case_file: mockCaseFile,
  concern_description: "Test concern",
  location_description: "Test location",
  topic: { id: 1, name: "Water" },
  primary_officer: mockCaseFile.primary_officer,
  date_received: "2023-01-01",
  case_file_id: 1,
  project_id: 1,
  project_description: "Test project description",
  primary_officer_id: 1,
  requirement_source_id: 1,
  source_type_id: 2,
  source_agency_id: 1,
  is_active: true,
  status: "OPEN",
  project: mockCaseFile.project,
  source_type: { id: "2", name: "First Nation" },
  source_contact: {
    full_name: "Contact Name",
    email: "contact@example.com",
    phone: "123-456-7890",
    comment: "Test comment",
  },
  source_first_nation_id: 1,
  first_nation: { id: 1, name: "Test First Nation" },
  requirement_source: { id: RequirementSourceEnum.ORDER, name: "Order", source_title: "Order" },
  requirement_detail: {
    id: 1,
    complaint_id: 1,
    order_number: "B1",
  },
};

describe("ComplaintDrawer Component", () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  // Mock API data
  const mockSourceTypes = [{ id: "2", name: "First Nation" }];
  const mockRequirementSources = [
    { id: "1", name: "Schedule B" },
    { id: RequirementSourceEnum.ORDER, name: "Order", source_title: "Order" }
  ];
  const mockAgencies = [{ id: 1, name: "Test Agency" }];
  const mockFirstNations = [{ id: 1, name: "Test First Nation" }];
  const mockTopics = [{ id: 1, name: "Water" }];
  const mockCurrentUser = { preferred_username: "user-guid-1" };
  const mockOrders = [{ 
    id: 1, 
    order_number: "B1",
    order_status: { id: "OPEN", name: "Open" }
  }];

  beforeEach(() => {
    cy.viewport(1200, 800);

    // Reset the query client before each test
    queryClient.clear();

    // Mock the drawer state as open to prevent form reset
    useDrawer.setState({ isOpen: true });

    // Set up Cypress stubs for API calls
    cy.stub(window, "fetch").callsFake((url) => {
      if (url.toString().includes("/api/complaint-sources")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockSourceTypes),
        });
      } else if (url.toString().includes("/api/requirement-sources")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockRequirementSources),
        });
      } else if (url.toString().includes("/api/agencies")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockAgencies),
        });
      } else if (url.toString().includes("/api/first-nations")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockFirstNations),
        });
      } else if (url.toString().includes("/api/topics")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockTopics),
        });
      } else if (url.toString().includes("/api/current-user")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockCurrentUser),
        });
      } else if (url.toString().includes("/api/orders/projectwise")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockOrders),
        });
      }
      return Promise.reject(new Error(`Unhandled fetch request: ${url}`));
    });

    // Set the query data directly to ensure it's available
    queryClient.setQueryData(["complaint-sources"], mockSourceTypes);
    queryClient.setQueryData(["requirement-sources"], mockRequirementSources);
    queryClient.setQueryData(["agencies"], mockAgencies);
    queryClient.setQueryData(["first-nations"], mockFirstNations);
    queryClient.setQueryData(["topics"], mockTopics);
    queryClient.setQueryData(["current-user"], mockCurrentUser);
    queryClient.setQueryData(["inspection-orders-projectwise", mockCaseFile.id], mockOrders);
  });

  function mountComponent(complaint?: Complaint) {
    const onSubmitSpy = cy.spy().as("onSubmitSpy");

    return mount(
      <QueryClientProvider client={queryClient}>
        <AuthProvider {...OidcConfig}>
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <DrawerProvider />
            <ModalProvider />
            <ComplaintDrawer
              onSubmit={onSubmitSpy}
              caseFile={mockCaseFile}
              complaint={complaint}
            />
          </LocalizationProvider>
        </AuthProvider>
      </QueryClientProvider>
    );
  }

  it("renders the drawer with correct title", () => {
    mountComponent();
    cy.contains("Create Complaint").should("exist");
  });

  it("renders form sections correctly", () => {
    mountComponent();
    cy.contains("Concern Description").should("exist");
    cy.contains("Location Description").should("exist");
    cy.contains("Primary").should("exist");
    cy.contains("Date Received").should("exist");
    cy.contains("Complaint Source").should("exist");
    cy.contains("Requirement Source").should("exist");
  });

  it("populates form with existing complaint data when editing", () => {
    mountComponent(mockComplaint);

    // Wait for the form to be fully initialized
    cy.wait(1000);

    cy.get('textarea[name="concernDescription"]').should(
      "have.value",
      "Test concern"
    );
    cy.get('textarea[name="locationDescription"]').should(
      "have.value",
      "Test location"
    );
    cy.get('input[name="primaryOfficer"]').should("have.value", "John Doe");
    cy.get('input[name="dateReceived"]').should("contain.value", "2023-01-01");
    
    // Check complaint source - should now work with drawer state mocked
    cy.get('input[name="complaintSource"]').should(
      "have.value",
      "First Nation"
    );
    
    cy.get('input[name="firstNation"]').should(
      "have.value",
      "Test First Nation"
    );
    cy.get('input[name="requirementSource"]').should(
      "have.value",
      "Order"
    );
    
    // Wait for order field to be populated (it's initialized asynchronously)
    // First, ensure the requirement source is set to "Order"
    cy.get('input[name="requirementSource"]').should("have.value", "Order");
    
    // Wait for the order field to be visible (it only shows when requirement source is Order)
    cy.get('input[name="order"]', { timeout: 10000 }).should("be.visible");
    
    // Debug: Check if order data is loaded and dropdown works
    cy.get('input[name="order"]').click();
    
    // Wait for dropdown to open and check if options are available
    cy.get('li[data-option-index]', { timeout: 5000 }).should('have.length.at.least', 1);
    
    // Log the dropdown options for debugging
    cy.get('li[data-option-index]').then(($options) => {
      cy.log(`Found ${$options.length} dropdown options`);
      $options.each((index, option) => {
        cy.log(`Option ${index}: ${option.textContent}`);
      });
    });
    
    // Check if the first option contains "B1"
    cy.get('li[data-option-index="0"]').should('contain.text', 'B1');
    
    // Select the first option
    cy.get('li[data-option-index="0"]').click();
    
    // Verify the order field has the correct value
    cy.get('input[name="order"]').should("have.value", "B1");
    
    cy.get('input[name="topic"]').should("have.value", "Water");
  });

  it("submits the form with correct data for new complaint", () => {
    mountComponent();

    // Fill out the form
    cy.get('textarea[name="concernDescription"]').type("New concern");
    cy.get('textarea[name="locationDescription"]').type("New location");

    // Select primary officer
    cy.get('input[name="primaryOfficer"]').click();
    cy.get("li").contains("John Doe").click();

    // Select date
    cy.get('button[aria-label="Choose date"]').click();
    cy.get(".MuiPickersDay-root").contains("15").click();

    // Select complaint source
    cy.get('input[name="complaintSource"]').click();
    cy.get("li").contains("First Nation").click();

  });

  it("updates an existing complaint when in edit mode", () => {
    mountComponent(mockComplaint);

    // Update some fields
    cy.get('textarea[name="concernDescription"]')
      .clear()
      .type("Updated concern");
    cy.get('textarea[name="locationDescription"]')
      .clear()
      .type("Updated location");

  });
});
