import { mount } from "cypress/react";
import ComplaintGeneralInformation from "@/components/App/Complaints/Profile/ComplaintGeneralInformation";
import { Complaint } from "@/models/Complaint";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import dateUtils from "@/utils/dateUtils";
import { ComplaintSourceEnum } from "@/components/App/Complaints/ComplaintFormUtils";
import { RequirementSourceEnum } from "@/utils/constants";
import { Box } from "@mui/material";



describe("ComplaintGeneralInformation", () => {
  let mockOnEdit: sinon.SinonStub;
  let queryClient: QueryClient;

  const mockComplaint: Complaint = {
    id: 1,
    complaint_number: "COMP-001",
    case_file_id: 1,
    project_id: 1,
    project_description: "Test Project Description",
    concern_description: "Test concern description",
    location_description: "Test location description",
    primary_officer_id: 1,
    date_received: "2023-04-15T12:00:00Z",
    topic_id: 1,
    requirement_source_id: 1,
    requirement_source_description: "Test requirement source description",
    source_type_id: 1,
    source_agency_id: 1,
    source_first_nation_id: 1,
    is_active: true,
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
    primary_officer: { id: 1, name: "John Doe", is_active: true },
    project: { id: 1, name: "Test Project" },
    topic: { id: 1, name: "Test Topic" },
    source_type: { id: ComplaintSourceEnum.AGENCY, name: "Agency" },
    requirement_source: { id: RequirementSourceEnum.SCHEDULE_B, name: "Schedule B", source_title: "Schedule B" },
    source_contact: {
      full_name: "Test Contact",
      email: "test@example.com",
      phone: "(123) 456-7890",
      comment: "Test comment",
      description: "Test description",
    },
    requirement_detail: {
      id: 1,
      complaint_id: 1,
      order_number: "",
    },
    status: "Active",
    authorization: "Test Authorization",
    regulated_party: "Test Regulated Party",
    type: "Test Type",
    sub_type: "Test Sub Type",
    agency: { id: 1, name: "Test Agency" },
    first_nation: { id: 1, name: "Test First Nation" },
  };

  const mockQueryData = {
    data: [
      { id: 1, name: "Item 1" },
      { id: 2, name: "Item 2" },
    ],
  };

  const mountComponent = (complaintData = mockComplaint, allowEdit = true) => {
    mount(
      <QueryClientProvider client={queryClient}>
        <Box sx={{
          width: "800px",
          height: "800px",
          overflow: "visible",
          position: "relative"
        }}>
          <ComplaintGeneralInformation
            complaintData={complaintData}
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
      const style = doc.createElement('style');
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
    cy.contains("Test concern description").should("be.visible");
    cy.contains("Test Topic").should("be.visible");
    cy.contains("Test location description").should("be.visible");
    cy.contains("John Doe").should("be.visible");
    cy.contains(dateUtils.formatDate(mockComplaint.date_received)).should("be.visible");
  });

  it("renders requirement source information when available", () => {
    cy.contains("Requirement Source").should("be.visible");
    cy.contains("Schedule B").should("be.visible");
    cy.contains("Requirement Details").should("be.visible");
    cy.contains("Test requirement source description").should("be.visible");
  });

  it("renders order number when requirement source is ORDER", () => {
    const orderComplaint = {
      ...mockComplaint,
      requirement_source: { id: RequirementSourceEnum.ORDER, name: "Order", source_title: "Order" },
      requirement_detail: { id: 1, complaint_id: 1, order_number: "ORDER-123" },
    };
    mountComponent(orderComplaint);

    cy.contains("Requirement Source").should("be.visible");
    cy.contains("Order").should("be.visible");
    cy.contains("Order Number").should("be.visible");
    cy.contains("ORDER-123").should("be.visible");
  });

  it("renders complainant information section", () => {
    cy.contains("Complainant Information").should("be.visible");
    cy.contains("Complaint Source").should("be.visible");
    cy.contains("Agency").should("be.visible");
  });

  it("renders agency information when source type is AGENCY", () => {
    cy.contains("Organization Name").should("be.visible");
    cy.contains("Test Agency").should("be.visible");
  });

  it("renders first nation information when source type is FIRST_NATION", () => {
    const firstNationComplaint = {
      ...mockComplaint,
      source_type: { id: ComplaintSourceEnum.FIRST_NATION, name: "First Nation" },
    };
    mountComponent(firstNationComplaint);

    cy.contains("Organization Name").should("be.visible");
    cy.contains("Test First Nation").should("be.visible");
  });

  it("renders other description when source type is OTHER", () => {
    const otherComplaint = {
      ...mockComplaint,
      source_type: { id: ComplaintSourceEnum.OTHER, name: "Other" },
    };
    mountComponent(otherComplaint);

    cy.contains("Description").should("be.visible");
    cy.contains("Test description").should("be.visible");
  });

  it("renders contact information", () => {
    // Wait for the component to fully render and calculate dimensions
    cy.wait(100);

    // Check for text content first (more reliable than visibility)
    cy.get("body").should("contain.text", "Full Name");
    cy.get("body").should("contain.text", "Test Contact");
    cy.get("body").should("contain.text", "Email");
    cy.get("body").should("contain.text", "test@example.com");
    cy.get("body").should("contain.text", "Phone Number");
    cy.get("body").should("contain.text", "(123) 456-7890");
    cy.get("body").should("contain.text", "Comments");
    cy.get("body").should("contain.text", "Test comment");

    // Now try to check visibility with scrolling if needed
    cy.contains("Full Name").scrollIntoView().should("be.visible");
    cy.contains("Test Contact").scrollIntoView().should("be.visible");
    cy.contains("Email").scrollIntoView().should("be.visible");
    cy.contains("test@example.com").scrollIntoView().should("be.visible");
    cy.contains("Phone Number").scrollIntoView().should("be.visible");
    cy.contains("(123) 456-7890").scrollIntoView().should("be.visible");
    cy.contains("Comments").scrollIntoView().should("be.visible");
    cy.contains("Test comment").scrollIntoView().should("be.visible");
  });

  it("shows edit button when allowEdit is true", () => {
    cy.contains("button", "Edit").should("be.visible");
  });

  it("hides edit button when allowEdit is false", () => {
    mountComponent(mockComplaint, false);
    cy.contains("button", "Edit").should("not.exist");
  });

  it("calls onEdit when the Edit button is clicked", () => {
    cy.contains("button", "Edit").click();
    cy.get("@onEditStub").should("have.been.calledOnce");
  });
});
