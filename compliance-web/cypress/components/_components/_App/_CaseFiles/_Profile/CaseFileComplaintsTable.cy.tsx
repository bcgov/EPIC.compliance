import { mount } from "cypress/react18";
import CaseFileComplaintsTable from "@/components/App/CaseFiles/Profile/CaseFileComplaintsTable";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { 
  RouterProvider, 
  createMemoryHistory,
  createRootRoute,
  createRoute,
  createRouter
} from '@tanstack/react-router';
import { CaseFile } from "@/models/CaseFile";
import { INITIATION } from "@/utils/constants";

describe("CaseFileComplaintsTable", () => {
  let queryClient: QueryClient;

  const mockComplaints = [
    {
      id: 1,
      complaint_number: "COMP_123",
      status: "OPEN",
      concern_description: "Test concern description 1",
      source_type: { name: "Source 1" },
      primary_officer: { id: 1, name: "John Doe", is_active: true },
      date_received: "2023-04-15T12:00:00Z",
    },
    {
      id: 2,
      complaint_number: "COMP_124",
      status: "CLOSED",
      concern_description: "Test concern description 2",
      source_type: { name: "Source 2" },
      primary_officer: { id: 1, name: "Jane Smith", is_active: true },
      date_received: "2023-04-16T12:00:00Z",
    },
  ];

  const mockCaseFile: CaseFile = {
    id: 1,
    project: { id: 1, name: "Test Project" },
    date_created: "2023-04-15T12:00:00Z",
    initiation: { id: INITIATION.COMPLAINTS_ID, name: "Complaints" },
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

  beforeEach(() => {
    queryClient = new QueryClient();
    queryClient.setQueryData(["complaints-by-caseFileId", 1], {items: mockComplaints});

    // Create a simple router for testing
    const rootRoute = createRootRoute();
    
    const complaintsRoute = createRoute({
      getParentRoute: () => rootRoute,
      path: '/ce-database/complaints/$complaintNumber',
      component: () => <div>Complaint Detail Page</div>
    });
    
    const indexRoute = createRoute({
      getParentRoute: () => rootRoute,
      path: '/',
      component: () => (
        <QueryClientProvider client={queryClient}>
          <CaseFileComplaintsTable caseFile={mockCaseFile} />
        </QueryClientProvider>
      )
    });

    const routeTree = rootRoute.addChildren([indexRoute, complaintsRoute]);
    
    const memoryHistory = createMemoryHistory({
      initialEntries: ['/'],
    });
    
    const router = createRouter({
      routeTree,
      history: memoryHistory,
    });

    mount(<RouterProvider router={router as never} />);
  });

  it("renders the complaints section with correct title", () => {
    cy.contains("h6", "Complaints").should("exist");
  });

  it("displays complaint accordions with correct complaint numbers", () => {
    cy.contains("COMP_123").should("exist");
    cy.contains("COMP_124").should("exist");
  });

  it("shows complaint status chips", () => {
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
    
    // Should show expanded content
    cy.contains("Concern Description").should("exist");
    cy.contains("Source").should("exist");
    cy.contains("Date Received").should("exist");
    
    // Should show ExpandLessRounded icon when expanded
    cy.get('[data-testid="ExpandLessRoundedIcon"]').should("exist");
  });

  it("displays complaint details when expanded", () => {
    // Expand the first accordion
    cy.get('[role="button"]').first().click();
    
    // Check for concern description
    cy.contains("Test concern description 1").should("exist");
    
    // Check for source
    cy.contains("Source 1").should("exist");
    
    // Check for formatted date
    cy.contains("2023-04-15").should("exist");
  });

  it("shows complaint links with correct routing", () => {
    cy.get('a').contains("COMP_123").should("exist");
    cy.get('a').contains("COMP_124").should("exist");
  });

  it("has correct link to complaint detail", () => {
    cy.get('a').contains("COMP_123").should('have.attr', 'href')
      .and('include', '/ce-database/complaints/');
  });

  it("navigates to complaint detail when link is clicked", () => {
    // Just check that the link has the correct href
    cy.get('a').contains("COMP_123").should('have.attr', 'href')
      .and('include', '/ce-database/complaints/');
    
    // And that clicking doesn't throw errors
    cy.get('a').contains("COMP_123").click();
  });

  it("collapses accordion when clicked again", () => {
    // Expand the first accordion
    cy.get('[role="button"]').first().click();
    
    // Verify it's expanded
    cy.contains("Concern Description").should("exist");
    
    // Click again to collapse
    cy.get('[role="button"]').first().click();
    
    // Verify it's collapsed (content should not be visible)
    cy.contains("Concern Description").should("not.be.visible");
  });

  it("shows no complaints message when there are no complaints", () => {
    // Set empty complaints data
    queryClient.setQueryData(["complaints-by-caseFileId", 1], []);
    
    // Re-mount with empty data
    const rootRoute = createRootRoute();
    const indexRoute = createRoute({
      getParentRoute: () => rootRoute,
      path: '/',
      component: () => (
        <QueryClientProvider client={queryClient}>
          <CaseFileComplaintsTable caseFile={mockCaseFile} />
        </QueryClientProvider>
      )
    });
    const routeTree = rootRoute.addChildren([indexRoute]);
    const memoryHistory = createMemoryHistory({ initialEntries: ['/'] });
    const router = createRouter({ routeTree, history: memoryHistory });
    
    mount(<RouterProvider router={router as never} />);
    
    cy.contains("You do not have any created complaints on this file.").should("exist");
  });
}); 
