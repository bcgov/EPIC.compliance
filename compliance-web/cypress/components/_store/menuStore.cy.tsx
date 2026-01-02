/// <reference types="cypress" />
import { useMenuStore } from "@/store/menuStore";
import { mount } from "cypress/react";

const TestComponent = () => {
  const { openMenus, expandMenu, appHeaderHeight, toggleMenu, toggleExpandMenu, setAppHeaderHeight } = useMenuStore();

  return (
    <div>
      <button data-cy="toggle-menu" onClick={() => toggleMenu("test-route")}>
        Toggle Menu
      </button>
      <button data-cy="toggle-expand-menu" onClick={toggleExpandMenu}>
        Toggle Expand Menu
      </button>
      <button data-cy="set-header-height" onClick={() => setAppHeaderHeight(50)}>
        Set Header Height
      </button>
      <div data-cy="open-menus">{JSON.stringify(openMenus)}</div>
      <div data-cy="expand-menu">{expandMenu.toString()}</div>
      <div data-cy="header-height">{appHeaderHeight}</div>
    </div>
  );
};

describe("useMenuStore", () => {
  beforeEach(() => {
    mount(<TestComponent />);
  });

  it("should toggle the menu open state", () => {
    cy.get("[data-cy=open-menus]").should("contain", "{}");
    cy.get("[data-cy=toggle-menu]").click();
    cy.get("[data-cy=open-menus]").should("contain", '{"test-route":true}');
    cy.get("[data-cy=toggle-menu]").click();
    cy.get("[data-cy=open-menus]").should("contain", '{"test-route":false}');
  });

  it("should toggle the expand menu state", () => {
    cy.get("[data-cy=expand-menu]").should("contain", "true");
    cy.get("[data-cy=toggle-expand-menu]").click();
    cy.get("[data-cy=expand-menu]").should("contain", "false");
    cy.get("[data-cy=toggle-expand-menu]").click();
    cy.get("[data-cy=expand-menu]").should("contain", "true");
  });

  it("should set the app header height", () => {
    cy.get("[data-cy=header-height]").should("contain", "0");
    cy.get("[data-cy=set-header-height]").click();
    cy.get("[data-cy=header-height]").should("contain", "50");
  });
});
