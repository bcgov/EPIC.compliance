// cypress/components/TopicModal.cy.tsx
import { mount } from "cypress/react";
import TopicModal from "@/components/App/Topics/TopicModal"; // Adjust the path as necessary
import { Topic } from "@/models/Topic";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

describe("<TopicModal />", () => {
  let mockOnSubmit: Cypress.Agent<sinon.SinonStub>;

  beforeEach(() => {
    // Initialize the stub before each test
    mockOnSubmit = cy.stub().as("onSubmit");
  });

  const mockTopic: Topic = {
    id: 1,
    name: "Existing Topic",
  };

  const queryClient = new QueryClient(); // Create a QueryClient instance

  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it("renders the modal for adding a new topic", () => {
    mount(
      <Wrapper>
        <TopicModal onSubmit={mockOnSubmit} />
      </Wrapper>
    );
    cy.contains("Add Topic").should("be.visible");
    cy.get("input[name='name']").should("exist");
    cy.get("button").contains("Add").should("be.visible");
  });

  it("renders the modal for updating an existing topic", () => {
    mount(
      <Wrapper>
        <TopicModal onSubmit={mockOnSubmit} topic={mockTopic} />
      </Wrapper>
    );
    cy.contains(mockTopic.name).should("be.visible");
    cy.get("input[name='name']").should("have.value", mockTopic.name);
    cy.get("button").contains("Save").should("be.visible");
  });

  it("validates the form and shows an error message for required fields", () => {
    mount(
      <Wrapper>
        <TopicModal onSubmit={mockOnSubmit} />
      </Wrapper>
    );
    cy.get("button").contains("Add").click();
    cy.contains("Name is required").should("be.visible");
  });

  it("validates the max length of the topic name", () => {
    mount(
      <Wrapper>
        <TopicModal onSubmit={mockOnSubmit} />
      </Wrapper>
    );
    cy.get("input[name='name']").type("a".repeat(101));
    cy.get("button").contains("Add").click();
    cy.contains("Max length exceeded").should("be.visible");
  });
});
