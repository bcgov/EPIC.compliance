/// <reference types="cypress" />
import { useDrawer } from "@/store/drawerStore";
import { Box } from "@mui/material";
import { mount } from "cypress/react";
import { act } from "react";

const TestComponent = () => {
  const { isOpen, drawerContent, setOpen, setClose } = useDrawer();

  return (
    <div>
      <div data-cy="drawer-status">{isOpen ? "Open" : "Closed"}</div>
      <div data-cy="drawer-content">{drawerContent}</div>
      <button
        data-cy="open-drawer"
        onClick={() =>
          setOpen({
            content: <Box data-cy="test-drawer-content">Test Drawer Content</Box>,
          })
        }
      >
        Open Drawer
      </button>
      <button data-cy="close-drawer" onClick={setClose}>
        Close Drawer
      </button>
    </div>
  );
};

describe("useDrawer Store", () => {
  beforeEach(() => {
    mount(<TestComponent />);
  });

  it("should initialize with drawer closed and no content", () => {
    cy.get('[data-cy="drawer-status"]').should("contain", "Closed");
    cy.get('[data-cy="drawer-content"]').should("be.empty");
  });

  it("should open the drawer and display content when setOpen is called", () => {
    cy.get('[data-cy="open-drawer"]').click();

    cy.get('[data-cy="drawer-status"]').should("contain", "Open");
    cy.get('[data-cy="test-drawer-content"]').should(
      "contain",
      "Test Drawer Content"
    );
  });

  it("should close the drawer and clear content when setClose is called", () => {
    cy.get('[data-cy="open-drawer"]').click();
    cy.get('[data-cy="close-drawer"]').click();

    cy.get('[data-cy="drawer-status"]').should("contain", "Closed");
  });

  it("should not open the drawer if no content is provided", () => {
    act(() => {
      useDrawer.getState().setOpen({ content: null });
    });

    cy.get('[data-cy="drawer-status"]').should("contain", "Closed");
  });
});
