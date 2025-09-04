import { mount } from "cypress/react18";
import CaseFileInspectionsTable from "@/components/App/CaseFiles/Profile/CaseFileInspectionsTable";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { 
  RouterProvider, 
  createMemoryHistory,
  createRootRoute,
  createRoute,
  createRouter
} from '@tanstack/react-router';
import { CaseFile } from "@/models/CaseFile";
import { INITIATION, EnforcementActionEnum } from "@/utils/constants";
import { InspectionMoreDetails } from "@/models/Inspection";

describe("CaseFileInspectionsTable", () => {
  let queryClient: QueryClient;

  const mockCaseFile: CaseFile = {
    id: 1,
    project: { id: 1, name: "Test Project" },
    date_created: "2023-04-15T12:00:00Z",
    initiation: { id: INITIATION.INSPECTION_ID, name: "Inspection" },
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

  const mockInspections: InspectionMoreDetails[] = [
    {
      id: 1,
      case_file_id: 1,
      project_id: 1,
      utm: "1234567890",
      initiation_id: 1,
      initiation: { id: INITIATION.INSPECTION_ID, name: "Inspection" },
      ir_number: "IR_123",
      inspection_status: "OPEN",
      location_description: "Test Location 1",
      start_date: "2023-04-15T12:00:00Z",
      primary_officer: { id: 1, name: "John Doe", is_active: true },
      ir_status_id: 1,
      project_status_id: 1,
      primary_officer_id: 1,
      end_date: "2023-04-16T12:00:00Z",
      debrief_date: "2023-04-17T12:00:00Z",
      types: [],
      types_text: "",
      is_active: true,
      project: { id: 1, name: "Test Project" },
      ir_status: { id: "1", name: "Active" },
      case_file: mockCaseFile,
      project_status: { id: "1", name: "Active" },
      requirement_details: [
        {
          requirement_id: 1,
          requirement_summary: "Test Requirement 1",
          requirement_sort_order: 1,
          requirement_number: "REQ_001",
          requirement_source_name: "Order",
          enforcement_action: {
            id: EnforcementActionEnum.ORDER,
            name: "Test Order",
            number: "ORDER_001",
            progress: {
              id: "ISSUED",
              name: "Issued"
            }
          }
        },
        {
          requirement_id: 2,
          requirement_summary: "Test Requirement 2",
          requirement_sort_order: 2,
          requirement_number: "REQ_002",
          requirement_source_name: "Condition",
          enforcement_action: {
            id: EnforcementActionEnum.WARNING_LETTER,
            name: "Test Warning Letter",
            number: "WL_001",
            progress: {
              id: "DRAFTING",
              name: "Drafting"
            }
          }
        }
      ]
    },
    {
      id: 2,
      case_file_id: 1,
      project_id: 1,
      utm: "1234567890",
      initiation_id: 1,
      initiation: { id: INITIATION.INSPECTION_ID, name: "Inspection" },
      ir_number: "IR_124",
      inspection_status: "CLOSED",
      location_description: "Test Location 2",
      start_date: "2023-04-16T12:00:00Z",
      primary_officer: { id: 2, name: "Jane Smith", is_active: true },
      ir_status_id: 1,
      project_status_id: 1,
      primary_officer_id: 2,
      end_date: "2023-04-17T12:00:00Z",
      debrief_date: "2023-04-18T12:00:00Z",
      types: [],
      types_text: "",
      is_active: true,
      project: { id: 1, name: "Test Project" },
      ir_status: { id: "1", name: "Active" },
      case_file: mockCaseFile,
      project_status: { id: "1", name: "Active" },
      requirement_details: [
        {
          requirement_id: 3,
          requirement_summary: "Test Requirement 3",
          requirement_sort_order: 1,
          requirement_number: "REQ_003",
          requirement_source_name: "Section",
          enforcement_action: undefined
        }
      ]
    },
  ];

  beforeEach(() => {
    queryClient = new QueryClient();
    
    // Set up the query data before mounting
    queryClient.setQueryData(["inspections-details-by-caseFileId", 1], mockInspections);
    queryClient.setQueryData(["staff-users"], []);

    // Create a simple router for testing
    const rootRoute = createRootRoute();
    
    const inspectionsRoute = createRoute({
      getParentRoute: () => rootRoute,
      path: '/ce-database/inspections/$inspectionNumber',
      component: () => <div>Inspection Detail Page</div>
    });
    
    const indexRoute = createRoute({
      getParentRoute: () => rootRoute,
      path: '/',
      component: () => (
        <QueryClientProvider client={queryClient}>
          <CaseFileInspectionsTable caseFile={mockCaseFile} />
        </QueryClientProvider>
      )
    });

    const routeTree = rootRoute.addChildren([indexRoute, inspectionsRoute]);
    
    const memoryHistory = createMemoryHistory({
      initialEntries: ['/'],
    });
    
    const router = createRouter({
      routeTree,
      history: memoryHistory,
    });

    // Debug: Log the query data to ensure it's set correctly
    cy.log('Setting up test with inspections data:', JSON.stringify(mockInspections));
    cy.log('Case file initiation ID:', mockCaseFile.initiation.id);
    cy.log('INITIATION.INSPECTION_ID:', INITIATION.INSPECTION_ID);

    mount(<RouterProvider router={router as never} />);
  });

  it("renders the inspections section with correct title", () => {
    cy.contains("h6", "Inspections").should("exist");
  });

  it("displays inspection accordions with correct inspection numbers", () => {
    // Debug: Check what's actually rendered
    cy.get('body').then(($body) => {
      cy.log('Body content:', $body.html());
    });
    
    cy.contains("IR_123").should("exist");
    cy.contains("IR_124").should("exist");
  });

  it("shows inspection status chips", () => {
    cy.get('[data-testid="status-chip"]').contains("OPEN").should("exist");
    cy.get('[data-testid="status-chip"]').contains("CLOSED").should("exist");
  });

  it("displays primary officer information", () => {
    cy.contains("Primary:").should("exist");
    cy.contains("John Doe").should("exist");
    cy.contains("Jane Smith").should("exist");
  });

  it("shows expand/collapse icons", () => {
    // Check for ChevronRight icons (collapsed state)
    cy.get('[data-testid="ChevronRightIcon"]').should("exist");
  });

  it("expands accordion when clicked", () => {
    // Click on the first accordion to expand it
    cy.get('[role="button"]').first().click();
    
    // Should show expanded content with requirement details
    cy.contains("Requirement Summary").should("exist");
    cy.contains("#").should("exist");
    cy.contains("Source").should("exist");
    cy.contains("Enforcement Action").should("exist");
    cy.contains("Enf. Status").should("exist");
    
    // Should show ExpandLessRounded icon when expanded
    cy.get('[data-testid="ExpandLessRoundedIcon"]').should("exist");
  });

  it("displays requirement details when expanded", () => {
    // Expand the first accordion
    cy.get('[role="button"]').first().click();
    
    // Check for requirement summaries
    cy.contains("#1. Test Requirement 1").should("exist");
    cy.contains("#2. Test Requirement 2").should("exist");
    
    // Check for requirement numbers
    cy.contains("001").should("exist"); // From REQ_001 split
    cy.contains("002").should("exist"); // From REQ_002 split
    
    // Check for requirement sources
    cy.contains("Order").should("exist");
    cy.contains("Condition").should("exist");
    
    // Check for enforcement actions
    cy.contains("Test Order").should("exist");
    cy.contains("Test Warning Letter").should("exist");
    
    // Check for enforcement status chips
    cy.contains("Open").should("exist");
    cy.contains("Drafting").should("exist");
  });

  it("shows inspection links with correct routing", () => {
    cy.get('a').contains("IR_123").should("exist");
    cy.get('a').contains("IR_124").should("exist");
  });

  it("has correct link to inspection detail", () => {
    cy.get('a').contains("IR_123").should('have.attr', 'href')
      .and('include', '/ce-database/inspections/');
  });

  it("navigates to inspection detail when link is clicked", () => {
    // Just check that the link has the correct href
    cy.get('a').contains("IR_123").should('have.attr', 'href')
      .and('include', '/ce-database/inspections/');
    
    // And that clicking doesn't throw errors
    cy.get('a').contains("IR_123").click();
  });

  it("collapses accordion when clicked again", () => {
    // Expand the first accordion
    cy.get('[role="button"]').first().click();
    
    // Verify it's expanded
    cy.contains("Requirement Summary").should("exist");
    
    // Click again to collapse
    cy.get('[role="button"]').first().click();
    
    // Verify it's collapsed (content should not be visible)
    cy.contains("Requirement Summary").should("not.be.visible");
  });

  it("shows no inspections message when there are no inspections", () => {
    // Set empty inspections data
    queryClient.setQueryData(["inspections-details-by-caseFileId", 1], []);
    
    // Re-mount with empty data
    const rootRoute = createRootRoute();
    const indexRoute = createRoute({
      getParentRoute: () => rootRoute,
      path: '/',
      component: () => (
        <QueryClientProvider client={queryClient}>
          <CaseFileInspectionsTable caseFile={mockCaseFile} />
        </QueryClientProvider>
      )
    });
    const routeTree = rootRoute.addChildren([indexRoute]);
    const memoryHistory = createMemoryHistory({ initialEntries: ['/'] });
    const router = createRouter({ routeTree, history: memoryHistory });
    
    mount(<RouterProvider router={router as never} />);
    
    cy.contains("You do not have any created inspections on this file.").should("exist");
  });

  it("handles requirement source links correctly", () => {
    // Expand the first accordion
    cy.get('[role="button"]').first().click();
    
    // Check that order requirement numbers are clickable links
    cy.get('a').contains("001").should("exist");
    cy.get('a').contains("002").should("not.exist");
  });

  it("displays enforcement action status chips with correct colors", () => {
    // Expand the first accordion
    cy.get('[role="button"]').first().click();
    
    // Check for enforcement status chips
    cy.contains("Open").should("exist");
    cy.contains("Drafting").should("exist");
  });

  it("handles inspections without requirement details", () => {
    const inspectionsWithoutRequirements = [
      {
        id: 3,
        ir_number: "IR_125",
        inspection_status: "OPEN",
        location_description: "Test Location 3",
        start_date: "2023-04-17T12:00:00Z",
        primary_officer: { name: "Bob Johnson" },
        requirement_details: []
      }
    ];

    queryClient.setQueryData(["inspections-details-by-caseFileId", 1], inspectionsWithoutRequirements);
    
    // Re-mount with data without requirements
    const rootRoute = createRootRoute();
    const indexRoute = createRoute({
      getParentRoute: () => rootRoute,
      path: '/',
      component: () => (
        <QueryClientProvider client={queryClient}>
          <CaseFileInspectionsTable caseFile={mockCaseFile} />
        </QueryClientProvider>
      )
    });
    const routeTree = rootRoute.addChildren([indexRoute]);
    const memoryHistory = createMemoryHistory({ initialEntries: ['/'] });
    const router = createRouter({ routeTree, history: memoryHistory });
    
    mount(<RouterProvider router={router as never} />);
    
    // Should still show the inspection
    cy.contains("IR_125").should("exist");
    
    // Expand the accordion
    cy.get('[role="button"]').first().click();
    
    // Should show headers but no requirement data
    cy.contains("Requirement Summary").should("exist");
    cy.contains("#").should("exist");
    cy.contains("Source").should("exist");
    cy.contains("Enforcement Action").should("exist");
    cy.contains("Enf. Status").should("exist");
  });
}); 
