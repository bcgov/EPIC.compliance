import ContinuationReportEntryModal from "@/components/App/ContinuationReports/ContinuationReportEntryModal";
import { ContinuationReport } from "@/models/ContinuationReport";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

describe("ContinuationReportEntryModal.cy.tsx", () => {
  const queryClient = new QueryClient();

  const defaultProps = {
    onSubmit: () => {},
    context: {
      caseFileId: 123,
      contextType: "INSPECTION",
      contextId: 456,
    },
  };

  beforeEach(() => {
    cy.stub(defaultProps, 'onSubmit').as("onSubmit");
    
    cy.mount(
      <QueryClientProvider client={queryClient}>
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <ContinuationReportEntryModal {...defaultProps} />
        </LocalizationProvider>
      </QueryClientProvider>
    );
  });

  it("renders add entry form with correct title", () => {
    cy.contains("Add Entry").should("exist");
  });

  it("shows edit entry title when editing existing entry", () => {
    const existingEntry : ContinuationReport = {
      id: 1,
      date_created: "2024-01-01T12:00:00Z",
      rich_text: "<p>Test entry</p>",
      text: "Test entry",
      case_file_id: 123,
      context_type: "INSPECTION",
      context_id: 456,
      system_generated: false,
      is_active: true,
      keys: [],
    };

    cy.mount(
      <QueryClientProvider client={queryClient}>
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <ContinuationReportEntryModal
            {...defaultProps}
            continuationReportEntry={existingEntry}
          />
        </LocalizationProvider>
      </QueryClientProvider>
    );

    cy.contains("Edit Entry").should("exist");
  });

  it("shows validation errors for required fields", () => {
    cy.contains("button", "Add Entry").click();
    cy.contains("Date Created is required").should("exist");
    cy.contains("Action is required").should("exist");
  });

  it("allows selecting date and time", () => {
    cy.get('button[aria-label="Choose date"]').click();
    cy.get(".MuiPickersLayout-root").should("exist");
  });
}); 
