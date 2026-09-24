/// <reference types="cypress" />
import { mount } from "cypress/react";
import StaffForm from "@/components/App/Staff/StaffForm"; // Adjust the path according to your project structure
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { FormProvider, useForm } from "react-hook-form";
import { StaffUser } from "@/models/Staff";
import { AuthUser } from "@/models/AuthUser";
import { Permission } from "@/models/Permission";
import { Position } from "@/models/Position";

// Mock data for Auth Users, Positions, Permissions, and Staff Users
const mockAuthUsers: AuthUser[] = [
  {
    id: "1",
    first_name: "John",
    last_name: "Doe",
    email_address: "",
    username: "jdoe@idir",
  },
  {
    id: "2",
    first_name: "Jane",
    last_name: "Smith",
    email_address: "",
    username: "jsmith@IDIR",
  },
  {
    id: "3",
    first_name: "John",
    last_name: "Doe",
    email_address: "",
    username: "jdoe@bceidbasic",
  },
  {
    id: "4",
    first_name: "Azure",
    last_name: "User",
    email_address: "",
    username: "auser@azureidir",
  },
  {
    id: "5",
    first_name: undefined as unknown as string,
    last_name: undefined as unknown as string,
    email_address: "",
    username: "nameless@idir",
  },
  {
    id: "6",
    first_name: "Alice",
    last_name: "Johnson",
    email_address: "",
    username: "ajohnson@idir",
  },
];

const mockPositions: Position[] = [
  { id: "1", name: "Manager" },
  { id: "2", name: "Developer" },
];

const mockPermissions: Permission[] = [
  { id: "1", name: "Admin" },
  { id: "2", name: "User" },
];

const mockStaffUsers: StaffUser[] = [
  {
    id: 1,
    name: "Alice Johnson",
    is_active: true,
    position_id: 3,
    auth_user_guid: "ajohnson@idir",
  },
  { id: 2, name: "Bob Brown", is_active: true, position_id: 2 },
];

describe("StaffForm Component", () => {
  const setup = (existingStaff = undefined) => {
    const queryClient = new QueryClient();

    // Create a wrapper component to provide react-hook-form context
    const Wrapper = ({ children }: { children: React.ReactNode }) => {
      const methods = useForm({
        defaultValues: {
          name: existingStaff ? `${existingStaff.full_name}` : "",
          position: null,
          deputyDirector: null,
          supervisor: null,
          permission: null,
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
        <StaffForm
          existingStaff={existingStaff}
          authUsersList={mockAuthUsers}
          positionsList={mockPositions}
          permissionsList={mockPermissions}
          staffUsersList={mockStaffUsers}
        />
      </Wrapper>
    );
  };

  beforeEach(() => {
    setup();
  });

  it("renders the form with all fields", () => {
    // Verify that all labels exist
    cy.contains("Name").should("exist");
    cy.contains("Position").should("exist");
    cy.contains("Deputy Director").should("exist");
    cy.contains("Supervisor").should("exist");
    cy.contains("Permission").should("exist");
  });

  it("allows selecting an auth user name", () => {
    cy.get('input[name="name"]').click();
    cy.get("li").contains("John Doe").click();
    cy.get('input[name="name"]').should("have.value", "John Doe");
  });

  it("lists only named IDIR users not already on staff", () => {
    cy.get('input[name="name"]').click();
    cy.get('[role="option"]').should("have.length", 2);
    cy.get('[role="option"]').contains("John Doe").should("exist");
    cy.get('[role="option"]').contains("Jane Smith").should("exist");
    cy.get('[role="option"]').contains("Azure User").should("not.exist");
    cy.get('[role="option"]').contains("undefined").should("not.exist");
    cy.get('[role="option"]').contains("Alice Johnson").should("not.exist");
  });

  it("searches and selects an IDIR user", () => {
    cy.get('input[name="name"]').type("Jane");
    cy.get('[role="option"]').should("have.length", 1).contains("Jane Smith").click();
    cy.get('input[name="name"]').should("have.value", "Jane Smith");
  });

  it("disables the 'Name' field if existingStaff is provided", () => {
    setup({ id: 3, full_name: "Existing Staff User" });
    cy.get('input[name="name"]').should("be.disabled");
  });

  it("allows selecting a position", () => {
    cy.get('input[name="position"]').click();
    cy.get("li").contains("Manager").click();
    cy.get('input[name="position"]').should("have.value", "Manager");
  });

  it("allows selecting a deputy director", () => {
    cy.get('input[name="deputyDirector"]').click();
    cy.get("li").contains("Alice Johnson").click();
    cy.get('input[name="deputyDirector"]').should(
      "have.value",
      "Alice Johnson"
    );
  });

  it("allows selecting a supervisor", () => {
    cy.get('input[name="supervisor"]').click();
    cy.get("li").contains("Bob Brown").click();
    cy.get('input[name="supervisor"]').should("have.value", "Bob Brown");
  });

  it("allows selecting a permission", () => {
    cy.get('input[name="permission"]').click();
    cy.get("li").contains("Admin").click();
    cy.get('input[name="permission"]').should("have.value", "Admin");
  });
});
