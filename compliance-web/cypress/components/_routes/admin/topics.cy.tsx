import { mount } from "cypress/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Topics } from "@/routes/_authenticated/admin/topics";
import ModalProvider from "@/components/Shared/Modals/ModalProvider";
import SnackBarProvider from "@/components/Shared/Popups/SnackBarProvider";
import router from "@/router/router";
import { AuthProvider } from "react-oidc-context";
import { OidcConfig } from "@/utils/config";

describe("Topics Component", () => {
  const queryClient = new QueryClient();

  function mountTopic(): React.ReactNode {
    return (
      <QueryClientProvider client={queryClient}>
        <AuthProvider {...OidcConfig}>
          <ModalProvider />
          <SnackBarProvider />
          <Topics />
        </AuthProvider>
      </QueryClientProvider>
    );
  }

  it("should render topics page correctly", () => {
    router.navigate({ to: "/admin/topics" });

    mount(mountTopic());

    cy.contains("h5", "Topics").should("be.visible");
    cy.get("button").should("contain.text", "Topic");
  });

  it("should render topics table correctly", () => {
    router.navigate({ to: "/admin/topics" });

    mount(mountTopic());

    cy.get("table").should("be.visible");
    cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Name");
  });

  it("should open the Topic modal when the add button is clicked", () => {
    router.navigate({ to: "/admin/topics" });

    mount(mountTopic());

    cy.get("button").contains("Topic").click();
    cy.contains("h5", "Add Topic").should("be.visible");

    cy.get('input[name="name"]').should("be.visible");
  });
});
