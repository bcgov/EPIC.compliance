import { mount } from "cypress/react";
import InspectionGeneralInformation from "@/components/App/Inspections/Profile/InspectionGeneralInformation";
import { Inspection } from "@/models/Inspection";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import dateUtils from "@/utils/dateUtils";
import { Box } from "@mui/material";

describe("InspectionGeneralInformation", () => {
  let mockOnEdit: sinon.SinonStub;
  let queryClient: QueryClient;

  const mockInspection: Inspection = {
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
    inspection_status: "Active",
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
      {
        id: 2,
        inspection_id: 1,
        attendance_option_id: 2,
        attendance_option: { id: "2", name: "First Nations" },
        data: [{ id: 1, name: "Test First Nation 1" }],
      },
    ],
  };

  const mockQueryData = {
    data: [
      { id: 1, name: "Item 1" },
      { id: 2, name: "Item 2" },
    ],
  };

  const mountComponent = (
    inspectionData = mockInspection,
    allowEdit = true
  ) => {
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
          <InspectionGeneralInformation
            inspectionData={inspectionData}
            caseFileData={inspectionData.case_file}
            onEdit={mockOnEdit}
            allowEdit={allowEdit}
          />
        </Box>
      </QueryClientProvider>
    );
  };

  beforeEach(() => {
    // Set viewport to ensure proper dimensions for DynamicHeightBox calculations
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

    mockOnEdit = cy.stub().as("onEditStub");
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    // Set up the mock data for the query
    queryClient.setQueryData(["someQueryKey"], mockQueryData);
    mountComponent();
  });

  it("renders the component with correct general information", () => {
    cy.contains("General Information").should("be.visible");
    cy.contains("Test Project").should("be.visible");
    cy.contains("Test project description").should("be.visible");
    cy.contains("Test location description").should("be.visible");
    cy.contains("10U 123456 6543210").should("be.visible");
    cy.contains("John Doe").should("be.visible");
    cy.contains("Test Initiation").should("be.visible");
    cy.contains("Field, Administrative").should("be.visible");
    cy.contains("In Progress").should("be.visible");
  });

  it("renders date range correctly when start and end dates are different", () => {
    const startDate = dateUtils.formatDate(mockInspection.start_date);
    const endDate = dateUtils.formatDate(mockInspection.end_date);
    const expectedDateRange = `${startDate} — ${endDate}`;

    cy.contains("Dates").should("be.visible");
    cy.contains(expectedDateRange).should("be.visible");
  });

  it("renders single date when start and end dates are the same", () => {
    const sameDateInspection = {
      ...mockInspection,
      start_date: "2023-04-15T12:00:00Z",
      end_date: "2023-04-15T12:00:00Z",
    };
    mountComponent(sameDateInspection);

    const singleDate = dateUtils.formatDate(sameDateInspection.start_date);
    cy.contains("Dates").should("be.visible");
    cy.contains(singleDate).should("be.visible");
  });

  it("renders in attendance information correctly", () => {
    // The formatInAttendance function should format the attendance data
    // Based on the mock data, it should show "Test Agency 1, Test Agency 2, Test First Nation 1"
    cy.contains("In Attendance").should("be.visible");
    cy.contains("Test Agency 1").should("be.visible");
    cy.contains("Test Agency 2").should("be.visible");
    cy.contains("Test First Nation 1").should("be.visible");
  });

  it("shows 'n/a' when no attendance data is available", () => {
    const noAttendanceInspection = {
      ...mockInspection,
      inspectionAttendances: [],
    };
    mountComponent(noAttendanceInspection);

    cy.contains("In Attendance").should("be.visible");
    cy.contains("n/a").should("be.visible");
  });

  it("renders all required properties", () => {
    const properties = [
      "Project",
      "Project Description",
      "Location Description",
      "UTM",
      "Primary",
      "Initiation",
      "Type",
      "Dates",
      "Project Status",
      "In Attendance",
    ];

    properties.forEach((property) => {
      cy.contains(property).should("be.visible");
    });
  });

  it("handles missing optional data gracefully", () => {
    const minimalInspection = {
      ...mockInspection,
      project_description: undefined,
      location_description: undefined,
      utm: undefined,
      types: [],
    };
    mountComponent(minimalInspection);

    // Should still render the component without errors
    cy.contains("General Information").should("be.visible");
    cy.contains("Project").should("be.visible");
    cy.contains("Type").should("be.visible");
  });

  it("shows edit button when allowEdit is true", () => {
    cy.contains("button", "Edit").should("be.visible");
  });

  it("hides edit button when allowEdit is false", () => {
    mountComponent(mockInspection, false);
    cy.contains("button", "Edit").should("not.exist");
  });

  it("calls onEdit when the Edit button is clicked", () => {
    cy.contains("button", "Edit").click();
    cy.get("@onEditStub").should("have.been.calledOnce");
  });

  it("renders edit button with correct icon and styling", () => {
    cy.contains("button", "Edit")
      .should("have.class", "MuiButton-text")
      .should("have.class", "MuiButton-sizeSmall");

    // Check for the EditRounded icon
    cy.get('[data-testid="EditRoundedIcon"]').should("exist");
  });

  it("handles case file data correctly", () => {
    // Verify that case file data is properly displayed
    cy.contains("Test Project").should("be.visible");
    cy.contains("Test project description").should("be.visible");
  });
});
