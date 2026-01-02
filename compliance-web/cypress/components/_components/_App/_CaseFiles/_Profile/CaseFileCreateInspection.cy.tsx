import { mount } from "cypress/react";
import CaseFileCreateInspection from "@/components/App/CaseFiles/Profile/CaseFileCreateInspection";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

describe("CaseFileCreateInspection", () => {
  let queryClient: QueryClient;

  const mockCaseFile = {
    id: 1,
    case_file_number: "CF-123",
    project: { id: 1, name: "Test Project" },
    // ... other required properties
  };

  beforeEach(() => {
    queryClient = new QueryClient();
    queryClient.setQueryData(["case-file", "CF-123"], mockCaseFile);
  });

  const mountComponent = (disabled = false) => {
    mount(
      <QueryClientProvider client={queryClient}>
        <CaseFileCreateInspection fileNumber="CF-123" hidden={disabled} />
      </QueryClientProvider>
    );
  };

  it("renders create inspection button", () => {
    mountComponent();
    cy.contains("button", "Inspection").should("exist");
    cy.get('button').find('svg').should("exist"); // Check for icon
  });

  it("hides button when hidden prop is true", () => {
    mountComponent(true);
    cy.contains("button", "Inspection").should("not.exist");
  });

  it("shows button when hidden prop is false", () => {
    mountComponent(false);
    cy.contains("button", "Inspection").should("exist");
  });
});
