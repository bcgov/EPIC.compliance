/// <reference types="cypress" />
import { mount } from "cypress/react";
import ProjectDetailsForm from "@/components/App/ProjectDetailsForm"; // Adjust path accordingly
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { FormProvider, useForm } from "react-hook-form";
import { UNAPPROVED_PROJECT_ID } from "@/utils/constants";

const projectList = [
  { id: 1, name: "Project Alpha" },
  { id: 2, name: "Project Beta" },
  { id: UNAPPROVED_PROJECT_ID, name: "Unapproved Project" },
];

const mockProjectData = {
  id: 1,
  name: "Project Alpha",
  ea_certificate: "12345",
  proponent: { name: "Proponent Name" },
  description: "Description of Project Alpha",
  type: { name: "Type A" },
  sub_type: { name: "Subtype A" },
};

describe("ProjectDetailsForm Component", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    // Initialize QueryClient with mock data
    queryClient = new QueryClient();

    // Set up mock data in the cache for the project query
    queryClient.setQueryData(["projects", mockProjectData.id], mockProjectData);

    const Wrapper = ({ children }: { children: React.ReactNode }) => {
      const methods = useForm({
        defaultValues: {
          project: null,
          authorization: "",
          regulatedParty: "",
          projectDescription: "",
          projectType: "",
          projectSubType: "",
        },
      });

      return (
        <QueryClientProvider client={queryClient}>
          <FormProvider {...methods}>{children}</FormProvider>
        </QueryClientProvider>
      );
    };

    mount(
      <Wrapper>
        <ProjectDetailsForm projectList={projectList} />
      </Wrapper>
    );
  });

  it("renders the component correctly", () => {
    cy.contains("Project").should("exist");
    cy.contains("Authorization").should("exist");
    cy.contains("Regulated Party").should("exist");
    cy.contains("Project Type").should("exist");
    cy.contains("Project Subtype").should("exist");
  });

  it("allows selecting a project from the project list", () => {
    cy.get('input[name="project"]').click();
    cy.get("li").contains("Project Alpha").click();
    cy.get('input[name="project"]').should("have.value", "Project Alpha");

    // Verify fields are updated based on the project data
    cy.get('input[name="authorization"]').should("have.value", "EAC# 12345");
    cy.get('input[name="regulatedParty"]').should("have.value", "Proponent Name");
    cy.get('input[name="projectType"]').should("have.value", "Type A");
    cy.get('input[name="projectSubType"]').should("have.value", "Subtype A");
  });

  it("disables fields correctly when a project is selected", () => {
    // Select a project
    cy.get('input[name="project"]').click();
    cy.get("li").contains("Project Alpha").click();

    // Verify fields are disabled
    cy.get('input[name="authorization"]').should("be.disabled");
    cy.get('input[name="regulatedParty"]').should("be.disabled");
    cy.get('input[name="projectType"]').should("be.disabled");
    cy.get('input[name="projectSubType"]').should("be.disabled");
  });

  it("enables fields when 'Unapproved Project' is selected", () => {
    // Select the "Unapproved Project" option
    cy.get('input[name="project"]').click();
    cy.get("li").contains("Unapproved Project").click();

    // Verify fields are enabled
    cy.get('input[name="authorization"]').should("not.be.disabled");
    cy.get('input[name="regulatedParty"]').should("not.be.disabled");
    cy.get('input[name="projectType"]').should("not.be.disabled");
    cy.get('input[name="projectSubType"]').should("not.be.disabled");
  });
});
