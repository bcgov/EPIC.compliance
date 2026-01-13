import { mount } from "cypress/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Staff } from "@/routes/_authenticated/admin/staff";
import router from "@/router/router";
import ModalProvider from "@/components/Shared/Modals/ModalProvider";

describe("Staff Component", () => {
  const queryClient = new QueryClient();

  function mountStaff(): React.ReactNode {
    return (
      <QueryClientProvider client={queryClient}>
        <ModalProvider />
        <Staff />
      </QueryClientProvider>
    );
  }

  it("should render staff page correctly", () => {
    router.navigate({ to: "/admin/staff" });

    mount(mountStaff());

    cy.contains("h5", "Staff").should("be.visible");
    cy.get("button").should("contain.text", "Staff Member");
  });

  it("should render staff table correctly", () => {
    router.navigate({ to: "/admin/staff" });

    mount(mountStaff());

    cy.get("table").should("be.visible");
    cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Name");
    cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Position");
    cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Supervisor");
    cy.get(".Mui-TableHeadCell-Content").should(
      "contain.text",
      "Deputy Director"
    );
    cy.get(".Mui-TableHeadCell-Content").should(
      "contain.text",
      "Permission Level"
    );
  });

  it("should open the Staff modal when the add button is clicked", () => {
    router.navigate({ to: "/admin/staff" });

    mount(mountStaff());

    cy.get("button").contains("Staff Member").click();
    cy.contains("h5", "Add Staff Member").should("be.visible");

    cy.get('input[name="name"]').should("be.visible");
  });
});
