import { mount } from "cypress/react";
import CaseFileGeneralInformation from "@/components/App/CaseFiles/Profile/CaseFileGeneralInformation";
import { CaseFile } from "@/models/CaseFile";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import dateUtils from "@/utils/dateUtils";
import { Box } from "@mui/material";

describe("CaseFileGeneralInformation", () => {
  let mockOnEdit: sinon.SinonStub;
  let queryClient: QueryClient;

  const mockCaseFile: CaseFile = {
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
    project_id: 0,
    primary_officer_id: 0,
    case_file_number: "",
    case_file_status: "",
    is_active: false,
  };

  const mockQueryData = {
    data: [
      { id: 1, name: "Item 1" },
      { id: 2, name: "Item 2" },
    ],
  };

  const mountComponent = (caseFileData = mockCaseFile) => {
    mount(
      <QueryClientProvider client={queryClient}>
        <Box sx={{ width: "800px" }}>
          <CaseFileGeneralInformation
            caseFileData={caseFileData}
            onEdit={mockOnEdit}
          />
        </Box>
      </QueryClientProvider>
    );
  };

  beforeEach(() => {
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
    cy.contains("Test Project Description").should("be.visible");
    cy.contains(dateUtils.formatDate(mockCaseFile.date_created)).should(
      "be.visible"
    );
    cy.contains("Test Initiation").should("be.visible");
    cy.contains("John Doe").should("be.visible");
    cy.contains("Jane Smith, Bob Johnson").should("be.visible");
  });

  // it("calls onEdit when the Edit button is clicked", () => {
  //   cy.contains("button", "Edit").click();
  //   cy.get("@onEditStub").should("have.been.calledOnce");
  // });
});
