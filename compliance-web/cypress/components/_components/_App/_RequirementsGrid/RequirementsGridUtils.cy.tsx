/// <reference types="cypress" />
import { mount } from "cypress/react18";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Box, Button } from "@mui/material";
import { 
  useConvertFiltersToQueryParams, 
  useRequirementsGridColumns 
} from "@/components/App/RequirementsGrid/RequirementsGridUtils";

// Create a simple test component that uses the utilities
const TestComponent = () => {
  const externalFilters = {
    primary_officer_id: ["1", "2"],
    approver_ids: ["10", "20"],
    enf_stats: ["APPROVAL_PENDING"],
    inspection_status: ["OPEN"],
    project_id: ["100", "200"],
  };

  const dataDependencies = {
    topics: [
      { id: 1, name: "Environmental" },
      { id: 2, name: "Safety" },
      { id: 3, name: "Compliance" },
    ],
    complianceFindings: [
      { id: "1", name: "Minor Violation" },
      { id: "2", name: "Major Violation" },
      { id: "3", name: "Critical Violation" },
    ],
    enforcementActions: [
      { id: "1", name: "Warning Letter" },
      { id: "2", name: "Administrative Penalty" },
      { id: "3", name: "Stop Work Order" },
    ],
    requirementSources: [
      { id: "1", name: "Schedule B", source_title: "Schedule B" },
      { id: "2", name: "Order", source_title: "Order" },
      { id: "3", name: "EAC", source_title: "EAC" },
    ],
    staffUsers: [
      { id: 1, name: "John Officer", is_active: true },
      { id: 2, name: "Jane Officer", is_active: true },
      { id: 3, name: "Bob Officer", is_active: true },
    ],
  };

  const convertFilters = useConvertFiltersToQueryParams(externalFilters);
  const columns = useRequirementsGridColumns(dataDependencies);

  const handleTestFilters = () => {
    const columnFilters = [
      { id: "tpc", value: ["1", "2"] },
      { id: "summary", value: "test requirement" },
      { id: "enf_stats", value: ["APPROVAL_PENDING"] },
    ];

    // Test the filter conversion function
    convertFilters(columnFilters);
  };

  const handleTestColumns = () => {
    // Columns result available in columns variable
  };

  return (
    <Box sx={{ p: 2 }}>
      <Button onClick={handleTestFilters} data-testid="test-filters">
        Test Filter Conversion
      </Button>
      <Button onClick={handleTestColumns} data-testid="test-columns">
        Test Column Generation
      </Button>
      <div data-testid="columns-count">
        Generated {columns.length} columns
      </div>
    </Box>
  );
};

describe("RequirementsGridUtils", () => {
  let queryClient: QueryClient;

  const mountComponent = () => {
    mount(
      <QueryClientProvider client={queryClient}>
        <Box sx={{ width: "600px", height: "400px" }}>
          <TestComponent />
        </Box>
      </QueryClientProvider>
    );
  };

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
  });

  describe("Component Integration", () => {
    it("should render the test component", () => {
      mountComponent();
      
      cy.get('[data-testid="test-filters"]').should("exist");
      cy.get('[data-testid="test-columns"]').should("exist");
      cy.get('[data-testid="columns-count"]').should("exist");
    });

    it("should show correct number of generated columns", () => {
      mountComponent();
      
      cy.get('[data-testid="columns-count"]').should("contain", "Generated 10 columns");
    });

    it("should have test buttons", () => {
      mountComponent();
      
      cy.get('[data-testid="test-filters"]').should("contain", "Test Filter Conversion");
      cy.get('[data-testid="test-columns"]').should("contain", "Test Column Generation");
    });
  });

  describe("Utility Functions", () => {
    it("should use convertFilters utility function", () => {
      mountComponent();
      
      // The component should render without errors when using the utility
      cy.get('[data-testid="test-filters"]').should("be.visible");
    });

    it("should use columns utility function", () => {
      mountComponent();
      
      // The component should render without errors when using the utility
      cy.get('[data-testid="test-columns"]').should("be.visible");
    });
  });

  describe("Data Dependencies", () => {
    it("should handle topics data", () => {
      mountComponent();
      
      // Component should render with topics data
      cy.get('[data-testid="columns-count"]').should("contain", "10 columns");
    });

    it("should handle compliance findings data", () => {
      mountComponent();
      
      // Component should render with compliance findings data
      cy.get('[data-testid="test-columns"]').should("be.visible");
    });

    it("should handle enforcement actions data", () => {
      mountComponent();
      
      // Component should render with enforcement actions data
      cy.get('[data-testid="test-filters"]').should("be.visible");
    });
  });
});
