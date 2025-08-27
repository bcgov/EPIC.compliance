// cypress/component/InspectionDrawer.spec.tsx
import { mount } from "cypress/react18";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import InspectionDrawer from "@/components/App/Inspections/InspectionDrawer";
import { Inspection } from "@/models/Inspection";
import dayjs from "dayjs";
import { AttendanceEnum } from "@/utils/constants";
import { CaseFile } from "@/models/CaseFile";
import { AuthProvider } from "react-oidc-context";
import { OidcConfig } from "@/utils/config";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";

describe("InspectionDrawer Component", () => {
  let mockOnSubmit: sinon.SinonStub;
  let queryClient: QueryClient;

  const mockCaseFile: CaseFile = {
    id: 1,
    project: { id: 1, name: "Test Project" },
    date_created: "2023-04-15T12:00:00Z",
    initiation: { id: "1", name: "Test Initiation" },
    primary_officer: { id: 1, name: "John Doe", auth_user_guid: "123", is_active: true },
    officers: [
      { id: 2, name: "Jane Smith", auth_user_guid: "124", is_active: true },
      { id: 3, name: "Bob Johnson", auth_user_guid: "125", is_active: true },
    ],
    project_id: 0,
    primary_officer_id: 0,
    case_file_number: "",
    case_file_status: "",
    is_active: false,
  };

  const mockInspection: Inspection = {
    id: 1,
    ir_number: "IR12345",
    authorization: "12332",
    regulated_party: "Regulated Party",
    case_file_id: 1,
    project_id: 1,
    initiation_id: 1,
    ir_status_id: 1,
    project_status_id: 1,
    primary_officer_id: 1,
    project_description: "Project Description",
    type: "Type",
    sub_type: "Sub Type",
    location_description: "Location Description",
    primary_officer: { id: 1, name: "Officer Name", is_active: true },
    ir_status: { id: "1", name: "Status" },
    project_status: { id: "1", name: "Project Status" },
    debrief_date: dayjs("2023-01-01").toISOString(),
    types: [
      { id: "1", name: "Type1" },
      { id: "2", name: "Type2" },
    ],
    start_date: dayjs("2023-01-01").toISOString(),
    end_date: dayjs("2023-01-02").toISOString(),
    inspectionAttendances: [
      {
        attendance_option: { id: AttendanceEnum.OTHER, name: "Option1" },
        attendance_option_id: AttendanceEnum.OTHER as unknown as number,
        data: "Other",
        id: 1,
        inspection_id: 1,
      },
    ],
    utm: "",
    types_text: "Type1, Type2",
    inspection_status: "",
    is_active: false,
    initiation: { id: "1", name: "Initiation" },
    project: { id: 1, name: "Project" },
    case_file: {
      id: 1,
      case_file_number: "12345",
      date_created: dayjs("2023-01-01").toISOString(),
      project_id: 1,
      primary_officer_id: 1,
      case_file_status: "open",
      initiation: { id: "1", name: "Initiation" },
      is_active: true,
      project: { id: 1, name: "Project" },
      primary_officer: { id: 1, name: "Officer Name", is_active: true },
    },
  };

  // Mock data for the query that's causing the issue
  const mockQueryData = {
    data: [
      { id: 1, name: "Item 1" },
      { id: 2, name: "Item 2" },
    ],
  };

  // Create a wrapper component that provides the mock auth context
  const TestWrapper = ({ children }: { children: React.ReactNode }) => {
    
    return (
      <QueryClientProvider client={queryClient}>
        <AuthProvider {...OidcConfig}>
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            {children}
          </LocalizationProvider>
        </AuthProvider>
      </QueryClientProvider>
    );
  };

  beforeEach(() => {
    mockOnSubmit = cy.stub().as("onSubmit");
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    queryClient.setQueryData(["someQueryKey"], mockQueryData);

    // Use the TestWrapper component instead
    mount(
      <TestWrapper>
        <InspectionDrawer
          onSubmit={mockOnSubmit}
          inspection={mockInspection}
          caseFile={mockCaseFile}
        />
      </TestWrapper>
    );
  });

  it("should render the component with the correct title", () => {
    cy.get("h6").contains(mockInspection.ir_number);
    cy.get("button").contains("Save").should("be.disabled");
    cy.get("button").contains("Cancel").should("be.disabled");
  });

  it("should show the button disabled when creating a new inspection", () => {
    mount(
      <TestWrapper>
        <InspectionDrawer onSubmit={mockOnSubmit} caseFile={mockCaseFile} />
      </TestWrapper>
    );
    cy.get("button").contains("Create").should("be.disabled");
  });
});
