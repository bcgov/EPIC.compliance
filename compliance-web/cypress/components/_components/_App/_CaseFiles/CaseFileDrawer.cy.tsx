import React from "react";
import { mount } from "cypress/react";
import CaseFileDrawer from "@/components/App/CaseFiles/CaseFileDrawer";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { CaseFile } from "@/models/CaseFile";
import { Project } from "@/models/Project";
import { Initiation } from "@/models/Initiation";
import { StaffUser } from "@/models/Staff";
import { AuthProvider } from "react-oidc-context";
import { OidcConfig } from "@/utils/config";

describe("CaseFileDrawer Component", () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  // Mock data
  const mockProjects: Project[] = [
    { id: 1, name: "Project 1", is_active: true },
    { id: 2, name: "Project 2", is_active: true },
    { id: 3, name: "Project 3", is_active: true },
    { id: 9999, name: "Unapproved Project", is_active: true },
  ];

  const mockInitiations: Initiation[] = [
    { id: "1", name: "Initiation 1" },
    { id: "2", name: "Initiation 2" },
  ];

  const mockStaffUsers: StaffUser[] = [
    { id: 1, name: "User 1", is_active: true },
    { id: 2, name: "User 2", is_active: true },
    { id: 3, name: "User 3", is_active: true },
  ];

  const mockCaseFile: CaseFile = {
    id: 1,
    case_file_number: "CF-2023-001",
    project_id: 1,
    date_created: "2023-01-01",
    primary_officer_id: 1,
    case_file_status: "OPEN",
    is_active: true,
    project: mockProjects[0],
    primary_officer: mockStaffUsers[0],
    initiation: mockInitiations[0],
    officers: [mockStaffUsers[1]],
    authorization: "AUTH-123",
    regulated_party: "Regulated Party Inc.",
    project_description: "Test project description",
    type: "Type A",
    sub_type: "Sub Type B",
  };

  beforeEach(() => {
    // Mock API responses using fetch
    cy.stub(window, "fetch").callsFake((url) => {
      if (url.toString().includes("/api/projects")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockProjects),
        });
      } else if (url.toString().includes("/api/initiations")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockInitiations),
        });
      } else if (url.toString().includes("/api/staff")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockStaffUsers),
        });
      }
      return Promise.reject(new Error(`Unhandled fetch request: ${url}`));
    });

    // Reset the query client before each test
    queryClient.clear();

    // Set the query data directly to ensure it's available
    queryClient.setQueryData(["projects", { includeUnapproved: true }], mockProjects);
    queryClient.setQueryData(["initiations"], mockInitiations);
    queryClient.setQueryData(["staff-users", true], mockStaffUsers);

  });

  function mountComponent(isEditMode = false) {
    const onSubmitSpy = cy.spy().as("onSubmitSpy");

    return mount(
      <QueryClientProvider client={queryClient}>
        <AuthProvider {...OidcConfig}>
          <CaseFileDrawer
            onSubmit={onSubmitSpy}
            caseFile={isEditMode ? mockCaseFile : undefined}
          />
        </AuthProvider>
      </QueryClientProvider>
    );
  }

  it("renders in create mode correctly", () => {
    mountComponent();

    // Check title
    cy.contains("Create Case File").should("be.visible");

    // Check form fields are present
    cy.get('input[name="project"]').should("be.visible");
    cy.get('input[name="initiation"]').should("be.visible");
    cy.get('input[name="primaryOfficer"]').should("be.visible");

    // Check submit button
    cy.contains("button", "Create").should("be.visible");
  });

  it("renders in edit mode correctly", () => {
    mountComponent(true);

    // Check title shows case file number
    cy.contains("CF-2023-001").should("be.visible");

    // Check form fields are populated with case file data
    cy.get('input[name="project"]').should("have.value", "Project 1");
    cy.get('input[name="initiation"]').should("have.value", "Initiation 1");
    cy.get('input[name="primaryOfficer"]').should("have.value", "User 1");

    // Check submit button
    cy.contains("button", "Save").should("be.visible");
  });
});
