import { mount } from "cypress/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Agencies } from "@/routes/_authenticated/admin/agencies";
import ModalProvider from "@/components/Shared/Modals/ModalProvider";
import SnackBarProvider from "@/components/Shared/Popups/SnackBarProvider";
import router from "@/router/router";
import { AuthProvider } from "react-oidc-context";
import { OidcConfig } from "@/utils/config";

describe("Agencies Component", () => {
  const queryClient = new QueryClient();

  function mountAgency(): React.ReactNode {
    return (
      <QueryClientProvider client={queryClient}>
        <AuthProvider {...OidcConfig}>
          <ModalProvider />
          <SnackBarProvider />
          <Agencies />
        </AuthProvider>
      </QueryClientProvider>
    );
  }

  it("should render agencies page correctly", () => {
    router.navigate({ to: "/admin/agencies" });

    mount(mountAgency());

    cy.contains("h5", "Agencies").should("be.visible");
    cy.get("button").should("contain.text", "Agency");
  });

  it("should render agencies table correctly", () => {
    router.navigate({ to: "/admin/agencies" });

    mount(mountAgency());

    cy.get("table").should("be.visible");
    cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Name");
    cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Abbreviation");
  });

  it("should open the Agency modal when the add button is clicked", () => {
    router.navigate({ to: "/admin/agencies" });

    mount(mountAgency());

    cy.get("button").contains("Agency").click();
    cy.contains("h5", "Add Agency").should("be.visible");

    cy.get('input[name="name"]').should("be.visible");
  });
});
