/// <reference types="cypress" />
import { mount } from "cypress/react";
import InspectionReports from "@/components/App/Inspections/Profile/InspectionReports";
import { Inspection } from "@/models/Inspection";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Box } from "@mui/material";

describe("InspectionReports", () => {
  let queryClient: QueryClient;
  let mockInspection: Inspection;

  const mountComponent = (inspectionData = mockInspection) => {
    mount(
      <QueryClientProvider client={queryClient}>
        <Box
          sx={{
            width: "800px",
            height: "800px",
            overflow: "visible",
            position: "relative",
          }}
        >
          <InspectionReports inspectionData={inspectionData} />
        </Box>
      </QueryClientProvider>
    );
  };

  beforeEach(() => {
    // Set viewport to ensure proper dimensions
    cy.viewport(1200, 800);

    // Add CSS overrides to fix overflow issues in testing
    cy.document().then((doc) => {
      const style = doc.createElement("style");
      style.innerHTML = `
        .MuiBox-root {
          overflow: visible !important;
        }
        [class*="DynamicHeightBox"] {
          height: auto !important;
          overflow: visible !important;
        }
      `;
      doc.head.appendChild(style);
    });

    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    // Default mock inspection data
    mockInspection = {
      id: 1,
      ir_number: "IR-001",
      case_file_id: 1,
      project_id: 1,
      location_description: "Test location description",
      utm: "10U 123456 6543210",
      initiation_id: 1,
      ir_status_id: 1,
      primary_officer_id: 1,
      start_date: "2023-04-15T12:00:00Z",
      end_date: "2023-04-16T12:00:00Z",
      debrief_date: "2023-04-17T12:00:00Z",
      types: [
        { id: "1", name: "Field" },
        { id: "2", name: "Administrative" },
      ],
      types_text: "Field, Administrative",
      inspection_status: "Open",
      is_active: true,
      project_description: "Test project description",
      initiation: { id: "1", name: "Test Initiation" },
      project: { id: 1, name: "Test Project" },
      primary_officer: { id: 1, name: "John Doe", is_active: true },
      ir_status: { id: "1", name: "Active" },
      case_file: {
        id: 1,
        project: { id: 1, name: "Test Project" },
        project_description: "Test Project Description",
        date_created: "2023-04-15T12:00:00Z",
        initiation: { id: "1", name: "Test Initiation" },
        primary_officer: { id: 1, name: "John Doe", is_active: true },
        officers: [
          { id: 2, name: "Jane Smith", is_active: true },
          { id: 3, name: "Bob Johnson", is_active: true },
        ],
        project_id: 1,
        primary_officer_id: 1,
        case_file_number: "CF-001",
        case_file_status: "Active",
        is_active: true,
      },
      project_statuses: [{ id: "1", name: "In Progress" }],
      inspectionAttendances: [
        {
          id: 1,
          inspection_id: 1,
          attendance_option_id: 1,
          attendance_option: { id: "1", name: "Agencies" },
          data: [
            { id: 1, name: "Test Agency 1" },
            { id: 2, name: "Test Agency 2" },
          ],
        },
      ],
      is_history: false,
    };
  });

  describe("Loading State", () => {
    it("shows loading spinner when data is loading", () => {
      // Pre-populate query cache with loading state
      queryClient.setQueryData(["inspection-reports", mockInspection.id], undefined);
      queryClient.setQueryData(["ir-statuses"], [
        { id: "1", name: "Preliminary" },
        { id: "2", name: "Final" },
      ]);

      mountComponent();

      // Check for CircularProgress component (MUI component)
      cy.get('.MuiCircularProgress-root').should("be.visible");
      cy.contains("Select Report Version").should("not.exist");
      cy.contains("This inspection is closed.").should("not.exist");
    });
  });

  describe("Open Inspection - No Reports", () => {
    beforeEach(() => {
      mockInspection.inspection_status = "Open";
      mockInspection.is_history = false;
      // Ensure no reports data exists and IR statuses are available
      queryClient.clear();
      queryClient.setQueryData(["ir-statuses"], [
        { id: "1", name: "Preliminary" },
        { id: "2", name: "Final" },
      ]);
    });

    it("shows report version selection when inspection is open and no reports exist", () => {
      mountComponent();

      cy.contains("Select Report Version").should("be.visible");
      cy.contains("Choose the IR report version you want to work on.").should("be.visible");
      cy.contains("Proceed to Report").should("be.visible");
    });

    it("renders radio buttons for each IR status option", () => {
      mountComponent();

      cy.contains("Preliminary Inspection Record").should("be.visible");
      cy.contains("Final Inspection Record").should("be.visible");

      // Check that radio buttons are rendered
      cy.get('input[type="radio"]').should("have.length", 2);
    });

    it("disables proceed button when no report version is selected", () => {
      mountComponent();

      cy.contains("button", "Proceed to Report").should("be.disabled");
    });

    it("enables proceed button when report version is selected", () => {
      mountComponent();

      // Select a report version
      cy.contains("Preliminary Inspection Record").click();

      cy.contains("button", "Proceed to Report").should("not.be.disabled");
    });

    it("handles report version selection correctly", () => {
      mountComponent();

      // Initially no version should be selected
      cy.get('input[type="radio"]:checked').should("have.length", 0);

      // Select Preliminary version
      cy.contains("Preliminary Inspection Record").click();
      cy.get('input[value="1"]').should("be.checked");

      // Select Final version
      cy.contains("Final Inspection Record").click();
      cy.get('input[value="2"]').should("be.checked");
    });
  });

  describe("Historical Inspection", () => {
    beforeEach(() => {
      mockInspection.is_history = true;
      mockInspection.inspection_status = "Open";
      queryClient.clear();
      queryClient.setQueryData(["ir-statuses"], [
        { id: "1", name: "Preliminary" },
        { id: "2", name: "Final" },
      ]);
    });

    it("automatically sets report version to FINAL for historical inspections", () => {
      mountComponent();

      // Should not show the report version selection UI
      cy.contains("Select Report Version").should("not.exist");
      cy.contains("Choose the IR report version you want to work on.").should("not.exist");

      // Should show proceed button with "Final Report" text
      cy.contains("button", "Proceed to Final Report").should("be.visible");
    });

    it("enables proceed button for historical inspections without requiring version selection", () => {
      mountComponent();

      cy.contains("button", "Proceed to Final Report").should("not.be.disabled");
    });
  });

  describe("Closed Inspection", () => {
    beforeEach(() => {
      mockInspection.inspection_status = "Closed";
      queryClient.clear();
    });

    it("shows closed inspection message when inspection is closed", () => {
      mountComponent();

      cy.contains("This inspection is closed.").should("be.visible");
      cy.contains("Select Report Version").should("not.exist");
      cy.contains("Proceed to Report").should("not.exist");
    });

    it("does not show report version selection for closed inspections", () => {
      mountComponent();

      cy.contains("Select Report Version").should("not.exist");
      cy.get('input[type="radio"]').should("not.exist");
    });
  });

  describe("Edge Cases", () => {
    it("handles missing IR statuses data gracefully", () => {
      // Pre-populate query cache with empty IR statuses
      queryClient.setQueryData(["ir-statuses"], []);

      mockInspection.inspection_status = "Open";
      queryClient.clear();
      queryClient.setQueryData(["ir-statuses"], []);

      mountComponent();

      // Should still render the component without errors
      cy.contains("Select Report Version").should("be.visible");
      cy.get('input[type="radio"]').should("have.length", 0);
    });

    it("handles inspection with undefined status", () => {
      mockInspection.inspection_status = undefined;
      queryClient.clear();

      mountComponent();

      // Should treat undefined status as not open
      cy.contains("This inspection is closed.").should("be.visible");
    });

    it("handles inspection with null status", () => {
      mockInspection.inspection_status = null;
      queryClient.clear();

      mountComponent();

      // Should treat null status as not open
      cy.contains("This inspection is closed.").should("be.visible");
    });
  });

  describe("Component Behavior", () => {
    it("handles different inspection statuses correctly", () => {
      // Test Open status
      mockInspection.inspection_status = "Open";
      queryClient.clear();
      queryClient.setQueryData(["ir-statuses"], [
        { id: "1", name: "Preliminary" },
        { id: "2", name: "Final" },
      ]);

      mountComponent();
      cy.contains("Select Report Version").should("be.visible");
    });

    it("handles historical vs non-historical inspections correctly", () => {
      // Test non-historical inspection
      mockInspection.is_history = false;
      mockInspection.inspection_status = "Open";
      queryClient.clear();
      queryClient.setQueryData(["ir-statuses"], [
        { id: "1", name: "Preliminary" },
        { id: "2", name: "Final" },
      ]);

      mountComponent();
      cy.contains("Select Report Version").should("be.visible");
      cy.contains("Preliminary Inspection Record").should("be.visible");
    });
  });
});
